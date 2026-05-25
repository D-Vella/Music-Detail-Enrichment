import json
from services.config import LLM_ENDPOINT


def call_llm_api(prompt: str, system: str, format: str ="json") -> str:
    import requests

    payload = {
        "model": "gemma4:e4b",
        "stream": False,
        "think": False, 
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
    }

    if format == "json":
        payload["format"] = "json"

    api_response = requests.post(f'{LLM_ENDPOINT}/api/chat',json=payload)

    import json
    returnMessages = api_response.text.splitlines()
    completeMessage = ''

    for idx, message in enumerate(returnMessages):
        returnMessage = json.loads(message)
        completeMessage += returnMessage.get('message', {}).get('content', '')

    return completeMessage

def llm_page_entry(prompt: str) -> tuple:
    system_prompt = """
        Your job is to take data from a Wikipedia page and generate a structured JSON object 
        with the following keys:
        {
            "overview": "string",
            "sound": "string",
            "activity": "string",
            "discography": {
                "Release Type": count
            }
        }

        Rules for each section:

        overview: A concise summary of the most important information about the artist,
        including their background, career highlights, and notable achievements.
        Maximum 200 words.

        sound: A description of the artist's musical style, influences, and any unique
        characteristics of their music. Assume the reader has no prior knowledge of the
        artist. Maximum 200 words.

        activity: A single sentence describing the artist's current status — whether they
        are active, on hiatus, or disbanded. If active, include their most recent release
        or upcoming projects if known.

        discography: A JSON object where each key is a release type (e.g. Studio Albums,
        Live Albums, EPs, Compilations) and the value is the count as an integer.
        Only include release types that are present.

        If insufficient information is available for any section, return null for that key.
        Do not guess or invent information.

        Return only the JSON object. No preamble, no explanation, no markdown code fences.
    """

    llm_response = call_llm_api(prompt=prompt, system=system_prompt, format="json")
    try:
        response = json.loads(llm_response)
        overview = response.get("overview", "")
        sound = response.get("sound", "")
        activity = response.get("activity", "")
        discography = response.get("discography", "")
    except Exception as e:
        print("Issue with LLM response. Printing raw response.")
        print(f"\n{repr(llm_response)}")
        raise ValueError(f"Failed to parse LLM response: {e}")

    return overview, sound, activity, discography

