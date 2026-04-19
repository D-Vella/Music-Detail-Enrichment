from notion_client import Client
from notion_client.helpers import collect_paginated_api
from dotenv import load_dotenv
import os
import json

# 1. Load the .env file: 
load_dotenv()

# 2. Access the variables using os.environ
notion_token = os.environ.get("NOTION_TOKEN")
#notion_database_id = os.environ.get("NOTION_DATABASE_ID")

# 3. Initialize the Notion client
notion = Client(auth=notion_token)

def update_mb_id(page_id, new_value, property_name, overwrite = False):
    page = notion.pages.retrieve(page_id=page_id)
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
                        "text": {"content": new_value}
                      }
                ]
            }
        }
    )

def build_property(property_type, value):
    """Convert a plain value into the nested Notion property structure."""
    if value is None:
        return None
    
    builders = {
        "title":        lambda v: {"title": [{"text": {"content": v}}]},
        "rich_text":    lambda v: {"rich_text": [{"text": {"content": v}}]},
        "select":       lambda v: {"select": {"name": v}},
        "multi_select": lambda v: {"multi_select": [{"name": i} for i in v]},
        "url":          lambda v: {"url": v},
        "checkbox":     lambda v: {"checkbox": v},
        "number":       lambda v: {"number": v},
        "date":         lambda v: {"date": {"start": v}},
    }
    
    if property_type not in builders:
        raise ValueError(f"Unknown property type: {property_type}")
    
    return builders[property_type](value)


def update_artist(notion, page_id, updates, dry_run=False):
    """
    Updates a Notion page with the provided field values.
    
    updates: dict of {notion_field_name: (property_type, value)}
    e.g. {
        "MB_ID":            ("rich_text", "abc-123"),
        "Country":          ("select",    "Finland"),
        "High Level Genre": ("select",    "Metal"),
        "Subgenre":         ("select",    "Power Metal"),
        "Website":          ("url",       "https://sonataarctica.info"),
    }
    """
    properties = {}
    
    for field_name, (property_type, value) in updates.items():
        payload = build_property(property_type, value)
        if payload is not None:
            properties[field_name] = payload
    
    if not properties:
        return
    
    if dry_run:
        print(f"DRY RUN — {page_id}:")
        for field, payload in properties.items():
            print(f"  {field}: {payload}")
        return
    
    notion.pages.update(page_id=page_id, properties=properties)

# Example Usage:
#     update_artist(notion, page_id, {
#     "MB_ID":            ("rich_text", mb_id),
#     "Country":          ("select",    country),
#     "High Level Genre": ("select",    genre),
#     "Website":          ("url",       homepage),
# }, dry_run=True)