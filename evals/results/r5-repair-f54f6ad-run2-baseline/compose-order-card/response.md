I fixed the accessibility defects in `OrderCard.kt`, and `./gradlew --console=plain assembleDebug` succeeds. I haven't tested it with TalkBack, Switch Access or a keyboard. The file header says it's generated from `evals/` and to edit the fixture instead. I edited this copy directly, so the change needs porting to the fixture or `generateEvalFixtures` will overwrite it.

**What I changed**

`OrderCard`
- **Track button:** the old `clearAndSetSemantics` on the whole row hid the Track button from accessibility services, so TalkBack and Switch Access couldn't reach it. I removed it.
- **Open order:** the open-order click is now on the summary column only. It has a button role, an "Open order N" click label and merged semantics, so it reads as one item. Track is a separate focus stop next to it.
- **Focus indicator:** I removed `indication = null` and the custom interaction source, so keyboard focus and press states show again.
- **Track label:** the Track button now reads "Track order N" instead of just "Track", so it's distinguishable between cards.

`AddressForm`
- **Error text:** the errors were plain red text outside the field, so they were conveyed by colour alone and weren't tied to the input. They now go in the field's `supportingText` with `isError = true`.
- **Announcement:** the errors sit in a polite live region, and each is prefixed "Error:", so they aren't conveyed by colour alone. The field also gets an `error(...)` semantic that joins all the messages.
- **Unchanged:** the focus-on-error behaviour, the street editing, and the public signatures.

**What needs a real-device check**
- **Track label:** TalkBack may read both "Track order N" and the visible "Track". Check that this isn't redundant.
- **Error announcements:** the `error` semantic and the live region might both announce the same errors. Check the wording isn't doubled.
- **Focus order:** go through the card and form with a hardware keyboard and Switch Access. Confirm the summary and Track are separate focus stops and the focus ring shows.
- **Touch target:** confirm the Track button is at least 48dp.
- **Colour contrast:** the error text colour has only been checked in code, not on screen.
