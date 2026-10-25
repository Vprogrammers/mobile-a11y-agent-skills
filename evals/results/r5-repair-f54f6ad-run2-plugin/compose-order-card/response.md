I fixed the `OrderCard` and `AddressForm` accessibility defects in `OrderCard.kt`, and `./gradlew --console=plain assembleDebug` succeeds. I didn't add tests or run `testDebugUnitTest`, and I haven't checked any of this on a device.

**`OrderCard`**
- **Track button:** the old `clearAndSetSemantics` on the whole row removed the Track button from the accessibility tree, so TalkBack and Switch Access couldn't reach it. I removed that wrapper.
- **Open action:** it now sits on the text column only, as a single labeled button ("Open order") that reads the order number and status. Track is a separate control, so it keeps its own focus and click.
- **Keyboard focus:** `indication = null` is gone, so keyboard users get the default focus and press indication.
- **Track label:** the button is announced as "Track order N" instead of just "Track". The name still contains the visible word "Track", which Voice Access relies on.

**`AddressForm`**
- **Error text:** errors were loose `Text` nodes with no link to the field. They now show as the field's supporting text, and the field is marked as being in error.
- **Error announcement:** the field also exposes the joined error text through its semantics, so TalkBack reads it with the field.
- **Focus on error:** the existing behavior that requests focus on the field when errors appear is unchanged.

Public signatures and the open, track and street-edit behavior are unchanged.

**Still needs a real-device check**
- With TalkBack, confirm the card reads as two stops (the order, then Track) and that the error is announced when focus lands on the street field.
- With Switch Access, confirm both Open and Track are reachable.
- With a keyboard, confirm Tab reaches both controls with visible focus and Enter/Space activates them.
- With Voice Access, confirm "Tap Track" works.
- Check the layout at large font size and with RTL.

**Limitations**
- The Open tap area is now the text column rather than the whole row, so tapping the padding around the Track button no longer opens the order. Say if you want the whole row to open it.
- I haven't confirmed that TalkBack announces the error on its own when it first appears. Focus moves to the field, but the announcement itself needs the device check above.
