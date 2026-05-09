> ## Documentation Index
> Fetch the complete documentation index at: https://docs.cartesia.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Prompting tips

> Get natural-sounding output from Sonic with minimal prompt engineering.

Sonic 3.5 is designed to sound natural with minimal prompt engineering. In most cases you can pass your transcript as-is and let the model handle normalization, pacing, and expression. The tips below apply across the Sonic family; differences between Sonic 3.5 and Sonic 3 are called out inline.

## Recommendations

* **Pass natural, well-punctuated text.** Full sentences with normal capitalization and punctuation produce the best pacing and intonation. End each transcript with terminal punctuation (`.`, `?`, `!`).
* **Pass numbers, dates, times, and common acronyms as-is** unless you have a specific reason to override. Sonic handles the most common patterns natively:

  * Large numbers like `1,234,567`
  * US phone numbers: `(415) 555-1212`
  * Email addresses: `user@example.com`
  * Dates in `MM/DD/YYYY` (or `DD/MM/YYYY` based on locale): `04/20/2025`
  * Times with a space before AM/PM: `7:00 PM`, `7 PM`, `7:00 P.M.`
  * Common acronyms (`NASA`) and initialisms (`USA`)

  Symbols are handled naturally — `@` reads as `at` (email addresses), `()` is silent (phone numbers).
* **Match the voice to the language.** Each voice has a primary language it works best with. Use the [Playground](https://play.cartesia.ai) to audition voices for a given language.
* **Keep prompts in their natural written form.** Heavy preprocessing (stripping punctuation, forcing all caps) generally hurts output quality.

## Controlling pacing and spelling

When you need character-by-character read-out (confirmation codes, order IDs, serial numbers, spelled-out names) or fine-grained pacing, use one of the following:

1. **Spell tags (recommended).** Wrap the string in `<spell>...</spell>`. Most reliable option, works for letters, digits, and mixed alphanumerics in all supported languages.
   ```
   Your confirmation code is <spell>AB12CD</spell>.
   ```
2. **Space-delimited characters.** If you prefer not to use tags, separate characters with single spaces.
   ```
   Your code is A B C 1 2 3.
   ```
3. **Commas for pauses between groups.** Use commas where a human would naturally pause.
   ```
   Your code is A B C, 1 2 3.
   ```

<Note>
  **Migrating from Sonic 3?** The recommended delimiter format has changed in Sonic 3.5. Use **spaces between characters** and **commas between groups** instead of commas between characters and periods between groups. The old format still works on `sonic-3` snapshots but is no longer recommended going forward.
</Note>

| Scenario                   | Old (Sonic 3)       | New (Sonic 3.5) |
| -------------------------- | ------------------- | --------------- |
| Spell out letters `HELLO`  | `H, E, L, L, O`     | `H E L L O`     |
| Spell out digits `123456`  | `1, 2, 3, 4, 5, 6`  | `1 2 3 4 5 6`   |
| Confirmation code `ABC123` | `A, B, C. 1, 2, 3.` | `A B C, 1 2 3`  |

## Inserting pauses

Sonic respects natural punctuation like commas and periods. For a longer or specifically-located pause, use a [break tag](/build-with-cartesia/capability-guides/ssml-tags#pauses-and-breaks). Break tags count as a single character and don't need surrounding whitespace.

## Pronunciation

For proper nouns, trademarks, and domain-specific terms — or to disambiguate identical spellings (e.g. *Nice*, the city, vs. *nice*, the adjective) — use [custom pronunciations](/build-with-cartesia/capability-guides/custom-pronunciations).

## Streaming

Use [continuations](/build-with-cartesia/capability-guides/stream-inputs-using-continuations) when generating chunks of audio that need to sound contiguous (for example, LLM-streamed output). This preserves prosody and voice consistency across chunk boundaries.
