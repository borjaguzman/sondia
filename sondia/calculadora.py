import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks import get_openai_callback

load_dotenv(find_dotenv())


def llm(input):
    deployment = "gpt-4.1-nano"
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    llm = AzureChatOpenAI(
        api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint=azure_endpoint,
        model=deployment,
        temperature=0.0,
        top_p=1,
        seed=43,
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"],
                        "index_name": os.environ["AZURE_SEARCH_INDEX_NAME"],
                        # "query_type": "semantic",  # NOTE: no funciona en free tier. Activar en el real
                        "top_n_documents": 5,  # NOTE: Esto puede modificarse si el usuario hace preguntas que requieren mas contexto
                        "authentication": {
                            "type": "api_key",
                            "key": os.environ["AZURE_SEARCH_API_KEY"],
                        },
                    },
                }
            ],
        },
    )
    with open("model_instructions.md", "r", encoding="utf-8") as file:
        model_instructions = file.read()

    messages = [
        ("system", model_instructions),
        ("user", input),
    ]
    with get_openai_callback() as cb:
        ai_msg = llm.invoke(messages)
        print(f"total tokens: {cb.total_tokens}")
        print(f"Total Cost (USD): ${format(cb.total_cost, '.6f')}")

    return ai_msg.content


if __name__ == "__main__":
    print(llm("de que trata la reunion?"))
