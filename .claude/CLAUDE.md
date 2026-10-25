# Project instructions

This repository contains reusable mobile accessibility agents and skills.

## Boundaries

- Keep every `SKILL.md` under 500 lines and detailed guidance in its direct `references/` directory.
- Avoid duplicating rules across agents and skills. Agents invoke skills by name; never assume a repository-relative skill path.
- Keep Android and iOS accessibility implementations native even when product requirements are shared through KMP. The exception is Compose Multiplatform shared UI, where Compose semantics are the iOS implementation and need VoiceOver verification on iOS.
- Never present automated output as proof of exact TalkBack or VoiceOver speech.
- Never introduce permissions, analytics, logging, or data collection for accessibility convenience.
- Treat passwords, authentication codes, payments, identity, location, and health data as sensitive.
- Treat legal applicability as jurisdiction- and product-specific. Never promise compliance or give legal advice.
- Do not include generated-by, assistant attribution, or co-author trailers in commits.

## Source policy

- Verify version-sensitive claims against current official Android, Apple, W3C, EU, or US government sources.
- Record a source and review date when adding legal, standards, deprecation, or OS-version guidance.
- Label draft guidance as draft and distinguish requirements from recommendations.

## Agent routing

1. Use `kmp-a11y-architect` first when a change affects shared public APIs, source-set ownership, exported types, dependencies, native UI boundaries, or Compose Multiplatform UI.
2. Use `android-a11y-engineer` and/or `ios-a11y-engineer` for platform implementation.
3. Use `accessibility-test-engineer` after implementation when accessibility coverage changes or is missing.
4. Use `accessibility-reviewer` for an independent final review after implementation and tests. Do not ask an implementation agent to approve its own work.

Keep edits limited to the requested accessibility change. Do not modify unrelated build configuration, dependency versions, public APIs, or product behavior to make a local fix easier. Stop and report when such a change is required.

## Completion report

Every implementation or testing agent must report changed files, commands executed, automated results as passed/failed/skipped, simulator or emulator results, real-device checks completed, real-device checks still required, assumptions, and unresolved decisions. Never collapse those evidence levels into “accessibility passed.”

## Validation

Run `./scripts/validate.sh` before a pull request. When example code or an eval fixture changes, update `samples/` and run `./gradlew assembleDebug testDebugUnitTest` in `samples/android` or `./samples/ios/test.sh`. For forward evaluation, give the agent only the selected eval prompt and fixture; apply the rubric afterward so expected findings are not leaked. Report automated results separately from simulator and real-device verification.
