from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

# Maximum score a song can receive from score_song()
# Genre(2.0) + Mood(1.5) + Energy(1.0) = 4.5
MAX_SCORE = 4.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(filepath: str) -> List[Dict]:
    """
    Read data/songs.csv and return a list of song dictionaries.

    Each dictionary has the same keys as the CSV header row.
    Numeric fields are cast to their correct Python types:
        float → energy, valence, danceability, acousticness
        int   → id, tempo_bpm
        str   → title, artist, genre, mood

    Rows with missing or un-parseable values are skipped with a warning
    so a single bad row never crashes the whole load.

    Args:
        filepath: Path to the CSV file (e.g. "data/songs.csv").

    Returns:
        A list of dicts, one per valid song row.
    """
    songs = []

    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # header row becomes dict keys automatically

        for row in reader:
            try:
                song = {
                    # --- integer fields ---
                    "id":           int(row["id"]),
                    "tempo_bpm":    int(row["tempo_bpm"]),

                    # --- float fields ---
                    "energy":       float(row["energy"]),
                    "valence":      float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),

                    # --- string fields (strip whitespace just in case) ---
                    "title":        row["title"].strip(),
                    "artist":       row["artist"].strip(),
                    "genre":        row["genre"].strip().lower(),
                    "mood":         row["mood"].strip().lower(),
                }
                songs.append(song)

            except (ValueError, KeyError) as e:
                # Skip the row but tell the developer which one failed and why
                print(f"[load_songs] Skipping malformed row {row}: {e}")

    return songs

def score_song(
    user_prefs: Dict,
    song: Dict,
) -> Tuple[float, List[str]]:
    """
    Score a single song against a user profile using the README recipe.

    Returns a tuple of:
        score   (float) — total additive points, 0.0 – 4.5
        reasons (list)  — one human-readable string per scoring step,
                          e.g. ["genre match (+2.0)", "mood mismatch (+0.0)",
                                "energy similarity: diff=0.02 (+0.96)"]

    Key lookup accepts both short keys ("genre", "mood", "energy") used by
    main.py and the full keys ("favorite_genre", "target_energy") used by
    the OOP interface.

    Algorithm (from README):
        Step 1 — genre match:  exact string compare  → 2.0 or 0.0
        Step 2 — mood match:   exact string compare  → 1.5 or 0.0
        Step 3 — energy score: max(0.0, 1.0 - 2 × |song.energy - target|)
    """
    reasons: List[str] = []
    total: float = 0.0

    # --- resolve preference values, supporting both key styles ---
    user_genre  = user_prefs.get("favorite_genre") or user_prefs.get("genre",  "")
    user_mood   = user_prefs.get("favorite_mood")  or user_prefs.get("mood",   "")
    # Use `is not None` so that energy=0.0 is treated as a valid value (0.0 is falsy)
    user_energy = (
        user_prefs["target_energy"]
        if user_prefs.get("target_energy") is not None
        else user_prefs.get("energy", 0.5)
    )

    # Step 1 — genre match (+2.0)
    if song["genre"] == user_genre:
        total += 2.0
        reasons.append("genre match (+2.0)")
    else:
        reasons.append(f"genre mismatch: {song['genre']} ≠ {user_genre} (+0.0)")

    # Step 2 — mood match (+1.5)
    if song["mood"] == user_mood:
        total += 1.5
        reasons.append("mood match (+1.5)")
    else:
        reasons.append(f"mood mismatch: {song['mood']} ≠ {user_mood} (+0.0)")

    # Step 3 — energy proximity (0.0 – 1.0)
    # Multiplying diff by 2 means the song must be within 0.5 of the
    # target to earn any points — a deliberate steep penalty (see README).
    diff       = abs(song["energy"] - user_energy)
    energy_pts = max(0.0, 1.0 - 2 * diff)
    total     += energy_pts
    reasons.append(
        f"energy similarity: |{song['energy']} − {user_energy}| = "
        f"{diff:.2f} → (+{energy_pts:.2f})"
    )

    return round(total, 4), reasons

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song in the catalog, rank by score, return the top-k.

    This function separates concerns into two distinct phases:
        1. Scoring — delegate to score_song() which judges each song independently
        2. Ranking — sort all scored songs and return the highest-rated ones

    This separation ensures that:
        - Changing the scoring formula never requires touching the ranking logic
        - Modifying k or adding filters never requires changing score_song()
        - The function remains testable and maintainable

    Args:
        user_prefs: Preference dictionary supporting both key styles:
                    - Short keys: "genre", "mood", "energy" (used by main.py)
                    - Full keys: "favorite_genre", "favorite_mood", "target_energy"
        songs: List of song dictionaries from load_songs() (each with keys:
               id, title, artist, genre, mood, energy, tempo_bpm, valence,
               danceability, acousticness)
        k: Number of top recommendations to return (default: 5). If k exceeds
           the number of songs, returns all scored songs.

    Returns:
        List of (song_dict, score, explanation) tuples, sorted by score
        descending (highest first). The explanation is a pipe-separated string
        summarizing each scoring component, e.g.:
        "genre match (+2.0) | mood mismatch: pop ≠ rock (+0.0) | energy similarity: |0.82 − 0.75| = 0.07 → (+0.86)"

    Example:
        >>> user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.75}
        >>> songs = load_songs("data/songs.csv")
        >>> recommendations = recommend_songs(user_prefs, songs, k=3)
        >>> for song, score, explanation in recommendations:
        ...     print(f"{song['title']}: {score:.2f} - {explanation}")
    """
    # Phase 1: Score every song independently
    # Using list comprehension to transform songs into (song, score, explanation)
    # The nested comprehension pattern ensures score_song() is called exactly once
    # per song and the results are unpacked cleanly.
    scored: List[Tuple[Dict, float, str]] = [
        (song, score, " | ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # Phase 2: Rank by score and return top-k
    # Sort in-place (more efficient than sorted() for local lists) by the score
    # at index 1 of each tuple, highest first. Using reverse=True is clearer
    # than key=lambda x: -x[1] and avoids potential floating-point precision issues.
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Slice to return exactly k results (or fewer if songs < k)
    # Python slicing gracefully handles k > len(scored) by returning the full list
    return scored[:k]