# JapJap Project State

## Current Phase

Phase 13 — Kanji + N5 Grammar Expansion (complete)

## Completed

- Phase 0: Open-source foundation, dev environment, CI/CD, testing infrastructure, docs.
- Phase 1: Authentication — registration, login, logout, JWT, protected routes, auth state.
- Phase 2: Onboarding — learning goals, experience, preferred level, JLPT target, editable profile, unrestricted level changes.
- Phase 3: Core Learning — vocabulary, grammar, flashcards, multiple choice, sentence completion, XP.
- Phase 4: Test Engine — test creation, questions, attempts, scoring, result page, history.
- Phase 5: Learner Model + Progress — skill mastery, progress dashboard, mistakes, activity history, estimated JLPT readiness.
- Phase 6: Gemini AI Tutor — AIService → GeminiService, grammar/vocabulary/mistake explanations, structured + Pydantic-validated, mocked in all tests.
- Phase 7: AI Content Generation — supplementary AI-generated vocabulary/grammar questions, mini stories, comprehension questions; all validated and stored.
- Phase 8: Text Conversation — roleplay conversation sessions with AI characters across 3 scenarios (ramen shop, convenience store, train station), full history threading for scenario consistency, conversation history view.
- Phase 9: Speech-to-Text — `SpeechToTextService` abstraction (`GeminiSTTProvider` implementation), pronunciation practice against 9 curated target phrases (N5–N1), browser microphone recording, similarity-based scoring, first real data source for the `speaking` learner-model category.
- Phase 10: Adaptive Recommendations — deterministic "what to practice next" engine reading the learner model, surfaced as a "Recommended for you" panel on the dashboard; closes the `Learning → Practice → Assessment → Learner Model → Weakness Detection → Adaptive Recommendation` loop from [ARCHITECTURE.md](ARCHITECTURE.md).
- Phase 11: Achievements — a 10-badge gamification catalog seeded into MongoDB (unlike Phase 8/9's in-code content), deterministic milestone detection across XP/activity/mastery/category-breadth, idempotent unlock-on-read with a stable `unlocked_at`, dedicated Achievements page.
- Phase 12: Spaced Repetition — SM-2-inspired per-concept scheduling (`review_schedule` collection) for vocabulary, grammar, and speaking; quizzes and the flashcard deck now surface due/never-seen concepts first instead of re-serving whatever was just answered correctly, so a learner stops seeing the same well-known items on repeat.
- Phase 13: Kanji + N5 Grammar Expansion — a full new Kanji practice category (80 real N5 kanji, quiz + flashcards, fully integrated into the learner model/recommendations/achievements/spaced-repetition) plus N5 grammar grown from 8 to 38 real, verified points, both researched from authoritative community-compiled JLPT scope references (not copied exam content — see this phase's section below for the copyright distinction).

## Frontend

- React + TypeScript + Vite (`frontend/`), Tailwind CSS v4, React Router,
  TanStack Query, Zustand (auth only).
- `src/services/aiGenerationApi.ts`, `src/types/aiGeneration.ts` — client
  for the five new `/api/ai/generate/*` and `/api/ai/generated-questions/*`
  and `/api/ai/mini-stories/*` endpoints.
- New pages: `AIPracticePage` (`/ai-practice` — pick category + any JLPT
  level N5–N1, generate a single question on demand, answer it, get scored;
  unlike other practice pages this one lets the learner pick *any* level
  since generation doesn't depend on pre-seeded content) and
  `MiniStoriesPage` (`/mini-stories` — pick a level and optional topic,
  generate a story with reading comprehension questions answered one form,
  submitted together).
- Dashboard's practice grid grew to 6 tiles (3×2): Flashcards, Quiz, Tests,
  Progress, AI Practice, Mini Stories.
- Test tooling: Vitest + RTL, 34 tests total (added
  `AIPracticePage.test.tsx`, `MiniStoriesPage.test.tsx`).

### Phase 8 additions

- `src/services/conversationApi.ts`, `src/types/conversation.ts` — client
  for the five `/api/conversation/*` endpoints.
- New pages: `ConversationScenariosPage` (`/conversation` — pick a JLPT
  level and one of 3 scenarios, starts a session and navigates to it),
  `ConversationChatPage` (`/conversation/:sessionId` — chat-bubble UI,
  send a message, see the character's reply and translation, XP earned),
  `ConversationHistoryPage` (`/conversation/history` — past sessions,
  newest-activity-first, links back into each one).
- Dashboard's practice grid grew to 7 tiles: added Conversation (💬).
- Test tooling: Vitest + RTL, 41 tests total (added
  `ConversationScenariosPage.test.tsx`, `ConversationChatPage.test.tsx`,
  `ConversationHistoryPage.test.tsx`).

### Phase 9 additions

- `src/hooks/useAudioRecorder.ts` — wraps `navigator.mediaDevices.getUserMedia`
  + `MediaRecorder` behind a small `{ status, audioBlob, start, stop, reset }`
  interface (`status` is `idle | recording | stopped | unsupported | denied`)
  so pages don't touch browser recording APIs directly, and so page-level
  tests can mock the hook instead of the whole Web Audio/MediaRecorder stack.
- `src/services/speechApi.ts`, `src/types/speech.ts` — client for the three
  `/api/speech/*` endpoints; `submitSpeakingAttempt` uploads the recorded
  audio as `multipart/form-data`, unlike every other API call so far which
  is JSON.
- New pages: `SpeakingPracticePage` (`/speaking` — pick a JLPT level, pick a
  target phrase, record, submit, see the transcript/match%/XP),
  `SpeakingHistoryPage` (`/speaking/history` — past attempts).
- Dashboard's practice grid grew to 8 tiles: added Speaking (🎤).
- Test tooling: Vitest + RTL, 51 tests total (added
  `useAudioRecorder.test.ts` — mocks `MediaRecorder`/`getUserMedia` globally
  to test the actual recording state machine — plus
  `SpeakingPracticePage.test.tsx` and `SpeakingHistoryPage.test.tsx`, which
  mock the hook itself rather than the browser APIs it wraps).

### Phase 10 additions

- `src/services/recommendationsApi.ts`, `src/types/recommendations.ts` —
  client for `GET /api/recommendations`.
- No new page — recommendations surface as a "Recommended for you" panel
  on `DashboardPage` itself (between the XP badge and the practice tile
  grid), since "what should I do next" belongs at the point where a
  learner is already deciding what to practice, not behind another click.
- Test tooling: Vitest + RTL, 53 tests total (added two `DashboardPage`
  cases: the panel renders a recommendation with a working action link,
  and it renders nothing when there's nothing to recommend).

### Phase 11 additions

- `src/services/achievementsApi.ts`, `src/types/achievements.ts` — client
  for `GET /api/achievements`.
- New page: `AchievementsPage` (`/achievements` — a grid of all 10
  badges, locked ones grayed out, unlocked ones highlighted with their
  unlock date). Unlike recommendations, achievements get their own page —
  a badge collection is something a learner browses deliberately, not a
  landing-moment nudge.
- Dashboard's practice grid grew to 9 tiles: added Achievements (🏅).
- Test tooling: Vitest + RTL, 54 tests total (added
  `AchievementsPage.test.tsx`: unlocked count, per-badge rendering,
  locked vs. unlocked distinction).

### Phase 12 additions

- `src/services/activityApi.ts` gained `fetchFlashcardDeck` — calls the new
  `GET /api/activities/flashcards` endpoint instead of the plain
  `GET /api/vocabulary`/`GET /api/grammar` content endpoints.
- `FlashcardsPage` now studies the SRS-ordered deck (due/never-seen items
  first) instead of the raw, unordered content list — same page, no new
  route, since "smarter ordering" doesn't change what the feature *is*.
- Added a small progress bar under the card counter (Card N of M) —
  the first of the promised "more illustration/immersion" touches, folded
  into each phase's UI work rather than done as one separate pass.
- No changes needed to `QuizPage` — `GET /api/activities/quiz` already
  used the same client function, so making the backend SRS-aware there
  was transparent to the frontend.

### Phase 13 additions

- `ActivityCategory` (frontend) gained `'kanji'`; a new `KanjiItem` type
  mirrors the backend schema. `activityApi.ts` gained `fetchKanji`.
- `QuizPage` and `FlashcardsPage` both grew a third "Kanji" tab, reusing
  every existing quiz/flashcard/XP/AI-Tutor code path — no new page, no
  new route. `FlashcardsPage` gained a kanji-specific card face (large
  character, then on reveal: meaning, onyomi/kunyomi readings, and an
  example word) via a new `isKanjiItem` type guard alongside the existing
  `isVocabItem` one.
- No dashboard tile or dedicated `/kanji` page — kanji is reached through
  the same Flashcards/Quiz tiles vocabulary and grammar already use, same
  "third category, not a new feature" framing as the backend.
- `ProgressPage`, the Dashboard's recommendations panel, and
  `AchievementsPage` needed **zero** frontend changes — all three already
  render whatever categories the backend returns/labels
  (`CATEGORY_LABELS` already had a `kanji` entry since Phase 5's original
  scaffolding), so kanji mastery, recommendations, and achievement
  progress just started showing up once the backend had real data for it.

## Backend

- `app/schemas/ai_generation.py` — `GeneratedQuestion` and
  `GeneratedMiniStory` (with nested `ComprehensionQuestion`s), each with a
  `model_validator` enforcing the *business* rules Pydantic's field types
  alone can't (`_validate_multiple_choice`: exactly 4 unique options, the
  correct answer among them) — this is the "business validation" step in
  the Gemini → structured output → Pydantic validation → business
  validation → database pipeline from [AI.md](AI.md), not skippable
  shape-checking.
- `app/ai/base.py` / `gemini_service.py` — three new `AIService` methods:
  `generate_vocabulary_question`, `generate_grammar_question`,
  `generate_mini_story` (the last generates the story *and* its
  comprehension questions in one Gemini call — cheaper, and keeps questions
  grounded in the actual story text).
- `app/services/content_generation_service.py::ContentGenerationService` —
  orchestrates generation → storage → `ai_interactions` logging, and
  scoring (`submit_generated_question`, `submit_comprehension`) using the
  same deterministic re-check-against-stored-content pattern as Phases 3–4
  (Gemini is never asked to grade an answer).
- `app/api/ai_generation.py` — `POST /api/ai/generate/{vocabulary,grammar}-question`,
  `POST /api/ai/generate/mini-story`,
  `POST /api/ai/generated-questions/{id}/submit`,
  `POST /api/ai/mini-stories/{id}/comprehension/submit`. Generation itself
  needs no onboarding (browsing/generating content is free, like
  `GET /api/vocabulary`); only submitting an answer (which earns XP)
  requires it, and only submitting a mini-story's comprehension additionally
  enforces ownership (404, not 403, for someone else's story — same pattern
  as Phase 4's test attempts).
- Generated vocabulary/grammar questions are stored in the *existing*
  `questions` collection (Phase 4), tagged `source: "ai_generated"` — no new
  collection needed, and they're structurally reusable by a future Test if
  a later phase wants that. Mini stories get their own `mini_stories`
  collection since their comprehension questions are story-specific, not
  reusable content.
- **Comprehension answers now feed the `reading` category in the learner
  model** — the first real data source for `reading` since Phase 5
  introduced the category with permanently `has_data: false`.
- Test tooling: pytest, 93 tests total (added `test_ai_generation.py`:
  generation stores content and hides the answer, both submit endpoints
  score correctly and award/withhold XP correctly, ownership enforcement on
  mini-story submission, `reading`/`vocabulary` skill feed-through, and the
  same 502/503 patterns as Phase 6; extended `test_gemini_service.py` with
  business-validation-rejection cases: too few options, duplicate options,
  correct answer missing from options).

### Phase 8 additions

- `app/core/conversation_data.py` — static roster of characters and
  scenarios (see [AI.md](AI.md)); `app/schemas/conversation.py` — request/
  response schemas plus `ConversationReply` (Gemini's per-turn structured
  output).
- `app/ai/base.py` / `gemini_service.py` — new `continue_conversation`
  method: builds a prompt from the character's personality, the scenario,
  the learner's JLPT level, and the full replayed history, then validates
  Gemini's JSON reply the same way as every other `AIService` method.
- `app/repositories/conversation_repository.py` —
  `ConversationSessionRepository` / `ConversationMessageRepository`.
- `app/services/conversation_service.py::ConversationService` — starts
  sessions (static opening line, no Gemini call), sends messages
  (reconstructs history → calls Gemini → persists both turns → awards
  XP), lists/fetches sessions with ownership checks. Persists the
  learner's message only *after* the AI reply succeeds — see
  [DATABASE.md](DATABASE.md) for why persisting it first would corrupt
  future history.
- `app/api/conversation.py` — `GET /api/conversation/scenarios`,
  `POST /api/conversation/sessions`, `GET /api/conversation/sessions`,
  `GET /api/conversation/sessions/{id}`,
  `POST /api/conversation/sessions/{id}/messages`. Scenario/session
  browsing needs no onboarding; starting a session and sending a message
  do (XP-earning), matching the established pattern.
- 3 XP per message sent — lower than quiz/test XP (10) since there's no
  correct/incorrect answer to verify; conversation is deliberately **not**
  written to `learner_skills` (see [AI.md](AI.md)'s "What Gemini Is (and
  Isn't) Used For").
- Test tooling: pytest, 108 tests total (added `test_conversation.py`:
  scenario listing, session start/opening-line correctness, message
  send + XP award, per-scenario character correctness, **history
  accumulation across turns** — the scenario-consistency test — ownership
  checks, and the 404/502 error paths).

### Phase 9 additions

- `app/speech/base.py` — new `SpeechToTextService` ABC (mirrors
  `AIService`, deliberately a separate hierarchy — see
  [ARCHITECTURE.md](ARCHITECTURE.md)'s Speech Abstraction) + `SpeechServiceError`.
  `app/speech/gemini_provider.py::GeminiSTTProvider` implements it by
  sending the uploaded audio bytes to Gemini 2.0 Flash (which accepts audio
  input directly) and parsing a `{"transcript": "..."}` JSON response the
  same Gemini → JSON → Pydantic-validate way as every other Gemini call in
  the app — no new AI vendor/SDK needed for speech.
- `app/core/speaking_data.py` — 9 curated target phrases (4×N5, 2×N4,
  1×N3, 1×N2, 1×N1), static in code for the same reason as Phase 8's
  `conversation_data.py`: a phrase and its "correct" target text can never
  drift apart.
- `app/repositories/speaking_repository.py::SpeakingAttemptRepository` +
  `app/services/speaking_service.py::SpeakingService` — transcribes the
  upload, normalizes and compares it to the target phrase via
  `difflib.SequenceMatcher` (similarity ≥ 0.8 counts as correct — tolerant
  of STT noise, not an exact-match requirement), persists the attempt only
  after transcription succeeds (same failure-ordering lesson learned in
  Phase 8), feeds `learner_skills` with `category: "speaking"`, and awards
  a flat 10 XP for a correct attempt (matches quiz/test XP — unlike
  conversation, pronunciation *does* have a correct-answer check).
- `app/api/speech.py` — `GET /api/speech/prompts`, `GET /api/speech/attempts`,
  `POST /api/speech/attempts` (multipart upload: `audio` file + `prompt_key`
  form field; validates content-type against an allowlist and a 5 MB size
  cap before ever calling the speech provider). Prompt/attempt browsing
  needs no onboarding; submitting an attempt (XP-earning) does.
- New `Settings.stt_api_key`/`stt_enabled` (already scaffolded since
  Phase 0) now actually gates `get_stt_service` — configured independently
  of `GEMINI_API_KEY`, even though the default provider happens to also
  call Gemini under the hood.
- Added `python-multipart` dependency (required by FastAPI's
  `UploadFile`/`Form` — nothing before Phase 9 needed file uploads).
- Test tooling: pytest, 121 tests total (added `test_speech.py`: prompt
  listing/level-filtering, onboarding requirement, correct/incorrect
  scoring, punctuation-tolerant matching, unknown-prompt 404, unsupported-
  format 422, 502/503 provider-failure paths, and the `speaking` skill
  feed-through).

### Phase 10 additions

- `app/services/recommendation_service.py::RecommendationService` — pure
  deterministic logic, no AI/Gemini call at all (matches
  [ARCHITECTURE.md](ARCHITECTURE.md)'s "deterministic ranking always lives
  in backend logic" rule). Reads `learner_skills` (already computed by
  every prior phase's scoring) plus `conversation_sessions` (since
  conversation deliberately never writes to `learner_skills`, see Phase 8)
  and produces at most one recommendation per practiceable category
  (`vocabulary`, `grammar`, `reading`, `speaking`, `conversation` — `kanji`
  and `listening` are excluded, since neither has an implemented practice
  route to link to yet): `"weak_mastery"` if a category has ≥3 combined
  attempts and mastery < 70%, `"try_something_new"` if it's never been
  attempted at all, or nothing if it's already in good shape. Falls back
  to a single `"challenge"` recommendation (pointing at `/tests`) when
  every category looks solid, so the endpoint never returns an empty list
  with nothing actionable.
- `app/schemas/recommendations.py` — `RecommendationEntry`
  (`category`/`reason`/`message`/`mastery`/`action_label`/`action_path`)
  and `RecommendationsResponse`.
- `app/api/recommendations.py` — `GET /api/recommendations`. No onboarding
  required (matches `/api/progress`/`/api/mistakes` — a brand-new learner
  with no profile yet still gets useful "try something new" nudges for
  every category).
- No new collection — recommendations are computed fresh on every request
  from existing data, the same "never store what can be computed live"
  principle used for mastery/progress/mistakes throughout the learner
  model (Phase 5).
- Test tooling: pytest, 127 tests total (added `test_recommendations.py`:
  untried nudges for a brand-new learner, weak-mastery detection sorted
  ahead of untried nudges, the too-few-attempts edge case correctly
  produces no recommendation, conversation correctly treated as "tried"
  once a session exists, and the challenge fallback when every category
  looks solid).

### Phase 11 additions

- `app/core/achievement_seed_data.py::ACHIEVEMENTS` — the 10-badge catalog
  (key/name/description/emoji), seeded into the `achievements` collection
  at startup the same way Phase 3's `VOCABULARY_N5`/`GRAMMAR_N5` are —
  unlike Phase 8/9's characters/scenarios/speaking prompts, this content
  is *listed* as a catalog (not referenced by key inside an AI prompt), so
  it follows the vocabulary/grammar seeding precedent instead.
- `app/repositories/achievement_repository.py` —
  `AchievementRepository` (the read-only, seeded catalog) and
  `UserAchievementRepository` (per-user unlock records; `unlock()` is an
  idempotent `$setOnInsert` upsert on `(user_id, achievement_key)`, so an
  already-unlocked achievement's `unlocked_at` never shifts on a later
  recheck).
- `app/services/achievement_service.py::AchievementService` — entirely
  deterministic, no Gemini call (same rule as Phase 10's
  `RecommendationService`). Gathers XP (profile), activity/test/
  conversation/speaking counts (new `count_by_user` methods added to
  `ActivityRepository`, `TestAttemptRepository`,
  `ConversationSessionRepository`, `SpeakingAttemptRepository`), and
  per-category mastery (`learner_skills`) — then evaluates all 10
  criteria and unlocks (persists) any newly-met one at that moment, with a
  stable timestamp.
- `app/api/achievements.py` — `GET /api/achievements`. No onboarding
  required (a profile-less user just sees everything locked, matching the
  `/api/progress`/`/api/recommendations` pattern).
- The 10 achievements: `first_steps` (first quiz/flashcard/test),
  `century_club`/`high_scorer`/`xp_master` (100/500/1000 XP),
  `chatterbox` (first conversation), `speaker` (first speaking attempt),
  `bookworm` (first reading comprehension), `well_rounded` (tried all 5
  practiceable categories), `perfectionist` (≥90% mastery in a category
  with ≥5 attempts), `test_taker` (5 completed tests).
- Test tooling: pytest, 137 tests total (added `test_achievements.py`:
  full-catalog-locked for a new learner, `first_steps`/XP-milestone/
  `chatterbox`/`well_rounded`/`perfectionist`/`test_taker` unlock
  conditions (including the too-few-attempts edge case for
  `perfectionist`), and `unlocked_at` staying stable across repeated
  requests).

### Phase 12 additions

- `app/repositories/review_schedule_repository.py::ReviewScheduleRepository` —
  SM-2-inspired spaced repetition, adapted for this app's binary
  correct/incorrect grading (no 0-5 recall-quality scale exists anywhere
  in JapJap, unlike Anki). `record_review()`: correct answers grow the
  interval (1 day → 6 days → interval × ease factor, ease factor nudged
  up), an incorrect answer resets repetitions to 0, shortens the interval
  back to 1 day, and nudges ease factor down (floored at 1.3). This is a
  scheduling signal only — entirely separate from `learner_skills`'
  mastery tracking (Phase 5); both update from the same answer event but
  answer different questions ("how well" vs. "when next").
- `ActivityService._rank_by_due_date` — shared by `generate_quiz` (now
  takes `user_id`) and the new `get_flashcard_deck`: shuffles the content
  pool, then stable-sorts by due date ascending (never-reviewed concepts
  sort first, via a sentinel `UNSEEN_SORT_KEY = datetime.min`). `generate_quiz`
  takes a prefix slice of the ranked pool (so some content simply won't be
  selected if the pool is bigger than the requested quiz size — the
  "repeat avoidance" the user asked for); `get_flashcard_deck` returns the
  *entire* reordered deck, since flashcard mode is meant to review
  everything, just smarter-ordered.
- New `GET /api/activities/flashcards?category=&level=` — same content as
  `GET /api/vocabulary`/`GET /api/grammar`, personalized order. Those
  plain content endpoints deliberately stay unordered/unpersonalized;
  this one is the study-queue equivalent (same "quiz has its own endpoint,
  raw content has its own" split already established in Phase 3/4).
- `record_review` calls added alongside every existing `record_result`
  call site: `ActivityService.submit_quiz`/`complete_flashcards`,
  `TestService.submit_attempt`, `SpeakingService.submit_attempt`. Scope
  deliberately excludes reading (mini-story comprehension — a story's
  concept is a one-off title, not a reusable pool to reorder) and
  conversation (never had a "concept" to schedule in the first place, see
  Phase 8) — SRS applies specifically to the three *fixed content pools*
  a learner draws from repeatedly: vocabulary, grammar, and speaking
  prompts.
- Speaking prompt *list ordering* (`GET /api/speech/prompts`) was left
  unchanged — review data is still recorded on every speaking attempt for
  future use, but the prompt picker is a manual "choose one to practice"
  UI, not an auto-generated set the way quiz/flashcards are, so the
  "don't repeat what you already answered" problem doesn't really apply
  there the same way.
- Test tooling: pytest, 147 tests total (added `test_review_schedule.py`:
  interval progression across 1st/2nd/3rd+ correct answers, the
  incorrect-answer reset, the ease-factor floor, and never-reviewed
  concepts being absent from `due_dates_by_concept`; extended
  `test_activities.py` with the new flashcard-deck endpoint and two
  ordering tests — a never-reviewed concept beats recently-correct ones in
  a size-limited quiz, and a freshly-reviewed item sorts to the back of
  the full flashcard deck).

### Phase 13 additions

- **Sourcing note** (see this phase's Important Decisions for the full
  reasoning): the *scope* of what's tested at each JLPT level — which
  kanji, which vocabulary, which grammar points — is publicly documented
  reference information compiled by the JLPT study community (the Japan
  Foundation/JEES stopped publishing official lists after 2010), not
  copyrighted exam content. This phase researched that scope (via web
  search) and used it to write **original** content — every explanation,
  example sentence, and example word below is composed for this app, none
  copied from any textbook, app, or past exam.
- `app/core/kanji_seed_data.py::KANJI_N5` — 80 real N5 kanji (character,
  onyomi, kunyomi, meaning, plus an original example word/reading/meaning
  each), seeded into a new `kanji` collection the same
  seed-from-code-into-Mongo way as Phase 3's vocabulary/grammar (unlike
  Phase 8/9's characters/scenarios/speaking prompts, which stayed
  purely in-code — kanji is a browsable *catalog*, matching vocabulary's
  precedent, not content referenced by key inside an AI prompt).
- `app/core/seed_data.py::GRAMMAR_N5` grown from 8 to 38 points — every
  new entry hand-verified for correct conjugation and a unique `answer`
  string (no two grammar points share an exact answer text, so quiz
  distractor options are never accidentally duplicated).
- **Kanji is now a full third `ActivityCategory`** (`app/schemas/activity.py`),
  not a bolted-on special case: `app/repositories/kanji_repository.py::KanjiRepository`
  mirrors `VocabularyRepository` exactly; `ActivityService._content_repo`
  became a dict-based dispatch across all three repositories;
  `_QUIZ_FIELDS`/`_ACTIVITY_TYPE_FOR_QUIZ`/`_CONCEPT_FIELDS` gained kanji
  entries (`character` → `meaning`, multiple-choice, same shape as
  vocabulary's `term` → `meaning`). New `GET /api/kanji` route mirrors
  `GET /api/vocabulary`/`GET /api/grammar`.
- Kanji was added to `RecommendationService.CATEGORIES_SCORED_BY_MASTERY`/
  `CATEGORY_ACTIONS` (Phase 10) and `AchievementService.WELL_ROUNDED_CATEGORIES`
  (Phase 11) — both were designed to key off `learner_skills`' category
  field generically, so adding kanji as a real practice category meant
  updating these two constants, not the underlying logic.
  `AchievementService`'s `perfectionist` check needed **no** change at
  all — it already iterates whatever categories appear in
  `learner_skills`, so kanji mastery started counting toward it
  automatically the moment kanji quizzes existed.
- The Test Engine (Phase 4) deliberately was **not** extended to kanji —
  `TestCategory` is a separate enum from `ActivityCategory`, and adding a
  kanji test would mean touching `TestService`/`seed_test_engine`/the test
  schemas for comparatively little benefit versus quiz+flashcards, which
  already cover the same "practice this category" need. Scope boundary,
  not an oversight.
- Test tooling: pytest, 152 tests total (added kanji listing, kanji quiz
  generation/submission/skill-feed, and kanji flashcard-deck tests to
  `test_activities.py`; updated Phase 10/11 tests that had hardcoded the
  old 5-category assumption now that kanji is a 6th).

## Database

- Added `mini_stories` (indexed on `level`, `generated_by_user_id`).
  `questions` (Phase 4) gained an optional `source` field
  (`"ai_generated"` vs absent-for-seeded) — no schema migration needed since
  MongoDB is schemaless and existing seeded documents are simply treated as
  "not AI-generated" by omission. See [DATABASE.md](DATABASE.md).
- Tests clean `mini_stories` fully and `questions` filtered to
  `source: "ai_generated"` between tests (seeded questions stay, matching
  the existing shared-reference-content pattern).
- Added `conversation_sessions` (indexed on `user_id`) and
  `conversation_messages` (indexed on `session_id`). Tests clean both
  fully between runs. See [DATABASE.md](DATABASE.md).
- Added `speaking_attempts` (indexed on `user_id`). Tests clean it fully
  between runs. See [DATABASE.md](DATABASE.md).
- Added `achievements` (the seeded catalog, indexed unique on `key` — not
  cleared between tests, matching the vocabulary/grammar shared-reference-
  content pattern) and `user_achievements` (per-user unlocks, indexed
  unique on `(user_id, achievement_key)` — cleared between tests). See
  [DATABASE.md](DATABASE.md).
- Added `review_schedule` (per-user spaced-repetition state, unique index
  on `(user_id, category, concept)`). Tests clean it fully between runs.
  See [DATABASE.md](DATABASE.md).
- Added `kanji` (80 seeded N5 items, indexed on `level` — shared reference
  content like vocabulary/grammar, not cleared between tests). See
  [DATABASE.md](DATABASE.md).

## AI

- Extended — see [AI.md](AI.md) for the full Phase 6–8 pipeline, storage
  design, conversation-consistency approach, and privacy notes.

## Speech

- Implemented (Phase 9) — see [ARCHITECTURE.md](ARCHITECTURE.md)'s Speech
  Abstraction and [AI.md](AI.md)'s Phase 9 section for the
  `SpeechToTextService` → `GeminiSTTProvider` pipeline, scoring approach,
  and testing notes.

## Testing

- Backend: pytest, 152 tests passing (health, config, auth, profile,
  activities (vocabulary/grammar/kanji), test engine, learner model/progress,
  AI tutor, AI content generation, conversation, speech, recommendations,
  achievements, review scheduling).
- Frontend: Vitest + React Testing Library, 55 tests passing.
- E2E (Playwright or similar): not yet set up — planned for a later phase.
- **Manually verified against the real Gemini API** (same non-functional
  local key as Phases 6–7): registered a user, completed onboarding,
  started a Ramen Shop conversation with Momo (confirmed the correct
  static opening line and character), and sent a message — confirmed the
  request genuinely reaches Gemini (visible in the backend log as a real
  502 from the provider, not an instant mock response) and the learner
  sees the same friendly retry message pattern established in Phase 6.
  This manual run also caught a real bug — the learner's message was being
  persisted *before* the Gemini call, so a failed reply left a dangling,
  unanswered turn in the database that would have corrupted the next
  prompt's history — fixed by reordering `ConversationService.send_message`
  to persist only after the reply succeeds (verified in the same manual
  session: a second failed send left the message count unchanged).
- **Phase 9 manually verified end-to-end**, working around the sandboxed
  browser's blocked microphone access: logged in, browsed `/speaking`,
  confirmed the 9 target phrases and level filtering render correctly, and
  confirmed the recording UI's `denied` path renders correctly when the
  browser blocks `getUserMedia` (a real permission-denial path, not a
  mock). Since real microphone audio couldn't be captured in this sandbox,
  the actual `POST /api/speech/attempts` upload-and-transcribe flow was
  exercised directly over HTTP with a synthetic audio file — confirmed the
  request genuinely reaches Gemini (visible in the backend log as a real
  502 from the invalid local key) and, per the design, that no
  `speaking_attempts` document is written when transcription fails (`GET
  /api/speech/attempts` stayed empty afterward).
- **Phase 10 manually verified end-to-end against real data**: logged in
  as the same account used across Phases 8–9 (which already had a
  conversation session, but no vocabulary/grammar/reading/speaking
  activity), confirmed the dashboard's "Recommended for you" panel showed
  untried-nudges for vocabulary/grammar/reading/speaking and correctly
  *excluded* conversation (since a session already existed); clicked
  "Practice vocabulary" and confirmed it navigated to `/quiz`; completed a
  5-question vocabulary quiz (4/5 correct, 80% mastery) and returned to
  the dashboard — vocabulary's recommendation was gone entirely (mastery
  ≥ 70% threshold), while grammar/reading/speaking remained. This
  confirms the full loop closes correctly against a real backend and real
  learner-model data, not just fixtures.
- **Phase 11 manually verified against real cross-phase data**: logged in
  as the same account used throughout Phases 8–10 (one completed quiz at
  80% mastery, one conversation session, nothing else), opened
  `/achievements`, and confirmed exactly 2/10 unlocked — `first_steps`
  (from the quiz) and `chatterbox` (from the conversation) — both with a
  real unlock date, every other badge correctly grayed out. This is
  genuine cross-phase verification: the achievement state reflects real
  actions taken during Phase 8 and Phase 10's manual testing sessions, not
  fixtures set up for this phase alone.
- **Phase 12 manually verified end-to-end, and caught a real "is this
  actually working" moment worth documenting**: opened `/flashcards` on
  the long-lived test account and the very first card was 学校 — a concept
  that account had already answered correctly back in Phase 10's testing,
  which looked like the reordering wasn't working. Investigation (a direct
  API call) confirmed it was a data-vintage issue, not a bug: that Phase
  10 quiz submission happened *before* Phase 12 existed, so no
  `review_schedule` entry was ever created for it — nothing retroactively
  populates history for a feature that didn't exist yet. Submitting a
  fresh answer for the same concept and immediately re-fetching the deck
  confirmed the fix works correctly on live data: it moved from
  effectively random position to 11th of 12 (the back of the deck), and a
  full quiz/flashcard/deck round-trip was confirmed in the browser
  afterward.
- **Phase 13 manually verified end-to-end with real cross-feature
  integration**: on the long-lived test account, opened the new "Kanji"
  tab on `/flashcards` — 80 real kanji loaded, card 1 (北) revealed
  correct meaning/onyomi/kunyomi/example word. Switched to `/quiz`'s
  Kanji tab and completed a 5-question quiz (all real kanji, all four
  options genuinely distinct meanings) at 5/5 correct, +50 XP. Confirmed
  the result rippled correctly through every downstream feature without
  any of them being touched directly: `/progress` showed Kanji at 100%
  mastery; the dashboard's recommendations panel correctly *stopped*
  recommending kanji (now above the 70% threshold) while still
  recommending grammar/reading/speaking; `/achievements` showed
  `century_club` (100 XP) and `perfectionist` (≥90% mastery, ≥5 attempts)
  newly unlocked with real timestamps. This manual run also caught a real
  bug: the `well_rounded` achievement's seeded *description* text still
  listed only the pre-Phase-13 five categories even though its actual
  unlock *criteria* had been updated to require kanji too — fixed in
  `achievement_seed_data.py` (a fresh-seeded database picks up the fix;
  an already-seeded one won't retroactively update, same as any
  seed-once content change — see Technical Debt).

## CI/CD

- Unchanged from Phase 1–6. Backend tests still run against a `mongo:7`
  service container in CI. No `GEMINI_API_KEY` is set or required in CI —
  every AI-dependent test uses `FakeAIService`.

## Known Issues

- None currently tracked.

## Technical Debt

- Carried over: `POST /api/auth/logout` protected no-op; no rate limiting on
  auth/onboarding/AI endpoints (every message sent in a conversation is now
  its own Gemini call, on top of the Phase 7 generate/submit calls — rate
  limiting AI endpoints specifically should be a priority before any public
  deployment); only N5 seed content exists (AI generation partially offsets
  this by supporting any JLPT level on demand); no level picker on the
  *seeded*-content practice pages.
- AI-generated questions are stored indefinitely with no expiry/cleanup —
  fine at current scale, worth revisiting if generation volume grows.
- `mini_stories` documents are never listed back to their creator (no
  "my past stories" page) — each generation is a one-off experience, by
  design for this phase; revisit if that turns out to feel incomplete.
- Conversation sessions never expire/archive and `HISTORY_LIMIT` (20) is a
  fixed constant, not configurable per level/scenario — fine at current
  scale; a very long-running session's early turns simply drop out of what
  gets replayed to Gemini, which only matters if a learner has an
  unusually long single conversation.
- No way to end/delete a conversation session — sessions accumulate
  indefinitely in the history list; acceptable for now since browsing is
  free and there's no per-session cost beyond storage.
- Only 9 speaking prompts exist (curated, in-code), all fixed sentences —
  no AI-generated pronunciation prompts yet (unlike Phase 7's vocabulary/
  grammar questions), and no per-word pronunciation feedback, only
  whole-phrase similarity. A learner will exhaust the prompt list quickly;
  revisit if that turns out to feel limited.
- Speaking similarity scoring (`difflib.SequenceMatcher`, threshold 0.8) is
  a simple text-similarity heuristic, not real pronunciation/phonetic
  analysis — it can't tell a mispronounced-but-correctly-transcribed word
  from a well-pronounced one, since Gemini's transcription already
  "corrects" minor mispronunciations to standard spelling. Good enough for
  an MVP; a dedicated pronunciation-scoring provider would be a bigger,
  separate feature.
- No live browser verification of actual microphone capture — the
  sandboxed browser environment used for manual verification blocks
  `getUserMedia`, so the recording UI was only confirmed to fail
  gracefully (the `denied` path), not to successfully capture and submit
  real audio in a real browser. The upload-and-transcribe flow itself was
  still verified end-to-end via a direct HTTP request with synthetic audio
  bytes. Worth a manual check in a real desktop browser before relying on
  this feature being fully working.
- Recommendations only cover `vocabulary`, `grammar`, `reading`,
  `speaking`, and `conversation` — `kanji` and `listening` have no
  implemented practice route, so nothing would happen if a learner clicked
  a recommendation for them. Once either phase lands, add it to
  `CATEGORIES_SCORED_BY_MASTERY`/`CATEGORY_ACTIONS` in
  `recommendation_service.py`.
- The recommendation engine is a single flat pass over category-level
  mastery — it doesn't recommend a specific *concept* within a weak
  category (e.g. "review 食べる specifically"), only "practice vocabulary
  in general." `/api/mistakes` already exists for concept-level detail;
  a future iteration could cross-reference it for sharper recommendations.
- No persistence of past recommendations (no "recommended X, learner
  ignored it 3 times" tracking) — every request recomputes fresh from
  current data. Fine for an MVP; would matter if recommendation *ranking*
  itself needed to improve from engagement signal later.
- No achievement-unlock notification/toast — a newly-unlocked badge is
  only visible the next time the learner opens `/achievements` (or the
  dashboard, if a future iteration surfaces a summary there), same
  lazy-discovery tradeoff as recommendations. There's no real-time
  push/toast system in the app yet to hook a "you just unlocked X!"
  moment into.
- Achievement criteria are hardcoded in `achievement_service.py`, not
  data-driven from the `achievements` collection's documents (the seeded
  catalog only carries display fields — key/name/description/emoji, no
  machine-readable criteria). Fine at 10 achievements; would need a small
  criteria DSL if the catalog grows large enough that hardcoding every
  check becomes unwieldy.
- `well_rounded` and `perfectionist` are the only achievements that
  reference *category* mastery rather than a flat count — if Phase 10's
  `RecommendationService` category list changes (e.g. kanji/listening gain
  practice routes), `AchievementService`'s category set should be
  revisited alongside it for consistency.
- Historical activity from before Phase 12 shipped has no `review_schedule`
  entries and never will (nothing retroactively backfills it) — a
  long-lived account's flashcard/quiz ordering will look partially random
  until enough fresh answers accumulate real schedule data. Expected, not
  a bug (see the manual-verification note above), but worth knowing if
  ordering looks off on an old test account.
- Speaking prompt *list* ordering (`GET /api/speech/prompts`) doesn't use
  `review_schedule` yet, even though speaking attempts feed it — the
  picker is a manual "choose one" UI, not an auto-generated set, so this
  wasn't in scope for Phase 12. Revisit if the prompt list grows large
  enough that manual browsing becomes tedious.
- Reading (mini-story comprehension) and conversation are excluded from
  spaced repetition entirely — a mini-story's "concept" is the story title
  (a one-off, not a reusable pool to reorder), and conversation never had
  a schedulable concept in the first place (Phase 8). SRS only applies to
  the three genuinely reusable content pools: vocabulary, grammar, and
  speaking prompts.
- No UI surfaces spaced-repetition state directly (no "5 cards due today"
  count, no due-date badge per card) — the *effect* is felt (smarter
  ordering) but the *mechanism* is invisible. A future pass could expose
  due counts, e.g. on the dashboard or flashcards page, if that turns out
  to matter for motivation/transparency.
- Vocabulary depth is still just 12 items (vs. the ~800-word real N5
  scope) — Phase 13 deliberately prioritized Kanji (a whole new,
  previously-unbuilt category) and grammar breadth over vocabulary
  breadth, given limited time in one phase. Phase 14 is earmarked for
  vocabulary expansion specifically.
- Only N5 kanji/grammar exist — N4 through N1 (progressively larger scope:
  roughly 300/650/1000/2000+ cumulative kanji and correspondingly more
  vocabulary/grammar per the researched estimates) are unbuilt. Getting a
  learner all the way to "ready for N1" is a multi-phase content effort,
  not a single pass.
- Kanji quizzing only tests meaning (character → English meaning),
  mirroring vocabulary's format — it doesn't yet quiz on/kunyomi readings
  separately, which real kanji study usually also drills. Worth adding as
  a second kanji quiz mode if reading recall turns out to matter more than
  meaning recognition for learners.
- The `well_rounded` achievement's seeded description text needed a
  manual fix alongside the code change that added kanji to its criteria
  (see the Phase 13 manual-verification note above) — a reminder that
  `achievement_seed_data.py`'s human-readable text and
  `achievement_service.py`'s actual unlock logic are two separate sources
  of truth that must be kept in sync by hand; there's no single place
  that generates one from the other.

## Important Decisions

- The git repository root is `jap-jap/` nested one level inside the
  `self-project/jap-jap/` folder on disk (pre-existing `git init` + GitHub
  remote `geoff023/jap-jap` were preserved rather than re-initialized).
- Generated vocabulary/grammar questions reuse Phase 4's `questions`
  collection rather than getting their own — they're structurally identical
  content (prompt/options/correct_answer/explanation/concept/category/level),
  and a `source` tag is enough to distinguish provenance without a schema
  fork. Mini stories get a dedicated collection because their comprehension
  questions are embedded and story-specific, not a reusable unit the way a
  vocabulary/grammar question is.
- `_validate_multiple_choice` lives as a `model_validator` on the Pydantic
  schemas themselves (`app/schemas/ai_generation.py`), not as separate
  "business validation" code called after Pydantic — for this app, the
  business rules (4 unique options, correct answer present) are simple and
  static enough that keeping them co-located with the schema is clearer
  than a second validation pass, while still being conceptually the
  pipeline's distinct "business validation" step.
- Comprehension question answers write to `learner_skills` with
  `category: "reading"` and `concept: <story title>` — a deliberate choice
  to give `reading` its first real data source now rather than waiting for
  a dedicated reading-comprehension phase, since Phase 7's mini stories are
  functionally exactly that.
- Standalone generated questions (unlike quiz/test answers) award 0 XP for
  a wrong answer rather than some smaller deterministic penalty — matches
  the quiz/test XP model (Phase 3/4) exactly: correct answers earn XP,
  incorrect answers earn none, never negative.
- Generation endpoints (`/generate/*`) don't require completed onboarding;
  only the endpoints that award XP (`*/submit`) do — matches the existing
  "browsing is free, earning XP requires a profile" pattern from Phases 3–4
  (e.g. `GET /api/vocabulary` vs `POST /api/activities/quiz/submit`).
- Characters and scenarios (Phase 8) are a static, in-code roster
  (`app/core/conversation_data.py`), not a database collection — small and
  curated enough that versioning them alongside the app guarantees "which
  character speaks in which scenario" can never drift, unlike a database
  record that could be edited independently of the code that assumes its
  shape.
- Scenario opening lines are static/curated, not AI-generated — guarantees
  a consistent first line from turn 0 for every learner in a given
  scenario, and saves one Gemini call per session start.
- `ConversationService.send_message` calls Gemini *before* persisting the
  learner's message (not the other way around) — discovered via manual
  browser verification that persisting first would leave a dangling,
  unanswered user turn in the database on AI failure, corrupting the next
  prompt's history reconstruction. This ordering also means a failed send
  costs nothing in stored state — a retry is indistinguishable from a first
  attempt.
- Conversation turns intentionally do **not** feed `learner_skills` — open-
  ended chat has no single correct answer to score against, so recording it
  would mean fabricating a mastery number, violating the never-fabricate
  principle used everywhere else in the learner model. XP is a flat 3 per
  message instead of a correctness-based amount.
- Conversation XP (3/message) is deliberately lower than quiz/test XP
  (10/correct answer) since sending a message requires no correctness check
  — keeps the XP economy weighted toward verified learning, not just
  activity volume.
- The default `SpeechToTextService` implementation (`GeminiSTTProvider`)
  reuses Gemini itself (via `google-genai`, same as `GeminiService`) rather
  than integrating a dedicated speech vendor (Google Cloud Speech-to-Text,
  Whisper, etc.) — Gemini 2.0 Flash already accepts audio input, so this
  avoids a second paid AI vendor/SDK and keeps contributor setup to one
  ecosystem. `STT_API_KEY` stays a distinct setting from `GEMINI_API_KEY`
  (per [ARCHITECTURE.md](ARCHITECTURE.md)'s original Speech Abstraction
  design) so speech features can still be toggled independently — a future
  phase could swap in a different `STTProvider` without touching
  `SpeakingService` or the API layer.
- Speaking prompts (Phase 9) are a static, in-code roster
  (`app/core/speaking_data.py`), same rationale as Phase 8's
  characters/scenarios — small and curated enough that a phrase and its
  target text can never drift apart, and no seeding/migration needed to
  add more later.
- Pronunciation correctness uses a similarity *threshold* (0.8 via
  `difflib.SequenceMatcher`), not exact string match — Gemini's
  transcription of real speech rarely matches the target byte-for-byte
  even when pronunciation was fine (optional particles, punctuation).
  Normalizing out whitespace/punctuation before comparing further reduces
  false negatives from formatting alone rather than pronunciation.
- `SpeakingService.submit_attempt` persists the attempt only *after*
  transcription succeeds — applying the Phase 8 lesson (see above) from
  the start this time, rather than discovering the same bug again.
  Verified live: a failed transcription leaves zero trace in
  `speaking_attempts`.
- A correct speaking attempt earns the same 10 XP as a quiz/test correct
  answer (not 3, like conversation) — pronunciation practice *does* have a
  deterministic correct/incorrect check (the similarity threshold), unlike
  open-ended conversation, so it belongs in the "verified learning" XP
  tier, not the lower "activity volume" tier.
- Recommendations are computed fresh on every `GET /api/recommendations`
  call rather than persisted to a `recommendations` collection (which
  DATABASE.md's original planned-collections list anticipated) — the same
  "mastery is always computed on read, never stored" principle used
  throughout the learner model since Phase 5 (`learner_model_service.py`)
  applies just as well here: there's no staleness to manage, and nothing
  yet needs a history of past recommendations.
- `RecommendationService` is entirely Gemini-free — recommending *what* to
  practice next is exactly the "deterministic ranking" the architecture
  reserves for backend logic, never AI (see
  [ARCHITECTURE.md](ARCHITECTURE.md)'s Product Model). AI stays confined
  to *content* (explanations, generation, conversation, transcription);
  deciding what a learner should do next is scoring logic, not creative
  generation.
- Conversation's "has this been tried" check queries `conversation_sessions`
  directly (`ConversationSessionRepository.list_by_user(..., limit=1)`)
  rather than `learner_skills.has_data`, because Phase 8 deliberately never
  writes conversation turns to `learner_skills` — using `has_data` for
  conversation would have permanently recommended it even to a learner
  who'd already had a dozen conversations.
- A category can produce at most one recommendation (either weak or
  untried, never both — the two conditions are mutually exclusive by
  definition), which naturally bounds the list to 5 entries without any
  separate "top N" capping logic.
- Recommendations surface on the Dashboard, not a dedicated `/recommendations`
  page — "what should I practice next" is a landing-moment decision, not a
  feature a learner navigates *to*; ProgressPage remains the place for
  mastery detail, Dashboard is where action happens.
- The achievement catalog is seeded into MongoDB (`achievements`
  collection), unlike Phase 8/9's characters/scenarios/speaking prompts
  which stayed purely in-code. The distinguishing factor: those are
  referenced by key *inside* AI prompt construction (personality strings,
  target phrases) and never listed as a standalone catalog, whereas
  achievements are exactly a catalog — a list of things to browse — which
  matches how Phase 3 already handles vocabulary/grammar (author in code,
  seed into Mongo, query from there). Same underlying content-authoring
  approach, different collection-vs-in-code call based on how the content
  is actually *used*, not a new rule.
- `UserAchievementRepository.unlock()` is an idempotent upsert
  (`$setOnInsert` on `(user_id, achievement_key)`), so `AchievementService`
  can safely call it on *every* met criterion on *every* request without
  ever double-unlocking or shifting `unlocked_at` forward — this is what
  makes "lazy unlock-on-read" (checking criteria fresh each request rather
  than hooking into every XP-earning service's write path) safe to do
  without a dedicated event system. Verified live: `unlocked_at` for
  `chatterbox` was identical across two consecutive `GET /api/achievements`
  calls in the same test.
- Achievement unlocking is computed lazily on read (whenever a learner
  visits `/achievements`) rather than event-driven (checked immediately
  after every quiz/test/conversation/speaking action). The event-driven
  approach would need threading an `AchievementService` dependency into
  five existing services (`ActivityService`, `TestService`,
  `ContentGenerationService`, `ConversationService`, `SpeakingService`) —
  broad and invasive for a first pass. Lazy-on-read costs only a slightly
  "late" `unlocked_at` timestamp (whenever the learner next checks, not
  the exact moment of completion) in exchange for zero changes to any
  existing write path — the same "compute derived state on read" choice
  made for Phase 10's recommendations.
- `well_rounded` and `perfectionist` reuse the exact category-mastery
  aggregation Phase 10's `RecommendationService` already computes
  (`learner_skills` grouped by category, correct/(correct+incorrect)) —
  duplicated in `achievement_service.py` rather than extracted into a
  shared helper, since the two services need it in slightly different
  shapes (recommendations need per-category `has_data`/mastery/attempts
  as a list; achievements need a single "does *any* category clear this
  bar" boolean) and the computation itself is a few lines, not worth an
  abstraction yet.
- Phase 12's scheduling algorithm is SM-2-*inspired*, not literal SM-2 —
  real SM-2 grades recall quality on a 0-5 scale and this app only ever
  has binary correct/incorrect (no activity anywhere asks "how easily did
  you recall this"). The two-branch simplification (correct → grow
  interval + ease; incorrect → reset repetitions, shorten interval, shrink
  ease) captures the core spaced-repetition behavior — well-known things
  get shown less, weak things get shown more — without needing a UI
  concept (a 0-5 self-rating) the rest of the app doesn't have anywhere
  else.
- Mastery (`learner_skills`, Phase 5) and scheduling (`review_schedule`,
  Phase 12) are deliberately two separate collections/repositories/write
  paths rather than one merged concept, even though both update from the
  same answer event. They answer different questions for different
  audiences: mastery is what `/api/progress`, `/api/mistakes`, and
  `/api/recommendations` show a learner about *how well* they know
  something; due-date is purely an internal *content-selection* signal a
  learner never sees directly. Merging them would couple two concerns
  that may evolve independently (e.g. a future mastery-decay feature
  shouldn't have to touch scheduling math, and vice versa).
- `generate_quiz`'s selection is a straightforward "sort by due date, take
  the first N" rather than a weighted/probabilistic pick — simpler to
  reason about and test deterministically (given fixed input, the ranking
  order is fully determined except for the intentional random tie-break
  among equal-priority items) — the random shuffle before the stable sort
  already prevents "always the exact same N items" staleness
  when many concepts are equally new/due.
- `ActivityService.get_flashcard_deck` returns *every* item in the level,
  just reordered — unlike `generate_quiz`, which takes a size-limited
  prefix. Flashcard mode's whole premise is reviewing the full deck; only
  the *order* should be smarter, not the *completeness*.
- **JLPT content sourcing (Phase 13):** the Japan Foundation/JEES have
  never published an official JLPT vocabulary/kanji list (and stopped
  publishing any official kanji list after 2010) — every study resource
  (Tanos, JLPTsensei, WaniKani, Migaku, etc.) works from the same
  reverse-engineered consensus scope, compiled by analyzing real past
  exams. That scope itself — which ~80 kanji, which ~800 words, which
  ~grammar points appear at N5 — is factual/reference information, not a
  copyrightable exam artifact; using it to decide *what* to teach is
  legitimate and how virtually every JLPT prep product works. What
  remains off-limits is reproducing actual past-exam questions, reading
  passages, or other exam-specific compositions verbatim. This phase
  researched the former (via web search against JLPTsensei/Tanos/
  community sources) and used it only to decide *scope* — every piece of
  actual content (kanji example words, grammar example sentences,
  explanations) was then originally written for this app, the same
  authorship model Phase 3 already established for vocabulary/grammar.
- Kanji joined the codebase as a genuine third `ActivityCategory`, not a
  parallel special-cased feature — same repository shape as vocabulary,
  same quiz/flashcard dispatch tables, same category-string plumbing
  through `learner_skills`/`review_schedule`/recommendations/achievements.
  This is why `RecommendationService` and `AchievementService` needed only
  small constant updates (add `"kanji"` to a set/dict) rather than new
  code paths — the category abstraction Phases 5/10/11 already built was
  designed generically enough to absorb a new category cheaply.
- Grammar expansion (8 → 38) was curated, not a mechanical dump of every
  researched grammar point — entries that are grammatical *categories*
  rather than fill-in-the-blank *patterns* (e.g. "i-adjectives" as a
  listing, standalone sentence-ending tone particles like ね/よ that need
  more context than one blank can carry) don't fit this app's
  sentence-completion format and were deliberately left out in favor of
  quality/correctness over raw count.

## Next Phase

Phase 14 — Vocabulary Expansion (grow N5 vocabulary from 12 items toward
the ~800-word researched scope, likely in batches given the sheer content
volume, following the same original-content/researched-scope sourcing
approach established in Phase 13), then Streaks & Daily Goals, XP Levels/
Ranks, Deeper Badges, and finally Leaderboards/Social per the phase
sequence agreed with the user. As with Phases 11–13, this sequence is
built from explicit user direction and scoped-down inference from the
user's own requests, not verbatim master-prompt text — the original
master prompt's phase list beyond Phase 10 remains unknown from here;
paste it if it should take precedence.
