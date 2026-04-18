class NotionDatabase:
    def __init__(self):
        pass

    def get_text(self, prop):
        """Rich text or title field → plain string"""
        items = prop.get("title") or prop.get("rich_text") or []
        return items[0]["plain_text"] if items else None

    def get_select(self, prop):
        """Single select field → string"""
        sel = prop.get("select")
        return sel["name"] if sel else None

    def get_multi_select(self, prop):
        """Multi-select field → list of strings"""
        return [item["name"] for item in prop.get("multi_select", [])]

    def get_checkbox(self, prop):
        """Checkbox field → bool"""
        return prop.get("checkbox", False)

    def get_url(self, prop):
        """URL field → string"""
        return prop.get("url")

    def get_date(self, prop):
        """Date field → start date string (YYYY-MM-DD)"""
        d = prop.get("date")
        return d["start"] if d else None

    def get_number(self, prop):
        """Number field → int or float"""
        return prop.get("number")

    def get_relation_ids(self, prop):
        """Relation field → list of related page IDs"""
        return [rel["id"] for rel in prop.get("relation", [])]

class myNotionDatabases(NotionDatabase):
    def extract_artist(self, page):
        props = page["properties"]
        return {
            "id":                   page["id"],
            "artist_name":          self.get_text(props["Artist Name"]),
            "status":               self.get_select(props["Status"]),
            "high_level_genre":     self.get_select(props["High Level Genre"]),
            "subgenre":             self.get_multi_select(props["Subgenre"]),
            "country":              self.get_text(props["Country"]),
            "label":                self.get_text(props["Label"]),
            "rating":               self.get_select(props["Rating"]),
            "format_owned":         self.get_multi_select(props["Format Owned"]),
            "website":              self.get_url(props["Website"]),
            "bandcamp_url":         self.get_url(props["Bandcamp url"]),
            "following_on_bandcamp":self.get_checkbox(props["Following on Bandcamp"]),
            "seen_live":            self.get_checkbox(props["Seen Live"]),
            "mb_id":                self.get_text(props["MB_ID"]),
            "how_i_found_them":     self.get_text(props["How I Found Them"]),
            "added":                self.get_date(props["Added"]),
            "last_listened":        self.get_date(props["Last Listened"]),
            "notes":                self.get_text(props["Notes"]),
            "Similar_to":           self.get_relation_ids(props["Similar to"]),
        }