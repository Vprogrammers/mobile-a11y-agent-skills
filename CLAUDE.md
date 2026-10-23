# Project instructions

This repository contains reusable mobile accessibility agents and skills.

## Boundaries

- Keep `SKILL.md` files under 500 lines.
- Store detailed platform guidance in the skill's direct `references/` directory.
- Avoid duplicating the same rule across agents and skills. Agents should route to skills.
- Keep Android and iOS implementations native even when product requirements are shared through KMP.
- Never present automated output as proof of real screen-reader speech.
- Never introduce permissions, analytics, logging, or data collection for accessibility convenience.
- Treat OTP, password, payment, identity, and health input as sensitive.
- Do not include generated-by, assistant attribution, or co-author trailers in commits.

## Validation

Before a pull request:

1. verify every skill directory contains `SKILL.md`;
2. verify skill frontmatter contains only `name` and `description`;
3. verify every linked reference exists;
4. review changed instructions against current Android or Apple behavior;
5. test example code in a minimal project when code is added;
6. report device-only verification separately.
