# Placeholder for MusicBrainz datasource. This will be used to fetch metadata about music tracks, albums, and artists from the MusicBrainz database. 
# The implementation will include functions to search for music information based on various criteria such as track name, artist name, album name, etc. 
# The data fetched from MusicBrainz will be used to enrich the metadata of music files in the user's library.

#Initialize MusicBrainz client
import musicbrainzngs as mb
import pycountry
import json

mb.set_useragent("Music Detail Enrichment", "0.1", "https://github.com/D-Vella/music-detail-enrichment")

def search_artist(artist_name):
    """Search for an artist by name and return their MusicBrainz ID"""
    result = mb.search_artists(artist=artist_name, limit=1)
    if len(result["artist-list"]) > 0:
        return result["artist-list"][0]["id"]
    else:
        return None
    
def get_artist_info(mb_id):
    """Get detailed information about an artist using their MusicBrainz ID"""
    result = {}
    try:
        result = mb.get_artist_by_id(mb_id, includes=["release-groups", "url-rels", "tags"], release_type=["album"])
    except mb.WebServiceError as exc:
        print("Something went wrong with the request: %s" % exc)
    else:
        artist = result["artist"]
        tags = artist["tag-list"]
        links = artist["url-relation-list"]

    result["homepage"] = [link["target"] for link in links if link["type"] == "official homepage"][0]
    result["country"] = pycountry.countries.get(alpha_2=artist["country"])
    result["albums"] = [album["title"] for album in artist["release-group-list"] if album["primary-type"] == "Album" and "secondary-type-list" not in album]

    return result