# Evaluation guide

Run commands from the repository root.

## Repository validation

```bash
./scripts/validate.sh
```

`validate.sh` runs the repository validator, compiles the scripts, runs the installation smoke test, and runs the unit tests. The validator checks skill and agent metadata, explicitly named invoked skills, duplicate names, local links, plugin version consistency, required review dates, executable permissions, and typed eval manifests/rubrics. It warns 30 days before each reference's declared review interval expires and fails when it is stale. Dynamic platform references use 180 days, regulatory guidance uses 90 days, and references without an override use 365 days. External links are optional in pull-request CI; a scheduled workflow checks them monthly.

CI also installs the pinned Claude Code version and runs its authoritative manifest check:

```bash
claude plugin validate --strict .
CHECK_EXTERNAL_LINKS=1 ./scripts/validate.sh
```

## Domain evals

Evaluation scenarios live in `evals/`. Each manifest entry points to a prompt, raw code fixture, scoring rubric, minimum score, and forbidden claims. Give only the prompt and fixture to the agent; apply the rubric afterward so expected findings are not leaked.

Rubrics keep finding `kind` separate from severity. Severity uses the `P0`–`P3` definitions in `mobile-a11y-review`, applies only to defects, and is `null` for architecture, interop, testing, verification, compliance, dependency, or recommendation criteria. A defect whose severity does not match the rubric earns no points for that finding; the rest of the result still counts. Evals that ask for severity set `"severity_required": true` and append the shared severity scale to both plugin and baseline prompts.

When judge output is rejected, `judge_eval.py` keeps it in `<result>.rejected.txt`. A valid result has this shape:

```json
{
  "matched_findings": [
    {"id": "gesture-only-help", "severity": "P1"},
    {"id": "non-modal-overlay", "severity": "P1"}
  ],
  "forbidden_claims": []
}
```

Calculate deterministic pass/fail with:

```bash
./scripts/score_eval.py android-compose-review result.json
```

Most evals cover guidance present in the skills. `heldout-*` evals measure behavior on defects not taught by the plugin. Their manifests declare `held_out_terms`; validation fails if those terms appear in a skill. Remove held-out status when guidance intentionally begins covering one of them.

Classification remains separate from scoring: a human or independent evaluator maps the raw response to finding IDs and forbidden claims. Substring matching is not treated as review-quality evidence.

## Judge and full suite

Configure a judge CLI that reads the blind judging prompt from standard input and returns the documented JSON result:

```bash
EVAL_JUDGE_COMMAND='claude -p --model opus --restricted --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 2 --max-budget-usd 0.25' \
  ./scripts/judge_eval.py android-compose-review response.md result.json
```

The adapter extracts JSON from a fenced block or short prose and validates it before writing the result. The judge is excluded from pull-request CI because it is nondeterministic, costs money, and requires user-managed credentials.

Run every domain eval with separate trusted agent and judge commands. The agent command must include `{agent}`; `{plugin_dir}` resolves to the repository root. Add only `skills/` to the restricted workspace because the repository root also contains rubrics.

```bash
EVAL_AGENT_COMMAND='claude -p --model sonnet --plugin-dir "{plugin_dir}" --agent mobile-a11y-agent-skills:{agent} --restricted --add-dir "{plugin_dir}/skills" --allowedTools Read Glob Grep Skill --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 8 --max-budget-usd 0.75' \
EVAL_JUDGE_COMMAND='claude -p --model opus --restricted --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 2 --max-budget-usd 0.25' \
EVAL_MODEL='agent=sonnet,judge=opus' \
./scripts/run_eval_suite.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-sonnet-opus"
```

Set `EVAL_VARIANT=baseline` to send the same prompts and fixtures without the plugin. Score both variants with the same judge and rubrics. Set `EVAL_SECOND_JUDGE_COMMAND` to require a second independent judge. Reviewed bundles live in `evals/results/`; see the [baseline summary](../evals/results/README.md).

```bash
EVAL_VARIANT=baseline \
EVAL_AGENT_COMMAND='claude -p --model sonnet --restricted --allowedTools Read Glob Grep --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 8 --max-budget-usd 0.75' \
EVAL_JUDGE_COMMAND='…same Opus judge…' EVAL_MODEL='agent=sonnet,judge=opus' \
./scripts/run_eval_suite.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-sonnet-opus-baseline"
```

## Official plugin evals

`plugin-evals/` contains one eval per agent. They test namespaced routing, and the reviewer eval also grades output quality in Claude Code's isolated runner:

```bash
claude plugin eval . --runs 1 --ablation with-without --max-cost-usd 8.00 --no-publish
```

Use the official runner for plugin loading, routing, traces, and baseline evidence. Use the custom suite for detailed accessibility rubrics and deterministic scoring.

The manually triggered `Agent eval regression` workflow runs plugin and baseline variants only when `CLAUDE_CODE_OAUTH_TOKEN` is configured. It has no schedule. Without the secret, it records an explicit skipped summary. Pull-request CI never invokes a paid model, and workflow results are retained as artifacts instead of committed automatically.

## Repair evals

Review evals show whether an agent can describe a fix. Repair evals under `evals/repairs/` check the edited code. The runner copies only the fixture and stubs into a temporary workspace. After the agent edits it, the runner adds hidden Robolectric tests and scores required behavior, forbidden patterns, and preserved behavior. A build that does not compile scores zero.

```bash
./scripts/run_repair_eval.py --self-check

EVAL_REPAIR_AGENT_COMMAND='claude -p --model sonnet --plugin-dir "{plugin_dir}" --agent mobile-a11y-agent-skills:{agent} --restricted --tools Read,Glob,Grep,Edit,Write,Bash,Skill --add-dir "{plugin_dir}/skills" --allowedTools Read Glob Grep Edit Write Bash Skill --permission-mode dontAsk --permission-prompts none --no-session-persistence --max-turns 25 --max-budget-usd 2.00' \
./scripts/run_repair_eval.py "evals/results/$(date -u +%Y-%m-%dT%H%M%SZ)-repair-sonnet"
```

Set `EVAL_VARIANT=baseline` and remove plugin and agent options for the baseline. Restricted mode removes Bash unless `--tools` names it, and the repair agent needs Bash to build. Bash is not confined by restricted file-tool boundaries, so use only trusted agent commands. Each run needs JDK 17 and the Android SDK.
