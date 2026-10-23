# Contributing

Contributions are welcome for Android, iOS, Kotlin Multiplatform, testing, and assistive-technology guidance.

## Rules

- Keep each `SKILL.md` concise and move detailed material into its `references/` directory.
- Use only `name` and `description` in skill frontmatter.
- Write instructions in imperative form.
- Prefer official platform APIs and documentation.
- Separate verified behavior from recommendations and assumptions.
- Never claim that automated checks reproduce actual TalkBack or VoiceOver output.
- Include the platform, OS version, UI framework, assistive technology, and verification method when reporting behavior.
- Avoid project-specific package names, paths, secrets, signing configuration, or credentials.
- Start every reference file with `Last reviewed: YYYY-MM-DD` and cite official https sources.
- When you change a code example in a reference, update the matching code in `samples/` and run its tests.
- Keep eval fixtures free of import lines; the samples compile generated copies. Update the guard tests when a fixture or rubric changes.
- Do not add generated-by or co-author metadata to commits.

## Pull requests

Explain:

- the problem being solved;
- the affected agent or skill;
- why the guidance is platform-correct;
- how it was validated;
- which parts still require manual device testing.
