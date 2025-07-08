# NOTE: Para correr esta api
# uvicorn main:app --host 0.0.0.0 --port 8000

import os
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI
from pydantic import BaseModel

from fastapi import FastAPI

load_dotenv(find_dotenv())

app = FastAPI()


class InputRequest(BaseModel):
    input: str


@app.post("/llm")
async def call_llm(request: InputRequest):
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

    prompt = request.input
    completion = client.chat.completions.create(
        model=deployment,
        temperature=0.0,
        # top_p=1, # NOTE: Pareciera que esto limita la respuesta del modelo
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
                        "query_type": "semantic",  # NOTE: no funciona en free tier. Activar en el real
                        # "top_n_documents": 5,  # NOTE: Esto puede modificarse si el usuario hace preguntas que requieren mas contexto
                        "authentication": {
                            "type": "api_key",
                            "key": os.environ["AZURE_SEARCH_API_KEY"],
                        },
                        "fields_mapping": {
                            "content_fields": ["content"],
                            "title_field": "metadata_storage_name",
                            "url_field": "metadata_storage_path",  # Map metadata_storage_path to URLs
                            "filepath_field": "metadata_storage_path",  # Explicitly include file path
                        },
                        "in_scope": True,
                    },
                }
            ],
        },
    )
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

    return {"response": response_content, "file_paths": file_paths}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
