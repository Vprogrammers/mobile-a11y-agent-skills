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
- Use `WebSearch` and `WebFetch` only for current primary sources from Android, Apple, JetBrains, W3C, ETSI, EU institutions, or US government bodies. If those tools are unavailable, mark the claim `not independently verified` instead of presenting it as current.

## Agent workflow

The `mobile-a11y-workflow` skill is the single source for agent routing, the repair/re-review loop, scope limits, the consumer source policy, safety rules, and the completion report. Invoke it when coordinating accessibility agents in this repository. Change those rules only in that skill; `distribution/light/CLAUDE.md` and the README point to it.

## Validation

Run `./scripts/validate.sh` before a pull request. When example code or an eval fixture changes, update `samples/` and run `./gradlew assembleDebug testDebugUnitTest` in `samples/android`, `./samples/ios/test.sh`, or `./gradlew check` in `samples/kmp`. For forward evaluation, give the agent only the selected eval prompt and fixture; apply the rubric afterward so expected findings are not leaked. Report automated results separately from simulator and real-device verification.
