import wikipediaapi # pyright: ignore[reportMissingImports]
import requests

def get_wikipedia_data(wikidata_id) -> tuple[str | None, str | None]:
    """
    Retrieve data from Wikipedia for a given Wikidata ID.
    This function uses the Wikidata ID to find the corresponding English Wikipedia page title,
    then fetches the summary and discography sections from that page.
    """
    wiki_wiki = wikipediaapi.Wikipedia(user_agent='MusicDetailEnrichmentBot/1.0 (https://github.com/D-Vella/Music-Detail-Enrichment)', language='en')

    summary = None
    discography_page = None

    main_title, discography_title = get_from_wikidata(wikidata_id)
    if main_title is None:
        # If we can't find a Wikipedia page title from Wikidata, we can't proceed with fetching data.
        # This assumes there is an english Wikipedia page, other languages are not considered.
        return None, None
    
    main_page = wiki_wiki.page(main_title)
    discography_page = wiki_wiki.page(discography_title)
    

    if main_page.exists():
        summary = main_page.summary
    else:
        return None, None

    if discography_title is not None and discography_page.exists():
        print("Artist has wiki page and discography page.")
        discography_page = discography_page.text
    else:
        for section in main_page.sections:
            if "discography" in section.title.lower():
                print("Artist has wiki page with discography section.")
                discography_page = section.text
                break

    return summary, discography_page


def make_wikidata_api_request(wikidata_id):
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    headers = {
        "User-Agent": "MusicDetailEnrichmentBot/1.0 (https://github.com/D-Vella/Music-Detail-Enrichment)"
    }
    response = requests.get(url, headers=headers).json()
    return response

def get_wikipedia_title_from_wikidata(wikidata_id, wikidata_response=None):
    if wikidata_response is None:
        response = make_wikidata_api_request(wikidata_id)
    else:
        response = wikidata_response

    # Where there has been a redirect, the original Wikidata ID may not be present in the response. In that case, we take the first entity returned, which should be the correct one.
    if wikidata_id not in response["entities"]:
        entity = next(iter(response["entities"].values()))
    else:
        entity = response["entities"][wikidata_id]

    sitelinks = entity.get("sitelinks", {})
    
    # Get the English Wikipedia article title
    enwiki = sitelinks.get("enwiki")
    if enwiki:
        title = enwiki["title"]
        return title

def get_from_wikidata(wikidata_id):
    main_title = None
    discography_title = None
    response = make_wikidata_api_request(wikidata_id)
    
    # Where there has been a redirect, the original Wikidata ID may not be present in the response. In that case, we take the first entity returned, which should be the correct one.
    if wikidata_id not in response["entities"]:
        entity = next(iter(response["entities"].values()))
    else:
        entity = response["entities"][wikidata_id]

    main_title = get_wikipedia_title_from_wikidata(wikidata_id, response)
    
    discography = entity.get("claims", {}).get("P358", []) # P358 is the property for "discography"
    if discography:
        id_code = discography[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        discography_response = make_wikidata_api_request(id_code)
        discography_title = get_wikipedia_title_from_wikidata(id_code, discography_response)

    return main_title, discography_title