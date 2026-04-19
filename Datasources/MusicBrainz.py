# Placeholder for MusicBrainz datasource. This will be used to fetch metadata about music tracks, albums, and artists from the MusicBrainz database. 
# The implementation will include functions to search for music information based on various criteria such as track name, artist name, album name, etc. 
# The data fetched from MusicBrainz will be used to enrich the metadata of music files in the user's library.

#Initialize MusicBrainz client
import musicbrainzngs as mb
import pycountry
import json

mb.set_useragent("Music Detail Enrichment", "0.1", "https://github.com/D-Vella/music-detail-enrichment")

def search_artist(artist_name, confidence_threshold=85):
    """Search for an artist by name and return their MusicBrainz ID
    
    Args:        
        artist_name (str): The name of the artist to search for
        confidence_threshold (int): The minimum confidence score required to consider a match valid (default: 85)
    
    Returns:        str: The MusicBrainz ID of the best matching artist, or None if no match meets the confidence threshold
    """
    result = mb.search_artists(artist=artist_name, limit=10)

    cleaned_results = []
    for artist in result['artist-list']:
        cleaned_results.append({
            'id': artist['id'],
            'name': artist['name'],
            'score': int(artist.get('ext:score', 0)),
            'type': artist.get('type', 'Unknown')
        })

    # Filter artists based on confidence threshold
    filtered_artists = [artist for artist in cleaned_results if artist['score'] >= confidence_threshold]

    #Filter artists based on type (only consider artists and groups)
    filtered_artists = [artist for artist in filtered_artists if artist['type'] in ['Person', 'Group']]

    # Sort the remaining artists by score and return the best match
    sorted_artists = sorted(filtered_artists, key=lambda x: x['score'], reverse=True)

    # Check for a single exact match (case-insensitive) among the sorted artists. Example was Senses where there are multiple exact matches, only declare an exact metch if there is exactly one exact match to avoid false positives.
    count_exact_matches = sum(1 for artist in sorted_artists if artist['name'].lower() == artist_name.lower())
    # If we get an exact match, return it immediately
    if count_exact_matches == 1:
        for artist in sorted_artists:
            if artist['name'].lower() == artist_name.lower():
                return artist['id'], "Exact Match"
    
    if count_exact_matches > 1:
        return None, "Multiple Exact Matches"
    
    if count_exact_matches == 0:
        return None, "No Exact Match"

    # if len(sorted_artists) > 0:
    #     return sorted_artists[0]["id"], "Best Match"
    # else:
    #     return None, None
    
def get_artist_info(mb_id):
    """Get detailed information about an artist using their MusicBrainz ID"""
    result = {}
    try:
        result = mb.get_artist_by_id(mb_id, includes=["release-groups", "url-rels", "tags"], release_type=["album"])
    except mb.WebServiceError as exc:
        print("Something went wrong with the request: %s" % exc)
        return result  # Return empty dict on error
    else:
        # This data gappy so I need to guard against missing fields.
        artist = result["artist"]
        tags = artist.get("tag-list", []) or []  # Ensure we have a list even if "tag-list" is missing
        links = artist.get("url-relation-list", []) or []  # Ensure we have a list even if "url-relation-list" is missing

        #parse the links to find the official homepage and bandcamp page (if they exist):
        homepage = None
        bandcamp = None

        for link in links:
            if link["type"] == "official homepage":
                homepage = link["target"]
            elif link["type"] == "bandcamp":
                bandcamp = link["target"]

        #Parse the album information to return only sutdio albums (exclude singles, EPs, compilations, etc.)
        albums = []
        release_groups = artist.get("release-group-list", [])
        for album in release_groups:
            if album["primary-type"] == "Album" and "secondary-type-list" not in album:
                albums.append(album["title"])

        #Country Processing:
        country_name = None
        country_code = artist.get("country") or None
        if country_code and len(country_code) != 2:
            country_code = None  # Invalid country code, set to None
        else:
            country_name = pycountry.countries.get(alpha_2=country_code)
        
        tags = []
        for tag in artist.get("tag-list", []):
            tags.append({
                "name": tag["name"],
                "score": int(tag.get("count", 0))  # Convert count to an integer, default to 0 if missing
            })

        #Build and return the result dictionary
        result["homepage"] = homepage
        result["bandcamp"] = bandcamp
        result["country"] = country_name
        result["albums"] = albums
        result["tags"] = [(tag["name"], tag["score"]) for tag in tags]

        return result