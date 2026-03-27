"""
Command-line runner for the Music Recommender Simulation.
Run with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs, MAX_SCORE

# ---------------------------------------------------------------------------
# Formatting constants — change here to restyle all output at once
# ---------------------------------------------------------------------------
DIVIDER  = "─" * 48
THIN_DIV = "·" * 48
TOP_K    = 5


def print_header(user_prefs: dict, total_songs: int) -> None:
    """Print the session header showing catalog size and active profile."""
    print(f"\n{DIVIDER}")
    print("  🎵  Music Recommender")
    print(DIVIDER)
    print(f"  Catalog : {total_songs} songs")
    print(f"  Profile : {user_prefs.get('genre', '—')} / "
          f"{user_prefs.get('mood', '—')} / "
          f"energy {user_prefs.get('energy', '—')}")
    print(f"{DIVIDER}\n")


def parse_reasons(explanation: str) -> list[str]:
    """
    Split an explanation string into individual reason lines.

    Handles the separators used across all versions of recommend_songs
    so this file stays compatible if the separator ever changes.

    Args:
        explanation: A joined string of per-step reasons.

    Returns:
        A list of individual reason strings.
    """
    for sep in (" | ", "; ", ", "):
        if sep in explanation:
            return explanation.split(sep)
    return [explanation]   # fallback: treat the whole string as one reason


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """
    Print one formatted recommendation card.

    Layout:
        ★   Song Title
            Artist Name
            Score: 4.46 / 4.5  ██████████  99%
            Why recommended:
              • reason one
              • reason two
              • reason three
        ················································
    """
    # Score bar: 10 blocks scaled to MAX_SCORE
    pct       = score / MAX_SCORE
    filled    = round(pct * 10)
    score_bar = "█" * filled + "░" * (10 - filled)

    # Top result gets a star badge; others get a numbered badge
    badge = "★ " if rank == 1 else f"#{rank}"

    print(f"  {badge}  {song['title']}")
    print(f"       {song.get('artist', 'Unknown artist')}")
    print(f"       Score: {score:.2f} / {MAX_SCORE:.1f}  {score_bar}  {pct * 100:.0f}%")

    print("       Why recommended:")
    for reason in parse_reasons(explanation):
        print(f"         • {reason}")

    print(f"  {THIN_DIV}")


def main() -> None:
    # --- 1. Load catalog ---
    songs = load_songs("data/songs.csv")

    if not songs:
        print("❌ No songs found in catalog. Please check data/songs.csv")
        return

    # --- 2. Define user profile ---
    user_prefs = {
        "genre":  "pop",
        "mood":   "happy",
        "energy": 0.8,
    }

    # --- 3. Print session header ---
    print_header(user_prefs, len(songs))

    # --- 4. Get recommendations (already sorted best-first by recommend_songs) ---
    recommendations = recommend_songs(user_prefs, songs, k=TOP_K)

    # --- 5. Guard: nothing to show ---
    if not recommendations:
        print("  No recommendations found. Check that songs.csv is loaded correctly.")
        return

    print(f"  Top {len(recommendations)} recommendations\n")

    # --- 6. Print each recommendation card ---
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)

    # --- 7. Scoring legend so the output is self-explanatory ---
    print(f"\n  Scoring:  genre match +2.0  |  mood match +1.5  |  energy match up to +1.0")
    print(f"  Maximum possible score: {MAX_SCORE:.1f}\n")


if __name__ == "__main__":
    main()