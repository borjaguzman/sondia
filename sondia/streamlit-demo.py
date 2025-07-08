import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI

load_dotenv(find_dotenv())


def llm(input):
    deployment = "gpt-4.1-nano"
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint=azure_endpoint,
    )

    with open("model_instructions.md", "r", encoding="utf-8") as file:
        model_instructions = file.read()

    prompt = input
    completion = client.chat.completions.create(
        model=deployment,
        temperature=0.0,
        top_p=1,
        seed=43,
        messages=[
            {
                "role": "system",
                "content": model_instructions,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
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
    )
    total_tokens_in = completion.usage.prompt_tokens
    total_tokens_out = completion.usage.completion_tokens

    # Extract the LLM response and citations
    response_content = completion.choices[0].message.content
    citations = (
        completion.choices[0].message.context.get("citations", [])
        if completion.choices[0].message.context
        else []
    )

    # Process citations to extract file paths
    file_paths = [
        citation["filepath"] for citation in citations if "filepath" in citation
    ]

    return {
        "response": response_content,
        "file_paths": file_paths[0],  # top documento en score
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
                response = llm(prompt)
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    # chatbot_ui()
    print(llm("cual es mi color favorito?"))
