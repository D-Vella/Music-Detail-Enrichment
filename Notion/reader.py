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