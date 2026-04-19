# Bands & Artists Enrichment — Project Roadmap

A phased build plan for enriching a Notion music database with metadata from external
sources. Designed for spare-time development — each phase delivers something working
and useful on its own.

---

## Phase 1 — Environment & API Exploration
**Goal:** Get your tooling in place and confirm you can talk to at least one data source
before writing any enrichment logic.
**Estimated effort:** 1–2 sessions

### Tasks
- [X] Create a project folder and initialise a virtual environment
  ```
  bands_enrichment/
  ├── enrichers/        # One module per data source (musicbrainz.py, lastfm.py, etc.)
  ├── notion/           # Notion read/write logic
  ├── data/             # Any cached responses or local lookup files
  ├── main.py           # Entry point
  └── config.py         # API keys, constants, config
  ```
- [X] Install core dependencies: `musicbrainzngs`, `requests`, `python-dotenv`
- [X] Register for a Last.fm API key and store it in a `.env` file
- [X] Write a throwaway script that queries MusicBrainz for one known artist and prints
  the raw response — get a feel for what data is actually returned
- [X] Do the same for Last.fm — query an artist's tags and top albums
- [X] Add `.env` and any cache files to `.gitignore`
- [X] Initialise a Git repository and make your first commit

### Exit Criteria
Running a script returns structured data (artist name, country, tags) from at least one
external API for a manually specified artist name.

---

## Phase 2 — Notion Integration (Read)
**Goal:** Connect to your Notion database and pull the list of artists you want to enrich.
**Estimated effort:** 1–2 sessions

### Tasks
- [X] Install the `notion-client` Python library
- [X] Create a Notion integration at developers.notion.com and connect it to your
  Bands & Artists database
- [X] Store the Notion API key and database ID in `.env`
- [X] Write a `notion/reader.py` module that queries the database and returns a list of
  artists — at minimum: `id`, `name`, and any fields already populated
- [X] Print the results to confirm you're reading the right records
- [X] Handle pagination (Notion returns max 100 results per request)

### Exit Criteria
Running `notion/reader.py` prints a list of artist names from your live Notion database.

---

## Phase 3 — First Enricher: MusicBrainz
**Goal:** Build the first real enricher and populate a handful of fields for a single artist.
**Estimated effort:** 2–3 sessions

### Tasks
- [X] Write `enrichers/musicbrainz.py` with a function that accepts an artist name and
  returns a standardised dict:
  ```python
  {
    "country": "US",
    "formed_year": 1991,
    "album_count": 9,
    "musicbrainz_id": "..."
  }
  ```
- [X] Handle the fuzzy matching problem — MusicBrainz search returns multiple candidates,
  so implement a basic best-match strategy (e.g. exact name match first, then score by
  popularity/type)
- [X] Add basic error handling: artist not found, API rate limit, ambiguous results
- [X] Set a proper `User-Agent` header as MusicBrainz requires this for API access
- [X] Test against 5–10 artists from your list manually and review the output quality
- [X] Document fields that are missing or unreliable as known data quality gaps

### Exit Criteria
Given an artist name, `musicbrainz.py` returns a clean dict of structured data. You have
a rough sense of how reliable the results are for your catalogue.

---

## Phase 4 — Second Enricher: Last.fm (Genre & Tags)
**Goal:** Add genre/subgenre data from Last.fm to complement MusicBrainz.
**Estimated effort:** 1–2 sessions

### Tasks
- [X] Write `enrichers/lastfm.py` with a function that returns top tags for an artist
- [ ] Apply data cleaning logic to the raw tags — Last.fm tags are community-driven and
  noisy (e.g. filter out tags like "seen live", "favourite", "awesome")
- [ ] Define a simple tag hierarchy or priority list: primary genre first, subgenre second
- [ ] Where MusicBrainz already returned genre data, compare the two sources and decide
  on a merge strategy (e.g. prefer Last.fm tags, fall back to MusicBrainz)
- [ ] Test against the same 5–10 artist sample from Phase 3

### Exit Criteria
Given an artist name, `lastfm.py` returns a cleaned list of genre/subgenre tags. You have
a merge strategy documented in code comments or a README note.

---

## Phase 5 — Notion Integration (Write)
**Goal:** Take the enriched data and write it back into Notion.
**Estimated effort:** 2 sessions

### Tasks
- [X] Write `notion/writer.py` with a function that accepts a Notion page ID and a dict
  of field updates, and patches the page via the API
- [ ] Map your enricher output fields to Notion property names — handle type differences
  (text, number, select, multi-select, URL)
- [ ] Add a dry-run mode: print what *would* be written without actually writing it —
  useful for QA before committing changes
- [ ] Run a dry-run over your sample set and review the proposed updates
- [ ] Confirm the writes look correct on one artist before running at scale

### Exit Criteria
Running the script in dry-run mode shows a sensible update plan. Running it live
updates one test artist in Notion correctly.

---

## Phase 6 — Pipeline & Batch Processing
**Goal:** Chain the enrichers together and run them across your full database.
**Estimated effort:** 2–3 sessions

### Tasks
- [ ] Write `main.py` that orchestrates the full pipeline:
  1. Read all artists from Notion
  2. For each artist, call each enricher in sequence
  3. Merge results and write back to Notion
- [ ] Add a `skip_if_populated` flag — don't overwrite fields that already have data
  unless explicitly requested
- [ ] Add basic logging so you can see what happened during a run
- [ ] Add a simple rate-limit delay between API calls (MusicBrainz allows ~1 req/sec)
- [ ] Handle failures gracefully — one bad artist lookup shouldn't abort the whole run
- [ ] Run across your full database in dry-run mode first, then commit

### Exit Criteria
Running `main.py` processes your full Bands & Artists database end to end, with a log
showing which fields were updated, skipped, or failed.

---

## Phase 7 — Remaining Enrichers (Stretch)
**Goal:** Add the remaining data sources once the core pipeline is proven.
**Estimated effort:** 1–2 sessions per enricher

### Candidates
- [ ] **Discogs** — richer discography data, more reliable album counts
- [ ] **Wikidata** — homepage URLs, more reliable country of origin
- [ ] **Bandcamp** — semi-manual URL resolution (construct and verify URLs by convention)
- [ ] **Spotify** — additional genre tags, artist images, popularity scores

### Notes
Add these one at a time and test each in isolation before wiring into the pipeline.
Bandcamp is unlikely to be fully automatable — a "best guess URL + manual confirmation"
workflow may be the most realistic approach.

---

## Data Quality Notes (Running Log)
*Use this section to track known issues as you discover them — treating this like an
engineer's field notes rather than a polished document.*

- MusicBrainz genre/tag coverage is inconsistent; Last.fm tags are noisy but broader
- Fuzzy artist name matching will need tuning for artists with common names or name
  changes (e.g. bands that have rebranded)
- Album counts may differ between sources depending on whether singles, EPs, and
  compilations are included — decide on a definition early

---

## Dependencies Reference

| Library            | Purpose                          | Install                    |
|--------------------|----------------------------------|----------------------------|
| `musicbrainzngs`   | MusicBrainz API client           | `pip install musicbrainzngs` |
| `requests`         | HTTP for Last.fm, others         | `pip install requests`      |
| `notion-client`    | Notion API client                | `pip install notion-client` |
| `python-dotenv`    | Load `.env` config               | `pip install python-dotenv` |
| `discogs-client`   | Discogs API (Phase 7)            | `pip install discogs-client` |
| `spotipy`          | Spotify API (Phase 7)            | `pip install spotipy`       |