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
- Start every reference file with `Last reviewed: YYYY-MM-DD` and cite official https sources. Add `Review interval: N days.` when the reference needs a shorter cadence than the 365-day default.
- When you change a code example in a reference, update the matching code in `samples/` and run its tests.
- Keep eval fixtures free of import lines; the samples compile generated copies. Update the guard tests in `samples/` or `tests/test_eval_fixtures.py` when a fixture or rubric changes.
- Name every invoked skill explicitly in agent instructions; the validator rejects phrases such as "relevant platform skills".
- Run `./scripts/validate.sh`; it also runs the unit and installation smoke tests.
- Keep paid or nondeterministic model evals outside pull-request CI. Use `claude plugin eval .` for plugin routing evidence and `scripts/run_eval_suite.py` for the detailed domain rubrics. Retain generated summaries and never commit credentials or private project data with eval evidence.
- Use `skills/mobile-a11y-testing/references/real-device-evidence-template.md` for manual assistive-technology results and keep them release-specific.
- Follow `SECURITY.md`; never use accessibility work to access secrets, weaken privacy, publish, sign, deploy, or send project data without explicit authorization.
- Do not add generated-by or co-author metadata to commits.

## Pull requests

Explain:

- the problem being solved;
- the affected agent or skill;
- why the guidance is platform-correct;
- how it was validated;
- which parts still require manual device testing.
