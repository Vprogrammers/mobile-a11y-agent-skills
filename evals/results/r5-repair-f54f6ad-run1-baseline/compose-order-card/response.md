I fixed the accessibility defects in `OrderCard.kt`, and `./gradlew --console=plain assembleDebug` succeeds. I haven't run it on a device or emulator, so none of this has been tested with TalkBack, Switch Access or a keyboard yet.

The file header says it's generated from `evals/` by `generateEvalFixtures` and that you should edit the fixture instead. I edited this copy directly, so the same changes need to go into the fixture or they'll be overwritten on the next generation.

**`OrderCard`**
- **Track button:** the whole row used `clearAndSetSemantics`, which hid the Track button from TalkBack and Switch Access. I removed that.
- **Open action:** only the text column is clickable now, and it is a separate node from the Track button. It is exposed as a button with the label "Open order N", and the number and status are announced together.
- **Focus indicator:** I dropped `indication = null` and the custom interaction source, so keyboard focus and press feedback are visible again.
- **Track label:** the button's description is now "Track order N", so a list of cards isn't a series of identical "Track" buttons.

**`AddressForm`**
- **Error display:** the errors were loose `Text` lines with no link to the field. They now show as `supportingText` on the field with `isError = true`.
- **Error announcement:** the field's semantics carry the joined error text, so TalkBack reads the errors when focus lands on it. The existing focus-on-error behaviour is kept.

Public signatures and the open, track and street-edit behaviour are unchanged.

**Needs a real-device check**
- **TalkBack:** it should read the error text when focus moves to the street field, with no double announcement from the supporting text plus the error semantics. It should also read "Open order N" and "Track order N" sensibly.
- **Switch Access and keyboard:** both the card and the Track button should be reachable and activatable. Tab order should go card, then Track, and the focus ring should be visible on both.
- **Large font size and display size:** check that the layout holds up with the Track button's text.
