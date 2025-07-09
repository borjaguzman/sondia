import requests
import json

service_name = "searchiasondiatest"
api_version = "2025-05-01-preview"
tenat_id = "22e057da-0df5-40b4-8985-4988fa9dfdf4"
searchai_key = "dVLXG0CaOntZGcRMwHjKuzqUKpoqxZO2Ut8dKWR56WAzSeDuxOFm"

folder = "/PruebaRAG/Carpeta1"
headers = {"Content-Type": "application/json", "api-key": searchai_key}


def create_data_source():
    url = f"https://{service_name}.search.windows.net/datasources?api-version={api_version}"
    # Define the endpoint and headers
    sp_url = "https://aurysconsulting.sharepoint.com/sites/OnyxDB"
    app_id = "31bd6896-13aa-4019-96e2-d937d03923db"
    # app_secret = "W3Q8Q~1EIoyH3vd3kOodVsypQsDzGans3QpaHa4V"
    conn_str = f"SharePointOnlineEndpoint={sp_url};ApplicationId={app_id}"

    # Define the payload
    payload = {
        "name": "sharepoint-datasource",
        "type": "sharepoint",
        "credentials": {"connectionString": conn_str},
        "container": {
            "name": "allSiteLibraries",
            "query": None,
        },
    }

    # Make the POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check the response
    if response.status_code == 201:
        print("Datasource created successfully:", response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")


def create_index():
    url = f"https://{service_name}.search.windows.net/indexes?api-version={api_version}"
    # Index definition
    index_data = {
        "name": "sharepoint-index",
        "fields": [
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
            },
            {
                "name": "metadata_spo_item_name",
                "type": "Edm.String",
                "key": False,
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
            },
            {
                "name": "metadata_spo_item_path",
                "type": "Edm.String",
                "key": False,
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False,
            },
            {
                "name": "metadata_spo_item_content_type",
                "type": "Edm.String",
                "key": False,
                "searchable": False,
                "filterable": True,
                "sortable": False,
                "facetable": True,
            },
            {
                "name": "metadata_spo_item_last_modified",
                "type": "Edm.DateTimeOffset",
                "key": False,
                "searchable": False,
                "filterable": False,
                "sortable": True,
                "facetable": False,
            },
            {
                "name": "metadata_spo_item_size",
                "type": "Edm.Int64",
                "key": False,
                "searchable": False,
                "filterable": False,
                "sortable": False,
                "facetable": False,
            },
            {
                "name": "content",
                "type": "Edm.String",
                "searchable": True,
                "filterable": False,
                "sortable": False,
                "facetable": False,
            },
        ],
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(index_data))

    # Check the response
    if response.status_code == 201:
        print("Index created successfully!")
        print(response.json())
    else:
        print(f"Failed to create index. Status code: {response.status_code}")
        print(response.text)


def create_indexer():
    url = (
        f"https://{service_name}.search.windows.net/indexers?api-version={api_version}"
    )
    # Index definition
    indexer_data = {
    "name" : "sharepoint-indexer",
    "dataSourceName" : "sharepoint-datasource",
    "targetIndexName" : "sharepoint-index",
    "parameters": {
    "batchSize": None,
    "maxFailedItems": None,
    "maxFailedItemsPerBatch": None,
    "configuration": {
        "indexedFileNameExtensions" : ".pdf, .docx",
        "excludedFileNameExtensions" : ".png, .jpg",
        "dataToExtract": "contentAndMetadata"
      }
    },
    "schedule" : { },
    "fieldMappings" : [
        { 
          "sourceFieldName" : "metadata_spo_site_library_item_id", 
          "targetFieldName" : "id", 
          "mappingFunction" : { 
            "name" : "base64Encode" 
          } 
         }
    ]
}

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(indexer_data))

    # Check the response
    if response.status_code == 201:
        print("Index created successfully!")
        print(response.json())
    else:
        print(f"Failed to create index. Status code: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    # create_data_source()
    # create_index()
    #create_indexer()
