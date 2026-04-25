# Python Learning Points

A running log of bugs and concepts encountered during this project, with notes to help avoid the same mistakes in future.

---

## 1. Secrets and Token Handling in Git

**Issue:** API tokens and secrets need to be kept out of git history entirely.

**Key lessons:**
- Never hardcode tokens in source files. Once committed, a secret is compromised — even if you delete it in a later commit, it lives in the history forever.
- Store secrets in a `.env` file and add `.env` to `.gitignore` before your first commit.
- Commit a `.env.example` file instead, showing the variable names but not the values. This tells other developers (or your future self) what needs to be configured.
- Load secrets at runtime using `os.getenv()` and the `python-dotenv` library:

```python
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("MY_API_TOKEN")
```

- If a secret is accidentally committed: remove it from the file, rotate the token immediately, then clean the git history using `git filter-branch` or the BFG Repo-Cleaner.

---

## 2. UnboundLocalError — Variable Used Before Assignment

**File:** `Datasources/MusicBrainz.py` — `get_artist_info()`

**Issue:** Certain artists with no country set in MusicBrainz caused a crash. The variable `country_name` was only assigned inside an `else` block, so when the `if` condition short-circuited (because `country_code` was `None`), `country_name` was never created — but the code tried to use it anyway.

```python
# Buggy version
country_code = artist.get("country") or None
if country_code and len(country_code) != 2:
    country_code = None          # else is skipped entirely
else:
    country_name = pycountry.countries.get(alpha_2=country_code)

result["country"] = country_name  # crashes if country_code was None
```

**Key lessons:**
- Always initialise variables to a safe default before conditional branches that may or may not assign them:

```python
country_name = None   # safe default
country_code = artist.get("country") or None
if country_code and len(country_code) == 2:
    country_name = pycountry.countries.get(alpha_2=country_code)
```

- Any variable that is only assigned inside an `if`/`else` block can cause an `UnboundLocalError` if none of the branches execute. Get into the habit of initialising at the top of the scope.
- External data (APIs, databases) is often incomplete. Assume fields can be missing and guard accordingly.

---

## 3. TypeError — Iterating a Dictionary Gives Keys, Not Values

**File:** `app.ipynb` — cell 6

**Issue:** `artist_database` is a `dict` mapping lowercase name strings to `Artist` objects. Iterating over the dictionary (or passing it to `sorted()`) yields the **keys** — plain strings — not the values. Trying to access `artist["mbid"]` on a string causes:

```
TypeError: string indices must be integers, not 'str'
```

```python
# Buggy — iterates over keys (strings)
for artist in random.sample(sorted(artist_database), ...):
    if artist["mbid"] is None:   # artist is a string here!
```

**Key lessons:**
- Iterating over a `dict` always gives **keys**. To get values use `.values()`, to get both use `.items()`.
- When you need to sort objects by an attribute, use a `key` function:

```python
# Correct — iterates over Artist objects, sorted by name
for artist in random.sample(
    sorted(artist_database.values(), key=lambda a: a.name),
    min(10, len(artist_database))
):
```

- A quick way to check what a loop variable actually is: `print(type(artist))` at the top of the loop body.

---

## 4. Choosing the Right Data Structure — Set vs List of Tuples

**File:** `Data/artists.py`

**Issue:** Tags were stored in a `set`, which automatically deduplicates. This is fine for a single data source, but the project collects tags from multiple sources (MusicBrainz, Last.fm, etc.) where the same tag appearing multiple times across sources is meaningful signal — it should increase that tag's weight, not be silently discarded.

**Key lessons:**
- A `set` is the right choice when you want uniqueness and membership testing, and the count doesn't matter.
- A `list` of `(tag, count)` tuples is the right choice when you need to accumulate raw data from multiple sources and process it later:

```python
# Accumulate without deduplication
self.tags = []

def add_tags(self, tags):
    self.tags.extend(tags)   # [(tag, count), ...]

# Later, in a separate processing step:
from collections import Counter
def aggregate_tags(self):
    totals = Counter()
    for tag, count in self.tags:
        totals[tag] += count
    return totals.most_common()
```

- Separate **data collection** from **data processing**. Collect raw data in full, then process it once at the end. This makes it easier to debug, re-run, and add new sources without changing the processing logic.

---

## 5. Jupyter Notebooks Must Contain Valid JSON

**File:** `app.ipynb`

**Issue:** An empty file (0 bytes) was committed as `app.ipynb`. GitHub and Jupyter both reported "The Notebook Does Not Appear to Be Valid JSON" because a `.ipynb` file is a JSON document and an empty file is not valid JSON.

**Key lessons:**
- A `.ipynb` file is just a JSON file with a specific structure. Even a blank notebook needs the skeleton:

```json
{
 "cells": [],
 "metadata": {
  "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
  "language_info": {"name": "python", "version": "3.x.x"}
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

- When creating a new notebook, always create it through Jupyter (File → New Notebook) rather than as a blank file, so the structure is generated for you.
- Before committing a notebook, check that it at least opens and renders without errors locally.

---

## 6. Dictionary Iteration — `.values()` vs `.items()`

**File:** `app.ipynb`

**Issue:** `clean_tags()` returns a `defaultdict` mapping tag names to scores `{ "heavy metal": 120, "power metal": 85 }`. Iterating over the dict directly yields the string keys, so `x[1]` in the sort lambda was indexing into the string (e.g. `"heavy metal"[1]` = `"e"`) rather than getting the score — causing `IndexError: string index out of range` for any tag with a name shorter than 2 characters.

```python
# Buggy — iterates over keys (strings), x[1] is a character not a score
sorted_tags = sorted(cleaned_tags, key=lambda x: x[1], reverse=True)

# Fixed — .items() yields (name, score) tuples
sorted_tags = sorted(cleaned_tags.items(), key=lambda x: x[1], reverse=True)
```

**Key lessons:**
- `.values()` — use when you only need the value as a standalone object (e.g. iterating `Artist` objects from a name→Artist dict).
- `.items()` — use when you need key and value together as a pair, e.g. when sorting, filtering, or displaying both. Yields `(key, value)` tuples you can index with `[0]` and `[1]`.
- The rule of thumb: if you find yourself writing `x[1]` in a lambda over a dict, you almost certainly want `.items()` not a bare iteration.

---

## 7. TypeError — Slicing or Indexing `None`

**File:** `Data/artists.py` — `Artist.__str__()`

**Issue:** `self.mbid[:8]` crashed for artists that had no MusicBrainz ID. `mbid` was `None`, and `None` is not a sequence — you cannot slice or index it.

```
TypeError: 'NoneType' object is not subscriptable
```

The error surfaced in the notebook via `{updated_data}` in an f-string, which called `__str__()` on the `Artist` object. The notebook line looked innocent; the real crash was one level deeper in `artists.py`.

```python
# Buggy — crashes if mbid is None
return f"'{self.name}' (mbid: {self.mbid[:8]}...)"

# Fixed — guard before slicing
mbid_display = f"{self.mbid[:8]}..." if self.mbid else "no mbid"
return f"'{self.name}' (mbid: {mbid_display})"
```

**Key lessons:**
- Any time you slice or index a variable (`x[:8]`, `x[0]`, `x["key"]`), ask: can this ever be `None`? If yes, guard it first.
- Read tracebacks **bottom up**: the bottom line is the error type and message; the line just above it is where the crash actually happened. The top of the traceback is merely where the chain started.
- An f-string like `{some_object}` silently calls `__str__()` — if that method has a bug, the error will appear to come from the f-string line, not from inside the class.
