# Codebase Feedback — V1.0 Review

---

## 1. Code Quality & PEP 8

### `Data/artists.py`

**`display_info` will crash** — `self.tags` is now a list of tuples like `[("metal", 5)]`, but line 28 does `', '.join(sorted(self.tags))`, which expects strings. This will throw `TypeError: sequence item 0: expected str instance, tuple found` any time you call it.

**`__dict__.update(kwargs)` is risky** — line 16 blindly copies all keyword arguments into the instance dictionary. If a caller accidentally passes a keyword that matches an existing attribute (`name`, `mbid`, etc.), it will silently overwrite it with no warning.

**Misleading comment** — `# Storage Functions.` (line 35) sits at column 0 inside the class definition, making it look like the class has ended. Move it inside with proper indentation or remove it.

---

### `Data/tags.py`

**`isinstance` vs `type ==`** — line 25 uses `type(item) == tuple`. The Pythonic way is `isinstance(item, tuple)`, which also handles subclasses and is the PEP 8 preference.

**`GOOD_TAGS` and `NOISE_TAGS` are never used** — both sets are defined but `clean_tags()` doesn't reference them. Either wire them in or remove them to avoid confusion about whether tag filtering is actually happening.

**Import inside function** — `from collections import defaultdict` on line 23 is inside `clean_tags()`. Imports should always be at the top of the file unless there is a specific reason to defer them (circular imports, optional heavy dependencies). Move it to the top.

**No docstring** — `clean_tags()` has no docstring explaining what it expects, what it returns, or what "cleaning" means in this context.

---

### `Datasources/MusicBrainz.py`

**Stale placeholder comment block** — lines 1–3 are copy-paste boilerplate from when the file was a stub. The file is now fully implemented; remove them.

**`import unicodedata` is mid-file** — line 16, after `mb.set_useragent()`. All imports must be at the top of the file per PEP 8 (E402).

**Inconsistent cache function naming** — `save_cache` is public (no underscore), but `_get_cache`, `_get_search_cache`, and `_save_search_cache` are private. Either make `save_cache` `_save_cache` to match, or make them all public. The inconsistency is misleading.

**Exact match comparison on normalised vs. unnormalised name** — in `search_artist()`, artist names from MB are run through `normalise_name()` (line 52) but the `artist_name` argument is not normalised before the exact-match comparison on line 67 (`artist['name'] == artist_name`). An artist named "Motörhead" would never match because the stored name becomes "motorhead" but `artist_name` is still "Motörhead". The normalised query name should be computed once at the top of the function and used consistently throughout.

---

### `Datasources/Last_Fm.py`

**Stale placeholder comment block** — lines 1–3, same issue as MusicBrainz.py. Remove them.

**`import requests` inside a function** — line 25, inside `last_fm_call()`. Move to the top of the file.

**`Root_URL` should be `ROOT_URL`** — PEP 8 (and common Python convention) is that module-level constants are `UPPER_SNAKE_CASE`. `Root_URL` is mixed case.

**Redundant length check** — `if len(json_response) != 0:` (line 48) should be `if json_response:`. Testing truthiness directly is idiomatic Python; `len() != 0` is verbose and the style linters will flag it.

---

### `Notion/writer.py` and `Notion/reader.py`

**Unused imports** — both files import `json` and `os` but never use them. Remove them.

**Commented-out line left in** — `writer.py` line 12: `#notion_database_id = os.environ.get("NOTION_DATABASE_ID")`. If it's not needed, delete it; if it might be needed, add a note explaining why it's commented out.

---

## 2. Error Handling

### `Datasources/MusicBrainz.py`

**Cache I/O has no error handling** — `_get_cache()` and `_get_search_cache()` open and `json.load()` the cache files with no try/except. If a cache file is corrupted (e.g. truncated by an interrupted write), the entire module will fail to import or the first API call will crash. Wrap in a try/except and fall back to an empty dict:

```python
try:
    with open(CACHE_FILE, "r") as f:
        _cache = json.load(f)
except (json.JSONDecodeError, OSError):
    _cache = {}
```

**Only `WebServiceError` is caught** — `get_artist_info()` catches `mb.WebServiceError` but not network-level errors (connection timeout, DNS failure) or unexpected API response shapes. These will propagate as unhandled exceptions. A broader `except Exception as exc` with a log message would be safer here.

---

### `Datasources/Last_Fm.py`

**Last.fm API errors are not caught** — Last.fm returns errors as JSON bodies (`{"error": 6, "message": "Artist not found"}`) rather than HTTP error codes. `response.raise_for_status()` will not catch these. `get_artist_tags()` should check for an `"error"` key in the response before trying to parse tags.

**No handling of network failures** — `requests.get()` can raise `requests.exceptions.ConnectionError` or `requests.exceptions.Timeout`. Neither is caught. For a tool that runs over a large artist database, a single network blip should not crash the whole run.

---

### `Notion/reader.py` and `Notion/writer.py`

**No validation that credentials are set** — `reader.py` creates the Notion client at import time using `notion_token`, but if the `.env` file is missing or the variable is not set, `notion_token` will be `None` and every API call will fail with an unhelpful authentication error. An early guard would surface the problem clearly:

```python
if not notion_token:
    raise EnvironmentError("NOTION_TOKEN is not set. Check your .env file.")
```

**No error handling on API calls** — `writer.py`'s `update_artist()` calls `notion.pages.update()` with no try/except. Notion API errors (rate limits, invalid page IDs, permission errors) will propagate uncaught.

---

## 3. Weakest Part of the Codebase

**`Data/artists.py`** is the weakest file.

The `Artist` class is the central data model that every other part of the project passes data through, which makes its bugs higher impact than the same bugs elsewhere:

- `display_info()` will crash on the current tag format (tuples not strings) — meaning the only built-in way to inspect an artist object at runtime is broken.
- The `__dict__.update(kwargs)` pattern makes the class's actual attributes unpredictable and hard to debug — you can never be sure what attributes an `Artist` instance has without reading the calling code.
- There are no type hints anywhere on the class, which makes it harder to catch mismatches (like passing a string where a list of tuples is expected) before they cause runtime errors.

The class works well enough to get data in and out, but it needs a tidy before you build more on top of it.

---

## 4. Dead Code & Repo Hygiene

### Files to remove

**`env_exmaple.py`** — this has a typo in its name, references `OPENAI_API_KEY`, `DATABASE_URL`, and `WEATHER_API_KEY` which are not used anywhere in this project, and is completely redundant now that `.env.example` exists. Delete it.

**`Notion/Notion.py`** — the original monolithic Notion file. It has been superseded by `Notion/reader.py` and `Notion/writer.py`. Verify nothing still imports from it, then delete it.

### Files to clean up

**`Datasources/Bandcamp.py`, `Datasources/Spotify.py`, `Datasources/Wikidata.py`** — pure placeholder comments with no code. Either stub out a function signature (even a `raise NotImplementedError`) so the intent is clear and importable, or remove them until you're ready to implement them. As-is they create the impression of functionality that doesn't exist.

### Things to add

**`README.md` is empty** — it currently only contains the project title. At minimum it should describe what the project does, what the prerequisites are, how to set up the `.env` file, and how to run `app.ipynb`. Anyone (including future you) looking at the repo cold has no idea where to start.

**Pin versions in `requirements.txt`** — the file lists bare package names with no versions. This means a fresh install six months from now could pull in a breaking release. Run `pip freeze > requirements.txt` (or use `pip freeze | grep -f requirements.txt`) to capture the exact versions you are currently running.

**`Datasources/Scratch/` notebooks** — these are useful for your own development but they add noise for anyone else reading the repo. Consider moving them to a top-level `scratch/` or `notebooks/` folder, or adding a comment in the README explaining they are experimental.

**`GOOD_TAGS` in `tags.py`** — if you intend to use this as a canonical genre allowlist for filtering or mapping tags, it belongs in a config file or at least needs to be connected to `clean_tags()`. Right now it's defined and goes nowhere.
