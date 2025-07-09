import streamlit as st
import json
import config as cfg
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
from urllib.parse import unquote
import re

load_dotenv(find_dotenv())


def doc_embedding(
    llm_response: str,
    citations: list[dict],
) -> tuple[str, list[str]]:
    docs = []
    # Encuentra las citations
    pattern = r"(\[doc\d+\])"
    matches = re.findall(pattern, llm_response)
    if matches:
        for match in matches:
            num_pattern = r".*(\d+)"
            doc_num = int(re.match(num_pattern, match).group(1)) - 1
            citation = unquote(citations[doc_num]["filepath"])
            llm_response = llm_response.replace(match, "")
            # Solo dejamos path sin base_url
            docs.append(citation.split("/", maxsplit=4)[4])
            full_response = (
                llm_response
                + "\n\nFuentes:"
                + "\n- "
                + "\n- ".join(doc for doc in docs)
            )
        return full_response
    return llm_response


def llm(
    session_messages: list[dict[str, str]],
    past_messages: int = 10,
    test_mode=False,
):
    deployment = "gpt-4.1-nano"
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint=azure_endpoint,
    )

    with open(cfg.PROJ_ROOT / "model_instructions.md", "r", encoding="utf-8") as file:
        model_instructions = file.read()

    if test_mode:
        with open(cfg.PROJ_ROOT / "example_response.json", encoding="utf-8") as f:
            completion = json.load(f)

    else:
        messages = [{"role": "system", "content": model_instructions}]
        messages.extend(session_messages[:past_messages])

        completion = client.chat.completions.create(
            model=deployment,
            temperature=0.0,
            top_p=1,
            seed=43,
            stream=False,
            messages=messages,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"],
                            "index_name": os.environ["AZURE_SEARCH_INDEX_NAME"],
                            # "query_type": "semantic",  # NOTE: no funciona en free tier. Activar en el real
                            # "top_n_documents": 5,  # NOTE: Esto puede modificarse si el usuario hace preguntas que requieren mas contexto
                            "authentication": {
                                "type": "api_key",
                                "key": os.environ["AZURE_SEARCH_API_KEY"],
                            },
                            "fields_mapping": {
                                "filepath_field": "metadata_storage_path",  # Explicitly include file path
                            },
                            "in_scope": True,
                        },
                    }
                ],
            },
        ).to_dict()

    total_tokens_in = completion["usage"]["prompt_tokens"]
    total_tokens_out = completion["usage"]["completion_tokens"]

    # Extract the LLM response and citations
    response_content = completion["choices"][0]["message"]["content"]
    citations = (
        completion["choices"][0]["message"]["context"].get("citations", [])
        if completion["choices"][0]["message"]["context"]
        else []
    )

    # Process citations to extract file paths

    response_content = doc_embedding(response_content, citations=citations)

    return {
        "response": response_content,
        "total_tokens_in": total_tokens_in,
        "total_tokens_out": total_tokens_out,
    }


def chatbot_ui():
    # Streamlit app configuration
    st.set_page_config(page_title="Sondia Chatbot", page_icon="robot", layout="wide")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # App title
    st.title("Sondia Chatbot")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to ask?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_response = llm(st.session_state.messages)

                st.markdown(full_response["response"])
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response["response"],
                }
            )

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    chatbot_ui()
