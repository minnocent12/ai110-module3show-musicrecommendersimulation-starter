from src.recommender import Song, UserProfile, Recommender, score_song, load_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# score_song tests
# ---------------------------------------------------------------------------

def make_song(genre="pop", mood="happy", energy=0.8) -> dict:
    """Helper that returns a minimal song dict for score_song()."""
    return {"genre": genre, "mood": mood, "energy": energy}


def test_score_song_perfect_match():
    """All three features match → maximum score of 4.5."""
    user  = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song  = make_song("pop", "happy", 0.8)
    score, reasons = score_song(user, song)
    assert score == 4.5
    assert any("genre match" in r for r in reasons)
    assert any("mood match"  in r for r in reasons)


def test_score_song_no_match():
    """No categorical matches and energy far away → score near 0."""
    user  = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song  = make_song("metal", "aggressive", 0.1)
    score, _ = score_song(user, song)
    assert score == 0.0


def test_score_song_genre_match_only():
    """Genre matches (+2.0), mood and energy miss → score between 2.0 and 3.0."""
    user  = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song  = make_song("pop", "chill", 0.1)   # energy far away → 0 pts
    score, _ = score_song(user, song)
    assert score == 2.0


def test_score_song_energy_proximity():
    """Energy within 0.5 earns partial credit; beyond 0.5 earns nothing."""
    user = {"genre": "jazz", "mood": "chill", "energy": 0.5}

    close_song = make_song("rock", "moody", 0.6)   # diff=0.10 → 0.80 pts
    far_song   = make_song("rock", "moody", 0.0)   # diff=0.50 → 0.00 pts

    close_score, _ = score_song(user, close_song)
    far_score,   _ = score_song(user, far_song)

    assert close_score > 0.0
    assert far_score   == 0.0


def test_score_song_reasons_always_has_three_entries():
    """score_song always returns exactly one reason per scoring step."""
    user  = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song  = make_song("rock", "chill", 0.5)
    _, reasons = score_song(user, song)
    assert len(reasons) == 3


# ---------------------------------------------------------------------------
# load_songs tests
# ---------------------------------------------------------------------------

def test_load_songs_returns_list():
    """load_songs should return a non-empty list from the real CSV."""
    songs = load_songs("data/songs.csv")
    assert isinstance(songs, list)
    assert len(songs) > 0


def test_load_songs_correct_types():
    """Numeric fields must be cast correctly; string fields must be strings."""
    songs = load_songs("data/songs.csv")
    song  = songs[0]

    assert isinstance(song["energy"],       float)
    assert isinstance(song["valence"],      float)
    assert isinstance(song["danceability"], float)
    assert isinstance(song["acousticness"], float)
    assert isinstance(song["tempo_bpm"],    int)
    assert isinstance(song["title"],        str)
    assert isinstance(song["genre"],        str)


def test_load_songs_genre_is_lowercase():
    """load_songs normalises genre and mood to lowercase."""
    songs = load_songs("data/songs.csv")
    for song in songs:
        assert song["genre"] == song["genre"].lower()
        assert song["mood"]  == song["mood"].lower()
