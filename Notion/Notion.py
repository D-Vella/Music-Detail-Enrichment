from notion_client import Client
from notion_client.helpers import collect_paginated_api
from dotenv import load_dotenv
import os
import json

# 1. Load the .env file: 
load_dotenv()

# 2. Access the variables using os.environ
notion_token = os.environ.get("NOTION_TOKEN")
notion_database_id = os.environ.get("NOTION_DATABASE_ID")

# 3. Initialize the Notion client
notion = Client(auth=notion_token)

def get_artists_db():
    response =  collect_paginated_api(
        notion.data_sources.query, data_source_id=notion_database_id
    )
    return response

def update_page_property(page_id, property_name, property_value):
    #get page properties first
    page = notion.pages.retrieve(page_id=page_id)
    existing_properties = page["properties"][property_name]
    
    #If the property is already set skip

    notion.pages.update(
        page_id=page_id,
        properties=properties
    )

def update_mb_id(page_id, new_mb_id):
    page = notion.pages.retrieve(page_id=page_id)
    property_name = "MB_ID"
    property_type = page['properties'][property_name]['type']
    property_value = page['properties'][property_name][property_type]

    if property_type == "rich_text" and property_value:
        #print(f"MB_ID already set for page {page_id} to {property_value}, skipping update.")
        return  # Exit early if already set
    
    notion.pages.update(
        page_id=page_id,
        properties={
            property_name:{
                property_type: [
                     {
                        "type": "text",
                        "text": {"content": new_mb_id}
                      }
                ]
            }
        }
    )