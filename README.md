# 🎵 Music Recommender Simulation

## Project Summary

In this project, I designed a simple content-based music recommender system that simulates how real-world platforms like Spotify or TikTok suggest content. The system represents both songs and user preferences as structured data and uses a weighted scoring rule to measure how well each song matches a user's taste. Songs are then ranked by score and the top results are returned as recommendations. The recommender works in two distinct stages: a **scoring rule** that evaluates each song individually against the user profile, and a **ranking rule** that sorts all scored songs and returns the top results — separate, independently improvable components that mirror how real platforms are built. This project highlights how recommendation systems transform raw input features into predictions while also exposing real limitations — including bias, filter bubbles, and lack of diversity.

---

## How The System Works

Real-world recommenders like Spotify and YouTube work by learning what a user enjoys — through both explicit signals (likes, skips, saves) and implicit ones (listen time, replay rate) — and then finding items that match that pattern. Large platforms typically blend two strategies: collaborative filtering (finding users with similar behavior and recommending what they liked) and content-based filtering (matching a song's audio attributes directly to a user's stated taste profile).

This simulation focuses exclusively on the content-based approach, which requires no data from other users. Instead of learning from behavior, it compares the audio and emotional attributes of each song against a user's preferences using a weighted proximity formula. Features that are close to the user's ideal earn a high score; features that are far earn a low one. The final recommendation is simply the songs with the highest total scores. Every score is traceable back to a specific feature match or mismatch, making the system fully interpretable — a deliberate design priority.

### `Song` Features

Each `Song` object stores the following attributes drawn from `data/songs.csv`:

| Feature | Type | Description |
|---|---|---|
| `id` | integer | Unique identifier |
| `title` | string | Song name |
| `artist` | string | Performing artist |
| `genre` | categorical | Style category: pop, lofi, rock, ambient, jazz, synthwave, indie pop |
| `mood` | categorical | Emotional tone: happy, chill, intense, relaxed, focused, moody |
| `energy` | float 0–1 | Perceived intensity — 0.0 is calm, 1.0 is driving |
| `valence` | float 0–1 | Musical positivity — 0.0 is dark/melancholic, 1.0 is euphoric |
| `danceability` | float 0–1 | Rhythmic suitability for dancing |
| `acousticness` | float 0–1 | Acoustic vs. electronic character |
| `tempo_bpm` | integer | Beats per minute (60–152); normalized to 0–1 before scoring |

### `UserProfile` Fields

A `UserProfile` stores the user's preferred values for the same scoreable features:

| Field | Type | Description |
|---|---|---|
| `preferred_genre` | categorical | The genre the user most wants to hear |
| `preferred_mood` | categorical | The emotional tone the user is seeking |
| `preferred_energy` | float 0–1 | Target energy level |
| `preferred_valence` | float 0–1 | Target positivity level |
| `preferred_danceability` | float 0–1 | Target danceability |
| `preferred_acousticness` | float 0–1 | Target acousticness |
| `preferred_tempo_bpm` | integer | Target tempo in BPM |

### Scoring Rule

Each song is scored against the user profile using a weighted sum of per-feature match scores.

Categorical features (`genre`, `mood`) use a binary match:

```
genre_score = 1.0  if song.genre == user.preferred_genre  else  0.0
mood_score  = 1.0  if song.mood  == user.preferred_mood   else  0.0
```

Numerical features use proximity scoring — rewarding closeness to the user's preference rather than higher or lower absolute values:

```
numeric_score = 1.0 - |song_value - user_preference|
```

Final weighted formula:

```
score = (genre_score    × 0.30)
      + (energy_score   × 0.25)
      + (mood_score     × 0.20)
      + (valence_score  × 0.15)
      + (dance_score    × 0.05)
      + (acoustic_score × 0.05)
```

Weights sum to 1.0, so every score falls between 0.0 and 1.0. Genre carries the highest weight because a genre mismatch is the most jarring possible recommendation. Energy is second because it determines listen context (workout vs. sleep). Mood and valence follow as emotional fine-tuning, with danceability and acousticness as supporting tie-breakers.

### Ranking Rule

After every song is scored independently, the `Recommender` sorts the full catalog by score in descending order and returns the top-N results (default: 3). Sorting and filtering are handled separately from scoring — adding post-filters like "exclude already-heard songs" or changing the number of results requires no changes to the scoring formula.

### Recommendation Pipeline

1. Load song catalog and user profile
2. For each song → apply scoring rule → produce score in [0.0, 1.0]
3. Sort all (song, score) pairs by score descending
4. Return top-N songs as recommendations

---


## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

