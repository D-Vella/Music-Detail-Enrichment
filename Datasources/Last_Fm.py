# Placeholder for fetching metadata about music tracks, albums, and artists from the Last.fm API.
# The implementation will include functions to search for music information based on various criteria such as track name, artist name, album name, etc.
# The data fetched from Last.fm will be used to enrich the metadata of music files in the user's library. This will involve making API calls to Last.fm's endpoints and processing the responses to extract relevant information for the music files.

import os
from dotenv import load_dotenv

# 1. Load the .env file: 
load_dotenv()

# 2. Access the variables using os.environ
app_name = os.environ.get("LASTFM_API_APP_NAME")
api_key = os.environ.get("LASTFM_API_KEY")
api_secret = os.environ.get("LASTFM_API_SECRET")
username = os.environ.get("LASTFM_USERNAME")

Root_URL = "http://ws.audioscrobbler.com/2.0/"

def last_fm_call(method: str, artist: str, musicbrainz_id: str = None):
    # Last.fm API uses API key for authentication, so we just need to ensure it's available
    if not api_key:
        raise ValueError("LASTFM_API_KEY is missing. Please check your .env file.")
    
    import requests
    # Test the API key by making a simple request
    params = {
        'method': method,
        'api_key': api_key,
        'format': 'json'
    }

    if artist:
        params['artist'] = artist
    elif musicbrainz_id:
        params['mbid'] = musicbrainz_id
    else:
        raise ValueError("Either artist name or MusicBrainz ID must be provided for the API call.")

    response = requests.get(Root_URL, params=params)
    response.raise_for_status()  # Raise an error for bad status codes
    if response.status_code == 200:
        print("✅ Successfully authenticated with Last.fm API.")
    else:
        raise ValueError("Failed to authenticate with Last.fm API.")

    return response.json()

def get_artist_tags(artist: str):
    json_response = last_fm_call(method="artist.getTopTags", artist=artist)
    tags = []
    for tag in json_response['toptags']['tag']:
            tags.append((tag['name'], tag['count']))
    return tags