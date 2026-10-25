# Project instructions

This repository maintains mobile accessibility agents and skills. The `mobile-a11y-workflow` skill is the single source for agent routing, delegation, the repair/re-review loop, scope, the source policy, safety rules, claims, and the completion report. Those rules also govern the guidance you write here; change them only in that skill. `distribution/light/CLAUDE.md` and the README point to it. [CONTRIBUTING.md](../CONTRIBUTING.md) lists every contribution rule.

## Authoring

- Keep every `SKILL.md` under 500 lines and detailed guidance in its direct `references/` directory. Keep each skill's “Where to look” table in step with its reference sections.
- Do not duplicate rules across agents, skills, and instruction files. Agents preload skills through `skills` frontmatter and invoke them by name; never use a repository-relative skill path.
- Skill frontmatter holds only `name` and `description`. Agent frontmatter holds `name`, `description`, `tools`, and `model`, and may add `skills` and `maxTurns`; every agent preloads `mobile-a11y-workflow`.
- Do not add a `heldout-*` eval's `held_out_terms` to `skills/`, `agents/`, or `distribution/light/CLAUDE.md`. To teach such a defect, remove the eval's held-out status in the same change.
- Do not include generated-by, assistant attribution, or co-author lines in commits or pull request descriptions.

## Sources

- Follow the source policy in `mobile-a11y-workflow` for every version-sensitive claim. Record the source and review date (`Last reviewed`, and `Review interval` when shorter than the default) when adding legal, standards, deprecation, or OS-version guidance.
- Compile every new API name in `samples/` instead of trusting memory, and check new source URLs.
- Label draft guidance as draft and distinguish requirements from recommendations.

## Validation

- Run `./scripts/validate.sh` and `claude plugin validate --strict .` before a pull request.
- When example code or an eval fixture changes, update `samples/` and run `./gradlew assembleDebug testDebugUnitTest` in `samples/android`, `./samples/ios/test.sh`, or `./gradlew check` in `samples/kmp`.
- When a repair eval's fixture, tests, or reference fix changes, run `./scripts/run_repair_eval.py --self-check --platform=android` or `--platform=ios`.
- Do not run paid or model-backed evals (`scripts/run_eval_suite.py`, `scripts/run_repair_eval.py` with an agent command, `claude plugin eval`) without the user's explicit approval for that run and its cost cap.
- For forward evaluation, give the agent only the selected eval prompt and fixture; apply the rubric afterward so expected findings are not leaked.
- Report automated results separately from simulator and real-device verification, and update the README verification status table when a row is tested on a device.
