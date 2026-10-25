I fixed the accessibility defects in `OrderCard` and `AddressForm`, and `./gradlew --console=plain assembleDebug` passes. I didn't run unit tests or add any. I haven't looked for an existing test target, and I didn't run `testDebugUnitTest`.

**What I changed in `src/main/kotlin/evals/fixtures/OrderCard.kt`**
- **`OrderCard`:**
  - **Track button:** The old `clearAndSetSemantics` on the row hid the Track button from TalkBack and Switch Access. I removed it and gave the "open order" click only to the text column. Open and Track are now two separate controls that both stay reachable.
  - **Open target:** The open target is a button with the action label "Open order N". It has a 48 dp minimum height and the default focus and ripple indication, so keyboard users can see where focus is. The old version suppressed the indication.
  - **Track label:** Track now announces "Track order N", so several cards in a list can be told apart. The visible word "Track" is still part of the label for Voice Access.
- **`AddressForm`:** The errors were plain red text with no link to the field. The field now sets `isError`, shows the errors as supporting text so they aren't conveyed by color alone, and exposes them as a semantics error. Focus still moves to the field when errors appear, and editing the street works as before.
- The public function signatures and the open, track and street-edit callbacks are unchanged. I added no dependencies.

**Still needs a real-device check**
- **TalkBack:** Each card should read as an open button followed by a separate "Track order N" button. Focusing the street field should read the error text.
- **Switch Access, keyboard and Voice Access:**
  - Switch Access and Tab navigation should reach both controls, with a visible focus indicator.
  - "Click Track" should work in Voice Access.
- **Display settings:** Check large font, RTL and dark theme.
- **Error timing:** Confirm the error is announced when focus jumps to the field. Compose can't request TalkBack focus directly, so I couldn't verify this without a device.
