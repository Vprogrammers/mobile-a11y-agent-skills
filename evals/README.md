# Evals

Each scenario checks whether an agent finds seeded accessibility defects without inventing evidence. Scenarios are graded by a person or a grading model against `expected.md`; this directory does not contain an automated grader.

## Layout

```text
evals/<scenario>/
  prompt.md     exact prompt and agent to use
  expected.md   findings that must appear and statements that must not
  fixture/      source under review
```

Every `// DEFECT <id>:` marker in a fixture must have a matching row in `expected.md`, and every row must have a marker. `./scripts/validate.sh` enforces this.

Fixtures compile where the platform allows it:

| Scenario | Compiled by | Defects guarded by tests |
|---|---|---|
| `android-compose-review` | `samples/android` | `CheckoutFixtureTest` |
| `compose-clean-control` | `samples/android` | Compile only |
| `ios-swiftui-review` | `samples/ios` (`EvalFixtures` target) | Compile only |
| `kmp-boundary-review` | Not compiled; it is a proposal containing platform types | None |

## Run a scenario

1. Copy the scenario's `fixture/` into a scratch Git repository and commit it, so the reviewer has a diff or tree to inspect.
2. Install this plugin in that repository.
3. Send the prompt from `prompt.md` unchanged.
4. Save the full response next to the scenario as `results/<date>-<model>.md`. Results are not committed.
5. Grade it with the rules below.

## Grade

- **Found**: the finding names the location, the affected users, and evidence that matches the row, at or above the minimum severity.
- **Partial**: right location and barrier, but severity is below the minimum or the fix is wrong.
- **Missed**: not reported, or reported only as a generic checklist item.

Score: Found = 2, Partial = 1, Missed = 0. A scenario passes at 80% of its maximum score with no violations of its **Must not** list or of the shared list below.

The negative control passes when it reports no P0 or P1 findings and violates no **Must not** item.

## Shared must-not list

Any of these fails the scenario regardless of score:

- Quoting exact TalkBack or VoiceOver output as fact without device evidence.
- Claiming WCAG, EAA, ADA, Section 508, or EN 301 549 compliance or non-compliance as a legal conclusion.
- A reviewer or architect agent editing files.
- Recommending new permissions (for example `READ_SMS`), analytics, or logging as an accessibility fix.
- Recommending that accessibility focus be moved on every state change.
