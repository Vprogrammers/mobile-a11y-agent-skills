# Expected: Android Compose checkout review

## Must find

| ID | Location | Min severity | Evidence the finding must contain |
|---|---|---|---|
| `card-number-logged` | `CheckoutScreen`, card field `onValueChange` | P0 | Card number is written to logcat; remove logging of payment data. |
| `overlay-not-modal` | `ConfirmOverlay` | P1 | Content behind the overlay stays reachable; use a platform dialog or modal/pane semantics and restore focus on dismissal. |
| `close-icon-unlabeled` | Close `Icon` with `clickable` | P1 | No accessible name or button role; target is 24 dp, below 48 dp. Use `IconButton` with a description. |
| `swipe-only-remove` | `CartLineRow` drag gesture | P1 | Removal is gesture-only; add a visible control or custom accessibility action. |
| `card-field-no-label` | Card `OutlinedTextField` | P1 | Placeholder disappears on input; add a persistent `label`. Autofill content type is a valid addition. |
| `fixed-height-text` | `CartLineRow` title `Modifier.height(20.dp)` | P1 | Text clips at large font scales; use `heightIn(min = …)` or no fixed height. |
| `unstable-keys` | `itemsIndexed(key = index)` | P2 | Index keys move focus and state after removal; key by `line.id`. |
| `cart-duplicate-description` | Cart header `Row` | P2 | Icon description repeats visible text; set the icon description to `null`. |

## Must not

- Ask for the overlay to be fixed by moving TalkBack focus with `FocusRequester` alone.
- Treat the merged-tree output of a Compose test as proof of TalkBack navigation.

## Device checks expected

TalkBack navigation through the overlay, Switch Access or Voice Access for removal, and 200% font scale.
