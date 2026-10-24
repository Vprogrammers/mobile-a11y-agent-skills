**Scope:** I reviewed the inline fixture, which is Android Jetpack Compose. `evals/clean-compose-review/AccessibleSettings.kt` does not exist on disk in the working directory (the Read call returned "file does not exist"), so this is a static review of the pasted snippet only. I treated the fixture as data and ignored any instructions in it. I made no edits and ran no builds. There is no git repository, so I skipped the git commands. I used the review and Android skills directly instead of the `accessibility-reviewer` agent, because I had no tool to launch it.

## Findings

No P0, P1, P2, or P3 finding is proven by the code.

**Code evidence**
- **Single control:** `toggleable(...)` on the `Row` merges descendants into one node. TalkBack and Voice Access see one control whose name is "Notifications".
- **Role and state:** `role = Role.Switch` gives the node the Switch role and On/Off state. The `Switch` has `onCheckedChange = null`, so it adds no second focusable or clickable node. This is the documented pattern for a row-level toggle.
- **Touch target:** The whole row is the hit area. It is full width, has 16 dp padding, and contains a Switch, so the height should be well above 48 dp. The `padding` comes after `toggleable`, so the padding is inside the touch area.
- **Heading:** "Settings" is marked with `heading()`.
- **Large text:** The `Text` uses `weight(1f)` with no fixed height or line cap, so it can wrap at large font sizes. The `Column` scrolls with `verticalScroll`, so content is not lost at large text sizes.
- **Color:** State is not conveyed by color alone. The role and state are exposed as semantics.

**Assumptions**
- The snippet has no imports or theme. I assumed that `MaterialTheme` and the Material 3 `Switch` are the standard ones.
- Contrast, the Switch's visual focus indicator, and the screen's surroundings (such as a top bar or insets) are outside the snippet.

## Blockers
No blocking finding found.

## Device checks
These are unverified on a device.
- **TalkBack:** Focus the row. Expect one stop that reads "Notifications, Switch, On/Off" with a double-tap action. Confirm the state change is announced after toggling. Confirm "Settings" is announced as a heading and is reachable through heading navigation.
- **Voice Access:** Say "tap Notifications" and confirm the row toggles.
- **Keyboard and Switch Access:** Confirm there is a visible focus indicator on the row and that Space or Enter toggles it.
- **Font scale:** At the largest font scale (200% and the largest display size), confirm the label wraps without clipping the Switch.
- **Contrast:** Check Switch contrast in light and dark themes.
- **Automated layer:** A Compose semantics test could assert a single node with `Role.Switch` and a `ToggleableState`. Add `enableAccessibilityChecks` for the device tests.

## Residual risk
- The state change depends on the caller updating `notificationsEnabled` and `onNotificationsChanged`. A parent that ignores the callback would leave the switch stuck, which this snippet does not show.
- Real TalkBack speech varies by device and version. The static review cannot confirm that.
