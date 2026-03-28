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

    # --- 2. Define user profiles ---
    # Each profile is a named dict so the header and experiments are readable.
    # Add or edit profiles here to test different listener archetypes.
    profiles = {
        "High-Energy Pop": {
            "genre":  "pop",
            "mood":   "happy",
            "energy": 0.9,
        },
        "Chill Lofi": {
            "genre":  "lofi",
            "mood":   "chill",
            "energy": 0.38,
        },
        "Deep Intense Rock": {
            "genre":  "rock",
            "mood":   "intense",
            "energy": 0.92,
        },
        "Late-Night Synthwave": {
            "genre":  "synthwave",
            "mood":   "moody",
            "energy": 0.75,
        },
        "Sunday Morning Jazz": {
            "genre":  "jazz",
            "mood":   "relaxed",
            "energy": 0.35,
        },

        # ------------------------------------------------------------------
        # Adversarial / edge-case profiles
        # Each one is designed to stress-test a specific assumption in the
        # scoring formula.  Run these and study the output to see whether
        # the results make sense.
        # ------------------------------------------------------------------

        # EDGE 1 — Mood that doesn't exist in the catalog.
        # Expected behavior: mood score is permanently 0 for every song,
        # so genre (+2.0) dominates and energy breaks all ties.
        # If genre is also absent the maximum possible score drops to 1.0.
        "Ghost Mood (mood not in catalog)": {
            "genre":  "pop",
            "mood":   "sad",        # no song in catalog has mood="sad"
            "energy": 0.8,
        },

        # EDGE 2 — Genre that doesn't exist in the catalog.
        # Expected behavior: genre score is permanently 0, max reachable
        # score is 2.5. Ranking flips: mood then energy decide the winner.
        "Genre Vacuum (genre not in catalog)": {
            "genre":  "k-pop",      # no song in catalog has genre="k-pop"
            "mood":   "happy",
            "energy": 0.8,
        },

        # EDGE 3 — Genre substring trap.
        # Catalog has "indie pop" but NOT "indie". Exact-match comparison
        # means zero genre points even though it feels like it should match.
        "Indie Substring Trap": {
            "genre":  "indie",      # "indie pop" ≠ "indie" — no match
            "mood":   "happy",
            "energy": 0.76,
        },

        # EDGE 4 — Conflicting mood + energy.
        # The only melancholic songs (Cathedral Light 0.22, Frozen Lake 0.19)
        # have energy far below 0.95.  Mood match awards +1.5 but energy diff
        # exceeds 0.5 so energy contribution = 0.  A high-energy non-melancholic
        # song can outscore a true melancholic match purely on energy proximity.
        "Sad Headbanger (mood vs energy conflict)": {
            "genre":  "classical",
            "mood":   "melancholic",
            "energy": 0.95,         # melancholic songs live at 0.19–0.22
        },

        # EDGE 5 — energy floor (0.0).
        # Formula: max(0, 1 − 2×diff). A song must have energy < 0.5 to earn
        # ANY energy points at all.  Only 6 catalog songs qualify; the rest score
        # exactly 0 on the energy axis, collapsing ranking to genre + mood.
        "Ultra Quiet (energy floor)": {
            "genre":  "ambient",
            "mood":   "melancholic",
            "energy": 0.0,          # pushes all songs above 0.5 to 0 energy pts
        },

        # EDGE 6 — energy ceiling (1.0).
        # Only Iron Tide (energy=0.97) is within 0.5 of the target and earns
        # meaningful energy points.  Tests whether a single song can dominate
        # if it happens to sit at the extreme of the scale.
        "Max Intensity (energy ceiling)": {
            "genre":  "metal",
            "mood":   "aggressive",
            "energy": 1.0,          # only Iron Tide (0.97) is close
        },
    }

    # --- 3. Run recommender for every profile ---
    for profile_name, user_prefs in profiles.items():

        # Section banner so profiles are easy to tell apart in the terminal
        print(f"\n{'=' * 48}")
        print(f"  Listener: {profile_name}")
        print(f"{'=' * 48}")

        # Session header (catalog size + profile values)
        print_header(user_prefs, len(songs))

        # Get top-K recommendations for this profile
        recommendations = recommend_songs(user_prefs, songs, k=TOP_K)

        if not recommendations:
            print("  No recommendations found.\n")
            continue

        print(f"  Top {len(recommendations)} recommendations\n")

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print_recommendation(rank, song, score, explanation)

        # Scoring legend once per profile so each block is self-contained
        print(f"\n  Scoring:  genre match +2.0  |  mood match +1.5  |  energy match up to +1.0")
        print(f"  Maximum possible score: {MAX_SCORE:.1f}\n")


if __name__ == "__main__":
    main()