# Scope review of `ScopeClaim.md`

The fixture was not edited. This is a technical review, not legal advice.

## 1. Technology and clause scoping

The claim that every surface is web content and only clause 9 applies is wrong. Running on a phone does not make something web content. EN 301 549 scopes by what each component is, so the app needs to be split up:

| Component | Technology | Clauses to evaluate |
|---|---|---|
| Compose and SwiftUI checkout screens, and the rest of the native app | Non-web software | **Clause 11** (software), which applies WCAG-derived criteria to non-web software. Also 11.5 (assistive technology interoperability, platform accessibility services), 11.7 (user preferences) and 11.8 if any authoring function exists. |
| Card payment in an embedded WebView | Web content hosted inside native software | **Clause 9** for the rendered content, plus **clause 11** for the host app's behaviour. That includes focus entering and leaving the WebView, back navigation, and screen-reader traversal across the native/web boundary. Confirm the exact applicability wording against the edition you are assessing against. |
| Tagged PDF receipt | Non-web document | **Clause 10**. Tagging helps, but it is not proof of conformity. Check reading order, language, table and heading structure, alt text, and contrast. |
| Whole product | | **Clause 4** (functional performance statements) and **clause 5** (generic requirements, such as 5.2 and 5.4, where relevant). Also **clause 12** (documentation and support services). Clause 6 applies if there is voice chat or calling. Clause 7 applies if there is video. |

Clause 8 (hardware) is out of scope for an app alone.

## 2. Publication is not legal citation

- An ETSI publication of a standard does not make it the legally applicable edition. "Latest" does not mean "applicable".
- For EU purposes, the edition that gives a presumption of conformity is the one whose reference is published in the Official Journal of the EU, under a Commission implementing decision. That is a separate step from ETSI publishing it. Which instrument is relevant depends on the legal regime: for example, public-sector apps fall under Directive (EU) 2016/2102, and products and services under the European Accessibility Act (Directive (EU) 2019/882).
- Member States also transpose and apply these rules nationally, so "automatically applicable in every EU country" is unsupported.
- I could not verify that V4.1.1 exists or its citation status. The fixture asserts it, and I have not confirmed it. Before relying on any edition, check ETSI's catalogue and the current OJEU harmonised-standards listing. Refer the question of which edition legally applies to counsel or the relevant authority.
- Recommended wording: "Assessed against EN 301 549 V[x.y.z]. Legal applicability to be confirmed per market."

## 3. Release-specific evidence

One automated scan of one screen supports none of the conformity claim. Automated tools detect only a minority of issues, and a single screen does not represent the release. Evidence should be tied to a specific release and include:

- **Identification:** app version and build numbers (Android and iOS), standard edition and version, test dates, and tester names.
- **Environment:** OS versions and devices tested. Assistive technology: TalkBack, VoiceOver, Switch Access or Switch Control, Voice Control or Voice Access. Settings: large text and display zoom, reduced motion, orientation, contrast and dark mode.
- **Coverage:** every user flow in the release (browse, cart, checkout, payment WebView, receipt download and open, errors, authentication), not only the checkout screen. A per-criterion result table with pass, fail, or not applicable, and a justification for each.
- **Method:** manual and AT testing as the primary evidence. Automated scans (Accessibility Scanner, Xcode Accessibility Inspector, axe for the WebView) as supplementary, with the reports attached. PDF checks with a PDF/UA tool such as PAC or Matterhorn plus manual screen-reader review.
- **Third parties:** accessibility evidence or a conformance report from the payment provider for the WebView content, and confirmation that it matches the version in use.
- **Residual risk:** known failures with severity, owners, and remediation dates. Re-run the evidence for each release or when affected components change, and record regression results.

## Corrected statement (draft)

"The release comprises native software (clause 11), embedded web content (clause 9), and a PDF document (clause 10), plus the generic, documentation and support clauses that apply. Conformity is assessed per release against the identified EN 301 549 edition using manual and assistive-technology testing, supplemented by automated tools. Legal applicability is confirmed separately."
