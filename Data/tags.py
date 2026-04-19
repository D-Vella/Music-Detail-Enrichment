NOISE_TAGS = {
    "seen live", "favourite", "favorites", "awesome", "love",
    "beautiful", "amazing", "best", "classic", "legend",
    "female vocalist", "male vocalist", "british", "american",
    "german", "finnish", # Countries aren't genres
    "00s", "90s", "80s", # Decades aren't genres
    "all", "spotify", "recommended"
}

GOOD_TAGS = {
    "Heavy Metal", "Thrash Metal", "Death Metal", "Black Metal", "Doom Metal", "Power Metal", "Progressive Metal", "Symphonic Metal", "Folk Metal", "Gothic Metal", "Melodic Death Metal", "Melodic Black Metal", "Viking Metal", "Pagan Metal", "Speed Metal", "Groove Metal", "Nu Metal", "Metalcore", "Deathcore", "Djent", 
             
    "Classic Rock", "Hard Rock", "Punk Rock", "Post-Punk", "Alternative Rock", "Indie Rock", "Progressive Rock", "Psychedelic Rock", "Grunge", "Shoegaze", "Post-Rock", "Garage Rock", "Stoner Rock", "Desert Rock", 
    
    "House", "Techno", "Trance", "Drum and Bass", "Dubstep", "Ambient", "IDM", "Electro", "Trip Hop","Synthwave", "Darkwave", "Industrial", "EBM", "Noise", 
    
    "Pop", "Synth-Pop", "Dream Pop", "Indie Pop", "Soul", "R&B", "Neo Soul", "Funk", "Hip Hop", "Jazz", "Folk", "Country", 
    
    "Classical", "Blues", "Reggae", "World Music", "Singer-Songwriter"
             }

def normalise(tag: str) -> str:
    return tag.lower().replace("-", "").replace(" ", "")

def clean_tags(raw_tags):
    cleaned = []
    for tag in raw_tags:
        if tag["name"].lower() in NOISE_TAGS:
            continue
        normalised = normalise(tag["name"])
        if normalised in GOOD_TAGS:
            cleaned.append(GOOD_TAGS[normalised])  # Return canonical form
    return cleaned