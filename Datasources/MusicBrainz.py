# Placeholder for MusicBrainz datasource. This will be used to fetch metadata about music tracks, albums, and artists from the MusicBrainz database. 
# The implementation will include functions to search for music information based on various criteria such as track name, artist name, album name, etc. 
# The data fetched from MusicBrainz will be used to enrich the metadata of music files in the user's library.

#Initialize MusicBrainz client
import musicbrainzngs as mb
import pycountry
import json
import os
from difflib import SequenceMatcher
CACHE_FILE = "Data/mb_cache.json"
SEARCH_CACHE_FILE = "Data/mb_search_cache.json"

mb.set_useragent("Music Detail Enrichment", "0.1", "https://github.com/D-Vella/music-detail-enrichment")

import unicodedata

def normalise_name(name):
    # Strip diacritics (ö → o, ü → u etc.)
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(c for c in name if not unicodedata.combining(c))
    # Normalise ampersands
    name = name.replace(' & ', ' and ').replace('&', 'and')
    # Collapse whitespace
    name = ' '.join(name.split()).lower()
    return name

def name_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() * 100

def search_artist(artist_name:str, confidence_threshold=85):
    """Search for an artist by name and return their MusicBrainz ID

    Args:
        artist_name (str): The name of the artist to search for
        confidence_threshold (int): The minimum confidence score required to consider a match valid (default: 85)

    Returns:        str: The MusicBrainz ID of the best matching artist, or None if no match meets the confidence threshold
    """

    search_cache = _get_search_cache()
    if artist_name in search_cache:
        cached_mb_id, cached_reason = search_cache[artist_name]
        return cached_mb_id, cached_reason

    result = mb.search_artists(artist=artist_name, limit=10)

    cleaned_results = []
    for artist in result['artist-list']:
        cleaned_results.append({
            'id': artist['id'],
            'name': normalise_name(artist['name']),
            'score': int(artist.get('ext:score', 0)),
            'type': artist.get('type', 'Unknown')
        })

    filtered_artists = [artist for artist in cleaned_results if artist['score'] >= confidence_threshold]
    filtered_artists = [artist for artist in filtered_artists if artist['type'] in ['Person', 'Group']]
    sorted_artists = sorted(filtered_artists, key=lambda x: x['score'], reverse=True)

    if not sorted_artists:
        mb_id, reason = None, "No results above confidence threshold"
        _save_search_cache(artist_name, mb_id, reason)
        return mb_id, reason

    highest_score = sorted_artists[0]['score']
    count_exact_matches = sum(1 for artist in sorted_artists if artist['name'] == artist_name)

    if count_exact_matches == 1:
        for artist in sorted_artists:
            if artist['name'] == artist_name:
                _save_search_cache(artist_name, artist['id'], "Exact Match")
                return artist['id'], "Exact Match"

    if count_exact_matches > 1:
        mb_id, reason = None, f"Multiple Exact Matches ({highest_score})"
        _save_search_cache(artist_name, mb_id, reason)
        return mb_id, reason

    best_fuzzy = None
    best_sim = 0
    for artist in sorted_artists:
        sim = name_similarity(normalise_name(artist_name), artist['name'])
        if sim > best_sim:
            best_sim = sim
            best_fuzzy = artist

    if best_fuzzy and best_sim >= 90:
        _save_search_cache(artist_name, best_fuzzy['id'], f"Fuzzy Match ({best_sim:.0f}%)")
        return best_fuzzy['id'], f"Fuzzy Match ({best_sim:.0f}%)"

    mb_id, reason = None, f"No Match — best fuzzy was '{best_fuzzy['name']}' ({best_sim:.0f}%)"
    _save_search_cache(artist_name, mb_id, reason)
    return mb_id, reason
    
def get_artist_info(mb_id):
    """Get detailed information about an artist using their MusicBrainz ID"""
    cache = _get_cache()
    if mb_id in cache:
        return cache[mb_id]

    try:
        raw = mb.get_artist_by_id(mb_id, includes=["release-groups", "url-rels", "tags"], release_type=["album"])
    except mb.WebServiceError as exc:
        print("Something went wrong with the request: %s" % exc)
        return {}

    artist = raw["artist"]
    links = artist.get("url-relation-list", []) or []

    homepage = None
    bandcamp = None
    for link in links:
        if link["type"] == "official homepage":
            homepage = link["target"]
        elif link["type"] == "bandcamp":
            bandcamp = link["target"]

    albums = []
    for album in artist.get("release-group-list", []):
        if album["primary-type"] == "Album" and "secondary-type-list" not in album:
            albums.append(album["title"])

    country_name = None
    country_code = artist.get("country") or None
    if country_code and len(country_code) == 2:
        country_obj = pycountry.countries.get(alpha_2=country_code)
        country_name = country_obj.name if country_obj else None

    tags = [(tag["name"], int(tag.get("count", 0))) for tag in artist.get("tag-list", [])]

    result = {
        "homepage": homepage,
        "bandcamp": bandcamp,
        "country": country_name,
        "albums": albums,
        "tags": tags
    }

    save_cache(mb_id, result)
    return result
    
_cache = None
_search_cache = None

def _get_search_cache():
    global _search_cache
    if _search_cache is None:
        if os.path.exists(SEARCH_CACHE_FILE):
            with open(SEARCH_CACHE_FILE, "r") as f:
                _search_cache = json.load(f)
        else:
            _search_cache = {}
    return _search_cache

def _save_search_cache(key, mb_id, reason):
    cache = _get_search_cache()
    cache[key] = [mb_id, reason]
    os.makedirs("Data", exist_ok=True)
    with open(SEARCH_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def _get_cache():
    global _cache
    if _cache is None:
        _cache = load_cache()
    return _cache

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache_key, cache_response):
    cache = _get_cache()
    cache[cache_key] = cache_response
    os.makedirs("Data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)