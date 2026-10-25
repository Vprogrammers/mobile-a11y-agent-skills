I fixed both composables in `src/main/kotlin/evals/fixtures/OrderCard.kt`. `./gradlew --console=plain assembleDebug` passes. I didn't run `testDebugUnitTest` and didn't add tests, because this project has no existing test target.

**OrderCard**
- **Problem:** `clearAndSetSemantics` on the whole row hid the Track button from TalkBack, Switch Access and keyboard. Opening the order was also only a description on the row, with no visible focus indicator.
- **Fix:** I removed the row-wide semantics override and `indication = null`, and the row is now plain layout. The title and status column is its own clickable button that opens the order. It has a "Open order N" click label, a 48 dp minimum height, and the default focus indication. Track stays a separate `TextButton`, so each action is its own focus stop.
- **Behavior:** Open and Track call the same callbacks as before.

**AddressForm**
- **Problem:** The error messages were loose `Text` nodes next to the field, so nothing tied them to it. Focus moved to the field when errors appeared, but TalkBack wouldn't say what was wrong.
- **Fix:** The field now has `isError`, the messages are its `supportingText`, and I added an `error(...)` semantic with the messages joined. Street editing and the focus request are unchanged.

**Real-device checks**
- With TalkBack, confirm that Open and Track are separate stops and that the street field reads its error text when errors appear.
- Check that Switch Access can reach and activate both actions.
- With a keyboard, Tab to both actions and confirm the focus ring is visible.
- At large font size, check that the card layout and the error text don't clip.

**Limitations:** I haven't checked how the semantics tree and TalkBack actually behave. The errors still appear on screen as red text, but I didn't add an icon or prefix, so that is a possible follow-up.
