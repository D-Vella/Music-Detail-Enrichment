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

def clean_tags(tags):
    from collections import defaultdict
    #ensure you have tuples.
    flat_list = [ item for item in tags if type(item) == tuple]
    #normalize the values using lower and strip.
    normalized_list = [ (item[0].strip().lower(), item[1]) for item in flat_list]

    # Combine into single entries, summing scores
    dd_flat_list = defaultdict(int)
    for key, value in normalized_list:
        dd_flat_list[key] += value

    return dd_flat_list