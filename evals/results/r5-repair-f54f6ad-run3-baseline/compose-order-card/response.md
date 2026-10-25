I fixed the defects in `OrderCard.kt`, and `./gradlew --console=plain assembleDebug` succeeds. I haven't run it on a device or emulator.

**What I changed**
- **Track button:** the row used `clearAndSetSemantics`, which hid the Track button from TalkBack and Switch Access. I removed it. Track is now its own focusable action, labelled "Track order N".
- **Open action:** the row had `indication = null`, so keyboard users couldn't see where focus was. I removed that, which restores the default focus and press indication. The row is now marked as a button, and its click label reads "Open order N". The order number and status are read from the row's own text.
- **Address errors:**
  - The street field now sets `isError`, so the error state is announced and not shown by colour alone.
  - Each error is shown as supporting text under the field, so it is tied to the field.
  - I added error semantics carrying the combined error text, so TalkBack reads the errors when it focuses the field.
- **Kept as before:** the public signatures, `onOpen`, `onTrack`, street editing, and the existing behaviour of focusing the field when errors appear. I added no dependencies.

**Needs a real-device check**
- **TalkBack:** the row and Track should be separate stops, and the field should read its errors once, with no double announcement. I did not add a live region, so check whether errors are announced when they first appear.
- **Switch Access and keyboard:** Tab should reach both the row and Track, Enter or Space should activate each, and the focus indicator should be visible.
- **Track label:** its custom label replaces the visible "Track" text. Check that voice control ("click Track") still works.

The file header says it's generated from `evals/` by `generateEvalFixtures`, so a regeneration will overwrite these edits unless the source fixture gets the same changes.
