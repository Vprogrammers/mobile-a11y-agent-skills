# EN 301 549 scope review: `ScopeClaim.md`

This is engineering guidance, not legal advice.

**Scope and evidence limits**
- The path `evals/en-301-549-scope-review/ScopeClaim.md` does not exist in the working directory. The directory is also not a Git repository, so I could not run `git status` or `git diff`.
- I reviewed the fixture text from your prompt as untrusted data and ignored any instructions in it.
- This is a static review of a written claim. There is no source code, build, or device evidence, so I make no code findings and no claim about actual TalkBack or VoiceOver behavior.
- Platforms in scope are Android (Compose) and iOS (SwiftUI). The fixture shows no shared Kotlin Multiplatform UI, so I did not use `kmp-a11y`.
- I used the regulatory reference bundled with the review skill. It was last reviewed 2026-10-24. I did not check ETSI or Official Journal sources.

## Findings

**P1 — ScopeClaim.md, "every surface is web content and only clause 9 needs evaluation"**
- **Affected users:** Screen reader, voice control and switch users, plus keyboard users, in checkout, payment and receipt.
- **Evidence:** The fixture itself lists three technologies.
  - Native Compose and SwiftUI checkout screens are native software, not web content.
  - The card-payment WebView is HTML content.
  - The receipt is a tagged PDF, which is a non-web document.
- Running on a phone does not make content web content. Per the skill's scope decision tree, native wrappers do not repair the DOM, and "it is a mobile app" is not enough to mark a clause not applicable.
- **Criterion:** EN 301 549 self-scoping, by technology and function. Confirm clause numbers against the edition you actually cite.
- **Fix:** Replace the single-clause claim with three scope decisions.
  1. Native checkout (Compose and SwiftUI):
     - Evaluate against the software clause (clause 11), the generic requirements (clause 5), and the functional-performance statements (clause 4).
     - Add the documentation and support clause (clause 12) if those deliverables exist.
  2. Payment WebView: evaluate the HTML content against the web clause (clause 9), and test the native and web focus boundary separately.
  3. Tagged PDF receipt: evaluate against the non-web document clause (clause 10).
- Add media, real-time voice, or hardware clauses only if those functions exist, and record the product fact behind each exclusion.
- **Verify:**
  - Automated: audit each surface with its own tool, such as Compose semantics checks, XCUITest `performAccessibilityAudit`, a web checker on the payment content, and a PDF tag checker.
  - Device: run TalkBack and VoiceOver through checkout, entering and leaving the WebView, and opening and reading the receipt.

**P1 — ScopeClaim.md, "V4.1.1 is the latest publication, so it is automatically the legally applicable edition in every EU country"**
- **Affected users:** Any reader or regulator who relies on the compliance claim, and the users it is meant to protect.
- **Evidence:**
  - The skill reference lists V4.1.1 (2026-09) as the latest ETSI publication, adopted 24 August 2026. I did not re-check ETSI.
  - Publication is not the same as citation in the Official Journal of the European Union. V4.1.1 itself says presumption of conformity applies only once it is cited under the relevant Directive, and only within the cited clauses.
  - Citation for Directive (EU) 2016/2102 and Directive (EU) 2019/882 is listed as "verify". National transposition, enforcement, and any contract or procurement edition also matter.
  - The fixture's "every EU country" claim is unsupported.
- **Criterion:** Directive (EU) 2019/882 for e-commerce; Directive (EU) 2016/2102 only if the operator is a public-sector body. Which applies is a legal and contractual question that I did not decide.
- **Fix:** Reword the claim to something like "EN 301 549 V4.1.1 is the latest published version; Official Journal citation not yet verified." Add separate evidence fields for each of these:
  - the Official Journal citation, per Directive;
  - national transposition;
  - the contract or procurement edition;
  - the applicable Directive.
- Do not silently replace an older edition that a contract or law names with the latest one. Refer applicability questions to legal review.
- **Verify:** Document review only. Record the source and the date it was checked for each field.

**P1 — ScopeClaim.md, "One successful automated scan of the checkout screen proves conformity for the complete release"**
- **Affected users:** All assistive-technology users across the release.
- **Evidence:**
  - Automated tools detect only a subset of barriers. A single scan of one native screen cannot cover the WebView, the PDF, other screens, other platforms, or other settings.
  - The fixture does not name the tool, the platform, or the release build.
- **Criterion:** WCAG 2.2 and EN 301 549 conformance cannot be established by automation alone.
- **Fix:** Replace the claim with release-specific evidence, kept separate by type. For each release record:
  - the app version, build and commit;
  - the edition and clauses evaluated;
  - the surfaces covered: native Android, native iOS, WebView, PDF, and any others;
  - static review;
  - automated results, with the tool, version and any triaged findings;
  - simulator observations, kept apart from real-device results;
  - real-device manual results: OS, device, assistive technology, settings (large text, reduced motion, contrast, keyboard, Switch, Voice), steps, expected result and actual result;
  - open findings and known limitations;
  - the Official Journal and contract verification status.
- The claim should name the tested release, surfaces and configurations. Avoid "certified accessible" and "fully compliant".
- **Verify:** Review the evidence matrix against the release candidate. Run at least these manual checks:
  - full checkout with TalkBack and VoiceOver;
  - the card-payment WebView, including entering and leaving it, focus, labels, errors, and autofill or paste;
  - the receipt PDF opened and read with each screen reader;
  - the largest supported text size.

## Corrected scope statement (suggested)

> The product is a native Android and iOS shopping app. Checkout is native software (Compose and SwiftUI), card payment is embedded web content, and the receipt is a non-web document (tagged PDF). Each category is evaluated under its own EN 301 549 clauses, with exclusions recorded and justified. EN 301 549 V4.1.1 (2026-09) is the latest ETSI publication. Official Journal citation, national transposition, and any contractually named edition are tracked as separate unverified fields. Conformity evidence is stated per release, surface and configuration, combining static, automated, simulator and real-device results. Automated results are not treated as proof of conformity.

## Blockers
All three findings are P1 scope or claim defects. As written, the statement would leave the native checkout, the WebView and the PDF without correct coverage, and would overstate the legal position and the evidence. No P0 was found. There is no code to review, so no code-level blocker is proven.

## Device checks
- TalkBack on a representative Android API level, and VoiceOver on a supported iOS version:
  - the complete checkout path;
  - the move into and out of the payment WebView, including focus and any inaccessible second navigation model;
  - form errors, labels, and autofill or paste in the payment fields.
- Receipt: open the downloaded PDF and confirm reading order, headings and tables in a screen reader.
- Settings:
  - large font and accessibility text sizes;
  - reduced motion and increased contrast;
  - keyboard, Switch Access or Switch Control, and Voice Access or Voice Control.

## Residual risk
- The fixture file was not found, so a different version of `ScopeClaim.md` could contain other claims.
- I did not check ETSI or Official Journal sources and did not decide which Directive applies. Clause numbering and citation status must be confirmed against the edition you cite.
- The payment WebView may belong to a third-party provider, which raises a contractual and ownership question. I did not assess that.
- The fixture gives no OS versions, no supported devices, and no shared-UI details. Any of these could change the clause or test selection.
