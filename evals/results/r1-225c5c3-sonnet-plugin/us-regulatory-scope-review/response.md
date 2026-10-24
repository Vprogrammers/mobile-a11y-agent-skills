# US regulatory scope review: `USComplianceClaim.md`

**Scope.** I reviewed the fixture text supplied in the prompt. `evals/us-regulatory-scope-review/USComplianceClaim.md` does not exist in the working directory, so I could not check the supplied text against the file. This is a statement review, not a code review. No Android, iOS or KMP source is in scope, so I did not invoke the platform skills. I made no edits. This is engineering guidance, not legal advice. The regulatory points come from the skill's `regulatory-landscape.md`, last reviewed 2026-10-24, and should be re-checked against primary sources before publication.

## Findings

```text
P1 — USComplianceClaim.md:sentence 1 ("passed an automated WCAG 2.2 scan, so it complies with ADA Title II, ADA Title III, and Section 508 throughout the United States")
Affected users: Disabled users who rely on the claim. Also the publisher, who carries the risk of a misleading statement.
Evidence: Proven from the text. An automated scan detects only a subset of barriers. Passing it is not proof of WCAG conformance, and conformance is not proof of legal compliance. The statement names three regimes with different coverage and does not say which entity, product or release it covers. Assumption: the scan tool, build and surfaces are unknown because the fixture gives none.
Criterion: Not a WCAG failure. This is a claim-validity problem.
Fix: Replace it with a scoped statement, for example: "Automated checks on release <version> for <surfaces> found no failures against WCAG 2.2 AA tests. Manual and assistive-technology verification is <completed/pending>. Legal applicability has not been determined by this document."
Verify: Record scan tool and version, build, surfaces and results. Then do manual TalkBack and VoiceOver checks on real devices for the critical flows.

P1 — USComplianceClaim.md:sentence 2 ("These laws all require WCAG 2.2 for every native mobile application")
Affected users: Same as above. It also misleads procurement and legal readers.
Evidence: Proven from the text. The statement is inaccurate on each law:
- Title II: the DOJ rule for state and local government web content and mobile apps uses WCAG 2.1 AA, not 2.2. Compliance dates are 26 April 2027 for public entities with a population of 50,000 or more, and 26 April 2028 for smaller entities and special districts, per the April 2026 Interim Final Rule. Both dates need verifying at ADA.gov. The rule applies to covered public entities, including content supplied through contractual or licensing arrangements. It is not a standard for every app.
- Title III: it covers businesses open to the public, but no single WCAG version is federally mandated for every private native app. Contracts, settlements, state law and sector rules may add specific duties.
- Section 508: it covers federal ICT and incorporates WCAG 2.0 A and AA for applicable content. It does not incorporate WCAG 2.2.
Criterion: ADA Title II rule, Section 508 Standards (Access Board), ADA Title III.
Fix: Remove the sentence. If a standard is stated, say: "WCAG 2.2 AA is our engineering baseline. It is not asserted as the legal standard under any of these laws."
Verify: Legal or contract review of the entity category, the applicable standard edition and the contract terms.

P1 — USComplianceClaim.md:sentence 3 ("Section 508 does not require any software interoperability or functional-performance review beyond WCAG")
Affected users: Federal employees and the public who use assistive technology with the app. Also federal buyers.
Evidence: Proven from the text. A native app assessment under Section 508 must not stop at a WCAG checklist. It should self-scope the functional-performance criteria, the software interoperability and application requirements, and the content, documentation and support provisions.
Criterion: Section 508 Standards, including the functional-performance criteria and the software chapter.
Fix: Delete the sentence. State which provisions were evaluated, which were excluded with the product facts behind each exclusion, and any equivalent-facilitation decisions.
Verify: Create a provision-by-provision record for each release. Check assistive-technology interoperability on device with TalkBack and VoiceOver. Add a keyboard or switch-input check on devices where it applies.

P1 — USComplianceClaim.md:sentence 4 ("The same scan proves that third-party SDK screens and future releases are compliant")
Affected users: Users who reach SDK-provided screens such as payment, login, consent or support. Users of later releases.
Evidence: Proven from the text. A scan of one build cannot show anything about different code in a later release. Unless the fixture shows the scan reached SDK screens, it does not prove those screens are covered, and no such evidence is given. SDK screens inside the product remain part of the offered experience. Assumption: whether the SDKs are in scope depends on facts not in the fixture, such as how the SDK is supplied and what UI it renders.
Criterion: Not applicable. This is a claim-validity problem.
Fix: Limit the claim to the tested release and the surfaces listed. Add the SDK screens as separate surfaces with their own evidence, or list them as known limitations. Re-test each release.
Verify: Add per-release regression checks. Add manual assistive-technology passes on the SDK screens, and track vendor accessibility statements.
```

## Context needed to decide applicability

These are facts to gather. They are not conclusions.

1. **Publisher type.** Is it a state or local government entity, a federal agency or contractor, or a private business open to the public? Check also whether the app is supplied to a public entity under a contract or license.
2. **Entity details.** For a public entity: the population category and the compliance date that applies. For a federal context: the procurement terms, any exceptions and any equivalent-facilitation decisions.
3. **Contracts and other duties.** Procurement terms, settlements, state laws and sector rules that name a standard or version.
4. **Technology inventory.** Native screens, embedded WebViews, PDFs and documents, media, support channels and documentation, third-party SDK screens, and whether each is covered.
5. **Platforms and releases.** Android and iOS versions, devices, the framework (Compose, SwiftUI, UIKit, KMP or Compose Multiplatform), and the release or build the claim covers.

## Release-specific evidence to define

Each claim should name the release, surfaces, standard edition and evidence limits, and should keep these layers separate:

- **Static review.** Code and design review notes, with file and symbol references.
- **Automated checks.** Tool name and version, rules enabled, surfaces covered, and failures. Mark them as "automated check passed; manual verification remains".
- **Simulator observations.** OS version and settings tested.
- **Real-device assistive-technology results.** OS, device, build, assistive technology, settings, steps, expected result and actual result. Cover TalkBack, VoiceOver, Voice Control or Voice Access, font scaling, reduced motion, and keyboard or switch input where supported.
- **Critical flows.** Onboarding, sign-in with paste and autofill allowed, core tasks, errors and confirmations, and checkout or payment if present.
- **Third-party and web content.** A separate record for each SDK screen, WebView and downloadable document.
- **Standards map.** Applicable provisions, excluded provisions with reasons, and the edition cited for the claim.
- **Known limitations and open findings.** Include a re-test trigger for every new release.

## Suggested replacement wording (for human and legal review)

> "For release <version>, we ran <tool/version> against <surfaces> using WCAG 2.2 AA as our engineering baseline and found <result>. Manual testing with <assistive technologies, devices> covered <flows>. Third-party screens <included/excluded>. This statement covers only that release. Legal applicability has not been assessed in this document."

## Blockers

Four P1 findings block publication of the statement as written. Every sentence makes an unsupported or incorrect claim.

## Device checks

None can be run from this fixture. For a rewritten claim, record on real devices:
- TalkBack on Android and VoiceOver on iOS.
- Voice Control or Voice Access.
- Large font and display scaling.
- Reduced motion.
- Keyboard or switch input.
- Critical flows, plus the SDK and WebView screens.

## Residual risk

- The fixture file was not found, so I could not check the text against the actual file.
- The scan tool, release, surfaces and SDKs are unknown.
- Title II dates and the 2026 rule status come from the skill reference and need verifying at ADA.gov.
- Legal applicability to the publisher is undetermined and needs legal or contract review.
