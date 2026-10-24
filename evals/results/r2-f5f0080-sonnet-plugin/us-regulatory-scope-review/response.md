# US regulatory scope review: `USComplianceClaim.md`

**Scope.** I reviewed the fixture text supplied in the prompt. `evals/us-regulatory-scope-review/USComplianceClaim.md` does not exist in the working directory, and a glob for it found nothing. The directory is not a git repository, so the git commands had no effect. I edited nothing and ran no builds.

No Android, iOS, or KMP code is in scope, so I did not invoke `android-a11y`, `ios-a11y`, or `kmp-a11y`. I used the `mobile-a11y-review` skill and its regulatory-landscape reference, last reviewed 2026-10-24. This is engineering guidance, not legal advice.

## Findings

The statement is a single document, and each finding is a claim inside it.

**P1 — claim 1: "Passed an automated WCAG 2.2 scan, so it complies with ADA Title II, Title III, and Section 508 throughout the United States."**
- **Affected users:** Everyone relying on the statement. This includes screen reader, Voice Control, switch, and low-vision users, because a false pass hides real barriers. It also includes the organization, which carries the risk of an overstated claim.
- **Evidence (proven from the text):** The claim moves from an automated scan to legal compliance. Automated checks cannot establish WCAG conformance, so they cannot establish legal compliance. The text names no tool, release, platform, or flow. Applicability of each law is not established.
- **Fix:** Replace the claim with a scoped statement such as: "Automated check passed on release X for surfaces Y. Manual verification [done/remaining]. Applicability requires legal or contractual review."
- **Verify:** Run an automated audit per surface, then do manual TalkBack and VoiceOver passes on real devices.

**P1 — claim 2: "These laws all require WCAG 2.2 for every native mobile application."**
- **Affected users:** Same as claim 1. A wrong baseline also misdirects testing.
- **Evidence (proven against the reference):** The statement is unsupported for all three laws.
  - **ADA Title II:** The DOJ rule for covered state and local government web content and mobile apps uses WCAG 2.1 AA, not 2.2. As of the April 2026 Interim Final Rule, the compliance dates are 26 April 2027 for entities of 50,000 or more people and 26 April 2028 for smaller entities and special districts. Verify these at ADA.gov. The rule applies to public entities. It is not a general rule for every app, though third-party apps offered under a contract or license can fall inside a public entity's covered offering.
  - **ADA Title III:** Businesses open to the public must provide accessible services. No single WCAG version is federally mandated for every private native app. Contracts, settlements, state law, and sector rules may set more specific duties.
  - **Section 508:** It covers federal ICT. It incorporates WCAG 2.0 A and AA for applicable content, not 2.2. A project may adopt 2.2 as its engineering baseline, but it should not describe 2.2 as the edition Section 508 incorporates.
- **Fix:** Separate the legal or contractual requirement from the engineering baseline. For example: "Engineering baseline: WCAG 2.2 AA. Title II (if applicable): WCAG 2.1 AA. Section 508 (if applicable): WCAG 2.0 A/AA plus the other applicable provisions."
- **Verify:** Counsel or the contract owner confirms the controlling standard and version. Then map each test to it.

**P1 — claim 3: "Section 508 does not require any software interoperability or functional-performance review beyond WCAG."**
- **Affected users:** Assistive-technology users, such as switch, voice, and screen reader users, and users with limited vision, hearing, or reach.
- **Evidence (proven against the reference):** This is wrong. A native app assessment must not stop at a WCAG checklist. It must self-scope the applicable functional-performance criteria, software interoperability and application requirements, content, documentation, and support provisions. It must also record the federal or procurement context, exceptions, and equivalent-facilitation decisions.
- **Fix:** Delete the sentence. State which Section 508 provisions were evaluated and which were excluded, with the product fact behind each exclusion.
- **Verify:** Keep a per-provision applicability record, then run real-device assistive-technology checks. Examples are platform accessibility API exposure, compatibility with system accessibility settings, and operation without vision, hearing, or fine motor control.

**P1 — claim 4: "The same scan proves that third-party SDK screens and future releases are compliant."**
- **Affected users:** Users who reach SDK screens, such as payment, consent, login, or support screens. Users of every later release are also affected.
- **Evidence (proven from the text):** A scan reflects one build at one time, so it cannot prove anything about future releases. Whether the scan covered SDK-rendered UI is unknown, and I assume it may not have. Embedded WebView content must be assessed as web content, because native wrappers do not repair the DOM. SDK screens inside the app are part of the product's experience. Third-party content can also fall within a public entity's covered offering.
- **Fix:** Remove the "proves" language. Inventory SDK and WebView screens and either test them or list them as known limitations with vendor evidence. Tie the statement to a release identifier.
- **Verify:** Run a release-gated automated check for each build. Do manual passes on SDK and WebView screens with TalkBack and VoiceOver.

## Context needed to determine applicability

These facts are not in the fixture. All of them are required before anyone can decide which law, if any, applies.

1. **Who operates and offers the app:**
   - Is it a state or local government entity, a vendor to one, a private business open to the public, a federal agency, or a federal contractor?
   - For a public entity: population category and any exceptions.
   - For federal use: the procurement context and contract terms.
2. **Contract, settlement, state law, or sector rules** that name a specific standard or version.
3. **Platforms, OS versions, and framework:** Android, iOS, KMP, Compose Multiplatform, or WebView.
4. **User-facing technology inventory:** native UI, embedded web content, PDFs and documents, media, real-time communication, SDK screens, documentation, and support channels.
5. **Critical flows and sensitive data:** sign-in, payment, and forms.
6. **Release under claim:** version, build, and date.
7. **Exceptions or equivalent-facilitation decisions** already made, and who made them.

## Release-specific evidence to require

Keep each item separate by surface and release. Never merge automated, simulator, and real-device results.

- **Identification:** app version and build, platforms, OS versions and devices, and the date. Record the named standard edition and the basis for choosing it: law, contract, or engineering choice.
- **Applicability record:** one row per provision or clause, marked applicable, not applicable, or unknown. Each row gives the product fact behind the decision and who made it.
- **Static review:** semantics, labels, roles, states, and focus order for each critical flow.
- **Automated checks:** the tool, its version, which screens it covered, and the results. State that manual verification remains.
- **Simulator and emulator observations:** list them separately from device results.
- **Real-device assistive-technology results:**
  - TalkBack and VoiceOver on the critical flows.
  - Voice Control or Voice Access, and switch or keyboard operation.
  - Large text and font scaling, reduced motion, and contrast.
  - Landscape and portrait.
- **Third-party and web surfaces:** an inventory of SDK screens and WebViews. For each one, the test evidence or the known limitation with vendor documentation.
- **Defect register:** open findings with severity, owner, and target release.
- **Claim wording check:** the final statement names the release, surfaces, configurations, standard edition, evidence limits, and any unresolved findings. It contains no phrases such as "fully compliant", "certified accessible", or "proves".

## Suggested replacement wording (for the owner to adapt)

> "Release X.Y (build N) of [app] on [platforms] was evaluated against WCAG 2.2 Level AA as our engineering baseline. An automated check passed on [screens]; manual and assistive-technology verification covered [flows] and is incomplete for [surfaces]. Third-party SDK and web content: [status]. Legal applicability of ADA Title II, Title III, and Section 508 depends on organization, contract, and context and requires legal review. Known limitations: [list]."

## Blockers

All four findings are P1. They are unsupported legal and technical statements that would be published as fact. The statement should not be published as written.

## Device checks

None of the following has been done. This was a text review only.
- TalkBack on Android and VoiceOver on iOS across the critical flows and SDK screens.
- Voice Access or Voice Control, plus switch or keyboard operation.
- Largest supported text size and display zoom.
- Reduced motion and contrast settings.
- WebView screens.

## Residual risk

- The fixture file is missing from the working directory, so I judged the supplied text. If the file differs, the findings may differ.
- The Title II dates and rule status come from the reference file as of 2026-10-24. Confirm them against ADA.gov, because rules can change.
- I have no facts about the app, its operator, or its contracts, so I cannot say whether any of these laws applies. That needs legal or contractual review.
- Any reviewed release will become stale once a new build ships.
