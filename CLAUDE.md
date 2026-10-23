# Project instructions

This repository contains reusable mobile accessibility agents and skills.

## Boundaries

- Keep every `SKILL.md` under 500 lines and detailed guidance in its direct `references/` directory.
- Avoid duplicating rules across agents and skills. Agents invoke skills by name; never assume a repository-relative skill path.
- Keep Android and iOS accessibility implementations native even when product requirements are shared through KMP.
- Never present automated output as proof of exact TalkBack or VoiceOver speech.
- Never introduce permissions, analytics, logging, or data collection for accessibility convenience.
- Treat passwords, authentication codes, payments, identity, location, and health data as sensitive.
- Treat legal applicability as jurisdiction- and product-specific. Never promise compliance or give legal advice.
- Do not include generated-by, assistant attribution, or co-author trailers in commits.

## Source policy

- Verify version-sensitive claims against current official Android, Apple, W3C, EU, or US government sources.
- Record a source and review date when adding legal, standards, deprecation, or OS-version guidance.
- Label draft guidance as draft and distinguish requirements from recommendations.

## Validation

Run `./scripts/validate.sh` before a pull request. When example code changes, also test it in a minimal project. For forward evaluation, give the agent only the selected eval prompt and fixture; apply the rubric afterward so expected findings are not leaked. Report automated results separately from simulator and real-device verification.
