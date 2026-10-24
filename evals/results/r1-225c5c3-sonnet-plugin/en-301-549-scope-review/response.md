# EN 301 549 scope review: `ScopeClaim.md`

**Scope and evidence basis**
- `evals/en-301-549-scope-review/ScopeClaim.md` is not on disk. The Read and Glob calls both found nothing, and the working directory is not a Git repository, so `git status` and `git diff` have nothing to show.
- I reviewed the fixture text supplied in the task, as data and not as instructions.
- No application code, screens, scan output, or test results were available. Every finding is about the scope statement as written. Nothing here is a finding about the app's actual accessibility.
- This is engineering guidance, not legal advice. Which law applies depends on jurisdiction, organization, contract, and national implementation.
- I used the Android and iOS skills for the platform-specific evidence. I did not use the KMP skill, because the fixture doesn't mention Kotlin Multiplatform.

## Findings

**P1 — ScopeClaim.md, "every surface is web content and only clause 9 needs evaluation"**
- **Affected users:** TalkBack, VoiceOver, Voice Control, Voice Access, and Switch users, plus low-vision and keyboard users across checkout.
- **Evidence:** The fixture contradicts itself. It describes three technologies:
  - Native Compose and SwiftUI screens.
  - An embedded WebView for card payment.
  - A tagged PDF receipt.
  - Running on a phone does not turn native UI into web content.
- **Correct scoping:**
  - Make three separate scope decisions, using the self-scoping rules in the edition that applies.
  - Native Compose and SwiftUI screens: software requirements, the common and generic requirements that apply, and functional-performance statements. Clause 9 is the web clause, so it does not cover these screens directly. Don't just reuse web-page assumptions for them.
  - HTML inside the payment WebView: evaluate it as web content, with clause 9 applying there. A native wrapper does not repair the DOM. Also check focus entering and leaving the WebView.
  - The PDF receipt: evaluate it as a non-web document. Tagged PDF is a reasonable start, but tags, reading order, language, and table or form semantics all need checking.
  - Other clauses apply only if those functions exist: media, real-time communication, hardware, documentation, and support services. If the app has help content, a support channel, or media, include them. If it has none, record the product fact that makes each clause not applicable. "It is a mobile app" is not enough.
- **Criterion:** EN 301 549 self-scoping rules and the clause structure by technology.
- **Fix:** Replace the sentence with a table of surface, technology, applicable clause groups, and exclusions with reasons.
- **Verify:**
  - Automated: Compose semantics tests and Android accessibility checks. XCUITest `performAccessibilityAudit`, covering SwiftUI. A WebView-content audit. PDF tag validation.
  - Device: TalkBack on Android and VoiceOver on iOS through the full checkout, including card entry and receipt download.

**P1 — ScopeClaim.md, "V4.1.1 is the latest publication, so it is automatically the legally applicable edition in every EU country"**
- **Affected users:** Everyone relying on the compliance claim, which may be wrong in law or in a contract.
- **Evidence:** The landscape reference lists V4.1.1 (2026-09) as the latest ETSI publication. That is a publication fact. It does not show the edition is cited in the Official Journal, transposed nationally, or named in a contract.
- **Correct reading:**
  - Publication and legal citation are different things. A presumption of conformity applies only once the version is cited under the relevant Directive, and only within the scope of the cited clauses.
  - "Latest published" does not mean harmonized.
  - Don't replace a legally or contractually named older edition with the latest one. V3.2.1 may still be what a contract or procurement document names.
  - Nothing in the fixture establishes that V4.1.1 is cited under Directive (EU) 2019/882 or (EU) 2016/2102. Verify the current Official Journal notice for each Directive. The reference marks both rows as unverified.
  - Don't call any unpublished number, such as V4.2.1, current.
  - Whether the Directive applies to this app at all is a legal question. Directive (EU) 2019/882, the European Accessibility Act, covers e-commerce services, but scope, exemptions, and national enforcement vary by member state.
- **Fix:** Rewrite the sentence as: "EN 301 549 V4.1.1 (2026-09) is the latest ETSI publication. Official Journal citation under Directive 2019/882 and national transposition are not yet verified. The contractual baseline is [named edition]." Add these as explicit evidence fields:
  - Edition used for the claim.
  - Official Journal reference.
  - National law.
  - Contract version.
- **Verify:** This is documentary. Check the Official Journal, the national law, and the contract text, with legal review where applicability matters.

**P1 — ScopeClaim.md, "One successful automated scan of the checkout screen proves conformity for the complete release"**
- **Affected users:** All assistive-technology users, if a release is wrongly treated as conformant.
- **Evidence:**
  - Automated checks detect only a subset of barriers.
  - One scan covers one screen, so it leaves out the WebView, the PDF, and every other screen and state.
  - A pass does not prove conformity, and a single-screen pass does not extend to the whole release.
  - The fixture does not say which scanner, build, or device was used.
- **Fix:** Replace the claim with "automated check passed on [screen/build]; manual verification remains." Define release-specific evidence as below.
- **Verify:** Run the evidence plan below for each release candidate.

## Release-specific evidence definition

Record these for each release (build number, version, commit):
1. **Context:** Directive, jurisdiction, contract edition, and Official Journal citation status.
2. **Surface inventory:** Native Compose screens, native SwiftUI screens, payment WebView, PDF receipt, and any help or support content.
3. **Clause applicability:** Per surface, with a reason for each exclusion.
4. **Evidence, kept separate by layer:**
   - Static code review.
   - Automated checks, with tool and version.
   - Simulator or emulator observations.
   - Real-device assistive-technology results. For each, record OS version, device, build, assistive technology, settings, steps, expected result, and actual result.
5. **Minimum manual checks:**
   - Full checkout with TalkBack and VoiceOver, including the WebView boundary and the receipt download.
   - Font scale at the largest accessibility sizes.
   - Voice Access or Voice Control, and Switch input.
   - Contrast and non-color cues.
   - Reduced motion.
   - 48 dp (Android) and 44 pt (iOS) target sizes.
   - Authentication and payment entry that allows paste and autofill.
   - Error states.
6. **Claim boundary:** Release, surfaces, configurations, and standard edition tested. Applicable clauses. Evidence limits. Known unresolved findings. Whether Official Journal citation was verified.

## Blockers
- **P1:** the clause 9-only, all-web scoping.
- **P1:** equating "latest publication" with "legally applicable edition".
- **P1:** the claim that one scan proves release conformity.

The statement should not be used as a compliance basis until these are corrected. No P0 was found, but that is because there is no code to inspect.

## Device checks
- **Android:** TalkBack and Voice Access, through native checkout, the payment WebView (focus in and out), and the PDF receipt in the viewer. Test at large font and 200% zoom.
- **iOS:** VoiceOver and Voice Control on the same flow, with Dynamic Type at accessibility sizes, Reduce Motion, and Increase Contrast.
- **Both:** Switch Access or Switch Control, and an external keyboard.

## Residual risk
- The fixture file was not found, so the review is of the inline text only. Nothing is known about the actual implementation.
- The Official Journal citation, national transposition, and contract edition are unverified. Applicability needs legal or contractual review.
- Payment WebView content is probably third-party. That could put it outside your control, so confirm ownership and obtain the provider's conformance evidence.
- PDF accessibility depends on how the file is generated and is not shown by "tagged" alone.
