# Review of `ScopeClaim.md`

The fixture is unmodified. This is a technical scoping review, not legal advice.

## Verdict
All three conclusions in the claim are unsupported. Each one is corrected below.

## 1. Technology and clause scoping
The claim says "runs on phones, so every surface is web content, so only clause 9." That is wrong. A native app is not web content because of the device it runs on. Each surface should be mapped to a clause by what it is:

| Surface | Primary clauses | Notes |
|---|---|---|
| Compose and SwiftUI checkout screens | **11** (software) | These are native software, not web pages. Clause 11 is the mobile-app counterpart of the WCAG-derived requirements. Include 11.5 (interoperability with platform accessibility services) and 11.7 (user preferences such as text size, contrast and reduced motion), if they apply. |
| Card payment WebView | **9** for the embedded web content, **plus 11** for the host app | The content inside the WebView is web content. The app is still the software that hosts it. Focus handoff, back navigation and AT behavior across the native/web boundary need testing. If a third-party payment provider supplies the page, record who is responsible for it and ask for their conformance evidence. Don't assume it. |
| Tagged PDF receipt | **10** (non-web documents) | Also check how it opens, since in-app viewer behavior and the reading experience affect the result. If it is served and rendered as a web page, clause 9 may apply too. |
| Whole product | **5** (generic requirements) | Check each sub-clause for applicability, such as 5.2 activation of accessibility features and 5.5 operable parts. Record N/A decisions with reasons. |
| Support, help and documentation | **12** | Covers accessible product documentation and support services. |
| Clauses 6, 7, 8, 13 | Likely N/A | Two-way voice, video, hardware and emergency services. Confirm that the app has no calling, video player or similar feature before marking them N/A. |

Clause 9 alone covers only part of the product. It leaves out the native screens, which carry most of the checkout.

## 2. Publication versus legal citation
"Latest publication, so automatically legally applicable in every EU country" confuses two different things.

- **Publication** means ETSI/CEN/CENELEC released a standard version. I have not verified here that V4.1.1 exists or what its status is. Check the ETSI catalogue.
- **Legal citation** means a Commission implementing decision references the standard in the Official Journal of the EU for a particular directive. It does not follow automatically from publication. Which directive applies, such as the Web Accessibility Directive for public bodies or the European Accessibility Act for products and services, determines which edition is referenced.
- **National transposition** and the dates from which obligations apply can differ by member state. A newer edition does not replace the cited one until the citation is updated.

Recommended wording for the statement: name the edition you test against, say why (which legal instrument and citation, as confirmed by your legal or compliance owner), and keep a record of the date you checked. Refer the applicability question to qualified counsel.

## 3. "One automated scan proves conformity for the complete release"
This claim is false, for four reasons:

- Automated tools detect only a minority of WCAG-derived failures. They cannot judge reading order, meaningful labels, focus behavior, error handling or alternative-text quality.
- A single screen is not the checkout flow, let alone the release.
- The scan results apply to one build, not to later ones.
- The scan did not cover the WebView or the PDF.

A scan can be one input among several. It cannot serve as proof of conformity.

## 4. Release-specific evidence
Define the evidence per release, with each item tied to a build identifier.

1. **Scope record:** app version and build number, platforms, minimum OS, a list of the flows and screens in scope, and the standard edition tested against with the reason.
2. **Clause traceability matrix:** every applicable clause (5, 9, 10, 11, 12) marked pass, fail, N/A with a reason, or not tested, with a link to the evidence.
3. **Manual testing:** the full checkout flow (browse, cart, address, payment, confirmation, receipt) with TalkBack on Android and VoiceOver on iOS. Also cover keyboard or Switch Access, Voice Control, 200% text size, display zoom, high contrast, reduced motion and both orientations. Record the devices, OS versions and test dates.
4. **WebView evidence:** the URL or provider and version of the payment content, a focus and AT walkthrough across the native/web boundary, and the provider's own conformance statement.
5. **PDF evidence:** a tag-structure check (for example PAC or Matterhorn Protocol), reading order, language, alternative text, table structure and a screen-reader read-through of the receipt.
6. **Automated results as a supplement:** the tool, rules version, screens covered and findings. Don't present them as evidence of conformity.
7. **Defect log:** open issues with severity, the clause each one maps to, the owner and any workaround, plus a retest record for fixes.
8. **Regression gate:** re-run the evidence on every release that touches in-scope flows, and store each release's results with its build ID.
9. **Sign-off:** the named assessor, the date and the known limitations. Include the third-party dependencies you relied on.

## Suggested corrected statement
> The product is a native Android and iOS app that contains native screens (EN 301 549 clause 11), embedded web content in the payment WebView (clause 9, third-party provider), and a downloadable PDF receipt (clause 10), together with the generic requirements in clause 5 and the support requirements in clause 12. Conformity is assessed per release against [edition, as confirmed by legal/compliance], using the evidence defined above. Automated scans are supplementary.
