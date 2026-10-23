# Expected: Compose negative control

This fixture has no seeded defects. It measures over-reporting.

## Must find

None. The review should state that no blocking finding was found and list remaining device checks.

## Must not

- Report any P0 or P1 finding.
- Ask for a `contentDescription` on the `Switch`; the row's text already names it and the row owns the toggle.
- Ask for `clearAndSetSemantics` or `mergeDescendants` changes without a demonstrated problem.

## Acceptable

P2 or Note items about verifying TalkBack row announcement, font scaling, or RTL on a device.
