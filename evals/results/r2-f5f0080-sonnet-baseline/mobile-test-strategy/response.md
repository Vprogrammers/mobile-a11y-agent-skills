# Checkout accessibility test strategy

I worked from the requirements as quoted in your message and didn't open the file. I created no files and edited nothing.

## Layer assignments

| # | Assertion | Narrowest reliable layer | What the test checks |
|---|---|---|---|
| 1 | Shared KMP validation rejects an empty cardholder name | **KMP unit test** (`commonTest`) | `validate("")` and whitespace-only input return a typed error such as `EmptyCardholderName`. Include a valid name as a control. Assert the error code, not a localized string. |
| 2a | Compose exposes the validation error | **Compose UI test** (`runComposeUiTest` or the JVM/instrumented rule) | Submit an empty name. Assert that the error node is in the semantics tree, with the error text or `error()` semantics on the field. Also assert the field's `contentDescription` or `stateDescription`. |
| 2b | SwiftUI exposes the validation error | **XCTest/XCUITest on the simulator**, or a view-inspection unit test | Submit an empty name. Assert the error element exists, with the expected `accessibilityLabel` or `accessibilityValue` on the field. |
| 2c | Both platforms map the same shared error code to a user-facing message | **Platform unit tests** | The mapper turns `EmptyCardholderName` into a string resource. This stops the two UIs drifting apart. |
| 3 | Custom slider supports equivalent increment/decrement | **Compose UI test and XCUITest** | Compose: `performSemanticsAction(SetProgress)` or the custom increment/decrement actions, then assert the value and range semantics. iOS: `adjustable` trait, then `element.adjust(toNormalizedSliderPosition:)` or the increment/decrement calls. Assert that the value changes by the same step in both directions and clamps at the min and max. The step logic itself belongs in a **KMP unit test**. |
| 4a | Overlay traps focus | **Compose UI test and XCUITest (structural)** | While the overlay is open, background nodes are not in the accessibility tree. Compose: assert background nodes are absent or hidden. iOS: assert `accessibilityViewIsModal` or equivalent, and that background elements are not queryable. |
| 4b | Overlay restores focus on dismiss | **Same UI tests, partial** | Assert that the triggering control is focused or focusable after dismiss. Compose: `assertIsFocused` where the focus model applies. iOS: XCUITest `hasFocus` is unreliable for VoiceOver focus, so treat that check as a smoke test only. |
| 5 | Payment details never appear in screenshots, logs, or artifacts | **Static check, plus a CI artifact scan** | Tests use only synthetic, clearly fake card data (such as a known test PAN). The app masks or secures payment fields (`FLAG_SECURE` on Android, a redaction view on iOS). A CI step greps logs, XCResult/JUnit output, and screenshots-as-text for the fake PAN and CVV patterns and fails on a hit. Disable screenshot-on-failure for the payment screens. A lint rule can ban logging payment model types. |
| 6 | CI proves exact TalkBack/VoiceOver announcement text | **Not achievable in CI as stated.** Split it into two parts (see below). | |

## Requirement 6: push back on the wording

CI can't observe what TalkBack or VoiceOver actually speaks. Screen readers build the spoken output from labels, roles, state, hints, user settings, OS version, and locale. Emulators and simulators don't run the real speech pipeline.

I'd propose this replacement:

- **In CI:** assert the *inputs* to the announcement: the accessibility label, value, state, role, and error text, plus any live-region or announcement string passed to the platform API. On Android, that means semantics `LiveRegion`. On iOS, it means the string handed to `UIAccessibility.post(.announcement)`. Inject a fake announcer so a test can assert on it.
- **Manually, on real devices:** confirm that what's spoken is understandable and matches the intent.

Ask Product to accept "the correct strings are supplied to the accessibility APIs" as the CI claim, not "the exact spoken text".

## What still needs a real device with assistive technology

Run these on at least one physical Android device with TalkBack and one physical iPhone with VoiceOver. Record the results in a manual checklist.

1. **Spoken output of the validation error.** Is it announced when it appears, without moving focus? Is it announced once, not twice? Does the field read as invalid?
2. **Slider.** TalkBack's volume-key and swipe-up/down adjustment, and VoiceOver's swipe-up/down adjustable gesture. Check that the spoken value and units are sensible.
3. **Overlay focus.**
   - Does screen-reader focus move into the overlay on open?
   - Can swipe navigation or Explore by Touch reach background content?
   - Does the VoiceOver two-finger scrub (escape) dismiss it?
   - Does the Android back gesture dismiss it?
   - Does focus land back on the trigger after dismiss? This is where simulators and emulators are least reliable.
4. **Payment fields.** Are masked values read out loud? Does the OS autofill or password-manager UI behave correctly? Does the app switcher hide the screen?
5. **Settings variations.** Large font and display size, bold text, reduced motion, and switch access or full keyboard access. One pass each is enough.

## Minimal CI shape

- **Per PR (fast):** KMP unit tests, the platform mapper tests, Compose semantics tests on the JVM or an emulator, and an iOS simulator XCUITest suite. Include the artifact secret scan.
- **Pre-release (manual):** the device checklist above, owned by QA, with a sign-off recorded per release.

I'd leave out automated screenshot-diffing of the payment screens and any attempt to scrape screen-reader speech, because both are costly and either leak data or give false confidence.
