# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeMatch 1.0**

A rule-based music recommender that scores songs against a listener profile and returns the top five matches.

---

## 2. Intended Use

VibeMatch is designed for classroom exploration of how recommender systems work. It is not a production app.

It takes three things from a listener — their favorite genre, their preferred mood, and how energetic they want the music to feel — and uses those to rank songs from a small catalog. It assumes the listener can be described by a single genre, a single mood, and one energy level. It does not learn from feedback or adapt over time.

It should not be used to make real music recommendations for real users. The catalog is too small and the scoring is too simple to reflect the complexity of actual musical taste.

---

## 3. How the Model Works

The system scores every song in the catalog against the listener's profile, then returns the five highest-scoring songs.

Scoring works in three steps:

1. **Genre check.** If the song's genre exactly matches the listener's favorite genre, it earns 2 points. If not, it earns 0. There is no partial credit.
2. **Mood check.** If the song's mood exactly matches the listener's preferred mood, it earns 1.5 points. Again, exact match only.
3. **Energy check.** Energy is a number between 0 and 1 — think of 0 as nearly silent and 1 as extremely loud and intense. The closer the song's energy is to the listener's target, the more points it earns, up to a maximum of 1 point. A song whose energy is more than halfway away from the target earns nothing.

The maximum possible score is 4.5. A song that matches perfectly on all three signals hits that ceiling.

Note: the catalog also stores tempo, danceability, valence, and acousticness for each song — but the scoring formula does not use any of those fields. They are collected but ignored.

---

## 4. Data

The catalog contains 20 songs. Each song has a title, artist, genre, mood, energy level, tempo, valence, danceability, and acousticness.

Fourteen different genres are represented: pop, lofi, rock, ambient, jazz, synthwave, metal, reggae, country, classical, afrobeat, electronic, folk, hip hop, indie pop, and latin. Most genres appear only once. Lofi is the most represented with three songs; pop has two. Every other genre has exactly one song.

Nine moods appear across the catalog: happy, chill, intense, relaxed, moody, focused, melancholic, aggressive, euphoric, dark, nostalgic, and uplifting. No song is tagged "sad," "angry," "romantic," or many other moods a real listener might want.

The catalog skews toward mid-to-high energy. Thirteen of the twenty songs have energy above 0.6. Low-energy listeners have fewer songs that can earn full energy points.

No songs were added or removed from the original dataset.

---

## 5. Strengths

The system works well when the listener's profile closely matches a song in the catalog.

For the five "normal" profiles tested, the top recommendation was correct every time. A synthwave listener got a synthwave song. A jazz listener got the one jazz song. The scoring logic reliably surfaces a strong match when one exists.

The energy scoring also handles close calls well. Two lofi/chill songs scored nearly identically because their energy values were both very close to the target — the system correctly treated them as nearly tied rather than forcing an arbitrary winner.

The explanation output is also a genuine strength. Every recommendation comes with a clear breakdown of exactly why it ranked where it did. A listener can see whether a song ranked high because of genre, mood, energy, or some combination. That kind of transparency is rare even in real-world recommendation apps.

---

## 6. Limitations and Bias

**Binary exact-match scoring structurally disadvantages listeners of niche and blended genres.**

The system awards genre and mood points using exact string comparison — a song either matches perfectly or scores zero, with no middle ground. During testing, a user profile set to `indie` received no genre credit for any song in the catalog, because the only sonically similar song is tagged `indie pop`, which the system treats as completely unrelated. This means listeners whose preferred genre sits between catalog labels — such as indie, folk-rock, or lo-fi hip hop — are permanently capped at a lower maximum score than listeners whose exact genre label appears in the data, like `pop` or `lofi`. The bias compounds with catalog size: well-represented genres like lofi (3 songs) give the system multiple chances to find a match, while culturally specific genres like afrobeat, reggae, and latin each have only one representative, making a correct recommendation nearly guaranteed but diversity within that recommendation impossible. In practice, the system is less a neutral scorer and more a reflection of whatever genre labels the catalog curator chose to use.

---

## 7. Evaluation

**Profiles tested and what the results revealed.**

Eleven listener profiles were tested — five normal archetypes (High-Energy Pop, Chill Lofi, Deep Intense Rock, Late-Night Synthwave, Sunday Morning Jazz) and six edge cases designed to stress-test the scoring logic (a mood not in the catalog, a genre not in the catalog, an exact-match substring trap, conflicting mood and energy signals, and energy targets at both extremes: 0.0 and 1.0).

For the five normal profiles, the top result felt right every time. The system correctly identified the one song that matched all three signals and ranked it first. No surprises there.

The edge cases were more revealing. When a profile used a mood that no song in the catalog shared — for example, asking for "sad" music when no song is tagged sad — the mood signal quietly scored zero for every single song and the system never flagged that. It just kept going, ranked what it could, and returned confident-looking results that were actually just the best of a bad situation. A real listener would want to know "we couldn't find anything that matches your mood" rather than silently receiving songs that don't match at all.

A weight-shift experiment was also run: genre was halved (from 2.0 to 1.0 points) and energy was doubled (from 1.0 to 2.0 points). The #1 result did not change for any of the 11 profiles. Only the #2–#5 rankings shuffled. This confirmed that when one song clearly dominates all three signals, no weight adjustment changes who wins — the sensitivity only matters in the fallback rankings where partial matches compete.

**Why does "Gym Hero" keep showing up for people who just want Happy Pop?**

Imagine you are looking for a happy pop song and you ask a friend for recommendations. Your friend has 20 songs to choose from. There is one perfect match — Sunrise City, which is pop and happy. But your friend also notices that Gym Hero is a pop song with extremely high energy, even though it has an intense, workout vibe rather than a happy one. Because your friend is scoring songs by three separate checkboxes — genre, mood, energy — Gym Hero gets a check for genre (it's pop) and a near-perfect check for energy (it's very loud, close to what you asked for). It only misses on mood. So it finishes second, even though anyone who actually listened to it would say it doesn't fit what you asked for.

That is exactly what the system does. It doesn't understand that "intense pop" and "happy pop" feel completely different to a listener. It only sees that two of the three boxes were checked. The more the catalog skews toward high-energy pop songs, the more often Gym Hero will appear — not because it is a good recommendation, but because the scoring formula has no way to say "this mood mismatch matters more than the genre match."

---

## 8. Ideas for Improvement

**1. Add partial credit for related genres and moods.**
Instead of zero points for any mismatch, the system could give partial credit for close relationships — for example, `indie pop` gets 0.5 genre points when the listener asks for `indie`, or `chill` gets 0.5 mood points when the listener asks for `relaxed`. This would fix the substring trap and make fallback rankings feel less arbitrary.

**2. Use the features the system already collects but ignores.**
The catalog stores valence, danceability, acousticness, and tempo for every song. None of these affect the score. Adding even one of these — acousticness, for example — would let the system distinguish between two songs with identical genre, mood, and energy but completely different feels. This is low-effort and high-impact since the data is already there.

**3. Add a "no match found" warning.**
When no song in the catalog matches the listener's mood or genre, the system should say so explicitly rather than silently returning the least-bad results. A simple check at the start — "does any song share this mood?" — would make the output more honest and much easier to trust.

---

## 9. Personal Reflection

Building this recommender made it clear how much a system's behavior is shaped by decisions that feel small at the time — like whether to use exact string matching or how many songs to include per genre. The system felt fair until we ran edge cases, and then it became obvious that "fair" had quietly been defined as "works well if your taste matches what the catalog already contains."

The most unexpected discovery was that changing the weights didn't change the top result for any profile. It felt like weight tuning should matter a lot, but in a 20-song catalog, the winner is usually predetermined — one song fits better than everything else, and no amount of rebalancing changes that. Weight sensitivity is a large-catalog problem.

This changed how I think about apps like Spotify, Apple Music, TikTok, and YouTube. When they recommend something surprisingly good, it's probably not because their algorithm is smarter — it's because they have millions of songs and enough diversity to make the scoring actually matter. A recommender is only as good as the variety in the data it searches.
