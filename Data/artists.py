class Artist:
    """Represents a single artist with all their associated data."""
    def __init__(self, name, mbid, country, tags=None, **kwargs):
        # Core properties
        self.name = name
        self.mbid = mbid
        self.country = country
        self.website_url = kwargs.get("website_url")
        self.bandcamp_url = kwargs.get("bandcamp_url")
        # Use a list for tags to capture duplicate tags
        # Ensure we have a list even if tags is None
        self.tags = list(tags) if tags else [] 
        
        # Use other keyword arguments to store any other data (e.g., genre, formation_year)
        self.__dict__.update(kwargs) 

    def __str__(self):
        # This allows the object to print nicely when you print it
        return f"'{self.name}' (mbid: {self.mbid[:8]}...)"

    def display_info(self):
        print("-" * 30)
        print(f"ARTIST: {self.name}")
        print(f"  mbid: {self.mbid}")
        print(f"  Country/Origin: {self.country}")
        print(f"  Tags: {', '.join(sorted(self.tags))}")
        # Display other arbitrary properties
        for key, value in self.__dict__.items():
            if key not in ["name", "mbid", "country", "tags"]:
                print(f"  {key.capitalize()}: {value}")
        print("-" * 30)

# Storage Functions.

    def add_tags(self, tags):
        self.tags.extend(tags)
# def add_artist(artist: Artist):
#     """Adds or updates an artist in the database."""
#     # Normalize the key by making it lowercase and stripping whitespace
#     key = artist.name.strip().lower()
#     ARTIST_DATABASE[key] = artist

# def get_artist(name: str) -> Artist | None:
#     """Retrieves an artist object by name."""
#     key = name.strip().lower()
#     return ARTIST_DATABASE.get(key)
