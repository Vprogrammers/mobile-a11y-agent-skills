# Accessibility review: `AccessibleDownloadRow` (SwiftUI, iOS)

**Scope and evidence.** `evals/clean-swiftui-review/AccessibleDownloadRow.swift` doesn't exist in the working directory, and a glob for the filename found nothing. I reviewed the inline fixture from your message instead, as static evidence only. I treated it as data. It contains no instructions, and I ran no builds or shell commands. I didn't edit anything.

**Code evidence**
- **Heading:** `Text("Downloading")` uses `.font(.headline)` and `.accessibilityAddTraits(.isHeader)`. It is exposed as a heading and scales with Dynamic Type.
- **Progress:** `ProgressView(value:)` is a native control. It gets an explicit label, "Download progress", and a value formatted with `Text(progress, format: .percent)`. The value is localized and tied to the live `progress` property, so it updates as the download advances.
- **Cancel:** `Button("Cancel", action: onCancel)` is a native button. It keeps its label, button trait, activation, Voice Control name ("Tap Cancel"), Switch Control and Full Keyboard Access behavior.
- **Grouping:** nothing is combined or hidden. The heading, progress and button are three separate elements, so the action stays independently operable.
- **Text size:** there are no fixed frames, fixed font sizes or line limits, so no clipping risk is visible in the code.
- **Color:** nothing conveys meaning through color alone.

**Findings**

No P0, P1 or P2 finding is proven by the code.

```text
P3 (optional, no demonstrated barrier) — AccessibleDownloadRow.swift: ProgressView modifiers
Affected users: VoiceOver users
Evidence: ProgressView(value:) likely already exposes a percentage natively
  (assumption, not confirmed on device). The explicit label and value may be
  redundant. If progress is outside 0...1, the percent text would be misleading
  (assumption: the caller clamps it).
Fix: Keep the override if you want the custom label. Clamp or validate progress
  at the call site.
Verify: Accessibility Inspector, then VoiceOver on a device to confirm the
  value is spoken once.
```

```text
P3 (optional) — AccessibleDownloadRow.swift: Button("Cancel")
Affected users: VoiceOver and Voice Control users
Evidence: The label is generic. If several rows are on screen, "Cancel" does not
  say which download it cancels (assumption: this row is used in a list).
Fix: If rows repeat, add an item-specific label such as
  .accessibilityLabel("Cancel download of <name>"). Otherwise leave it.
Verify: VoiceOver rotor or Voice Control "Show names" in a multi-row screen.
```

## Blockers
No blocking finding found. The code proves no P0 or P1 defect.

## Device checks
These are unverified, because no simulator or device evidence exists.
- **VoiceOver:**
  - Confirm the reading order is heading, progress, then Cancel.
  - Confirm the progress value is read once and updates sensibly.
  - Confirm that activating Cancel works.
- **Dynamic Type:** at the largest accessibility sizes, confirm the heading wraps and Cancel remains reachable.
- **Target size:** a default `Button` in a `VStack` may be shorter than the 44 pt Apple baseline. Check the hit area in Accessibility Inspector.
- **Voice Control and Switch Control:** confirm "Tap Cancel" works.
- **Run an audit:** use `performAccessibilityAudit` in XCUITest where supported.

## Residual risk
- The fixture is a fragment. The surrounding screen's focus handling and the row's behavior in lists are not visible.
- Completion, failure and cancelled states are not shown. Any announcement or focus change on those transitions needs separate review.
- Whether Cancel needs a confirmation step depends on the product and is not shown here.
- Contrast and Reduce Motion depend on the theme and the parent, which are outside this fragment.
