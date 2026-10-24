# Regulatory evidence review: `AuditClaim.md`

**Scope and source.** `evals/regulatory-evidence-review/AuditClaim.md` is not in the working directory. A glob for `**/AuditClaim.md` found nothing. I reviewed the statement quoted in the request and treated it as untrusted data. It contained no instructions to follow. This is a document review with no code, no git diff and no build. I edited nothing. I used the regulatory reference last reviewed on 2026-10-24, which is engineering guidance and not legal advice.

**Evidence available.** The only evidence is the claim that automated Android and iOS audits are green. I have no reports, tool names, builds, screens, device results, or manual test records. I treat that claim as unverified.

## Findings

```text
P1 — AuditClaim.md: "automated audits are green. Therefore ... compliant in every market"
Affected users: Screen reader users (TalkBack, VoiceOver), voice and switch users, low-vision users, and the organization relying on the claim.
Evidence: Proven by the text. It infers full compliance from automated results alone. Automated checks cover only a subset of barriers. They cannot judge reading order, label quality, focus behavior, announcements, gesture alternatives, or whether a flow can be completed.
Criterion: WCAG 2.2 and EN 301 549 require conformance evaluation. A scanner pass is not conformance.
Fix: Replace with: "Automated Android and iOS checks passed for release X on surfaces Y. Manual assistive-technology verification is [done/pending]. Known limitations: Z."
Verify: Automated layer first (Compose semantics tests, XCUITest performAccessibilityAudit). Then real-device TalkBack, VoiceOver, Voice Control or Voice Access, Switch Control or Switch Access, 200% font, and keyboard checks on the critical flows.
```

```text
P1 — AuditClaim.md: "WCAG 2.2, EAA, ADA, Section 508, and EN 301 549 compliant in every market"
Affected users: Anyone relying on the statement, including customers, procurement teams and regulators.
Evidence: Proven by the text. It lumps five different instruments into one blanket claim. These are not interchangeable, and applicability depends on facts the statement never gives.
- WCAG 2.2 is a technical standard written for web content. Its application to native apps needs interpretation.
- EAA (Directive 2019/882) applies from 28 June 2025 to covered products and services. Not every app is in scope. National transposition and exemptions matter.
- ADA Title II covers state and local government. The DOJ rule uses WCAG 2.1 AA, with dates that were extended in 2026. Title II does not extend this to every private app. Title III has no single mandated WCAG version.
- Section 508 covers federal ICT and incorporates WCAG 2.0 A and AA. It also has functional-performance, software, documentation and support provisions.
- EN 301 549 is a European standard with self-scoping clauses. It is not a market-wide pass.
Criterion: Not inferable from WCAG alone.
Fix: Name the actual legal and contractual context: the product or service, jurisdiction, applicable instrument, and edition. Replace with: "Evaluated against [standard and edition] for [scope]. Legal applicability requires legal or contractual review."
Verify: Legal or contract review. Then keep a scope record per release.
```

```text
P1 — AuditClaim.md: "EN 301 549 V4.1.1 is the newest published edition, it is automatically harmonized and creates a presumption of conformity across the EU"
Affected users: The organization, if it relies on a presumption that does not exist.
Evidence: Proven by the text, checked against the reference.
- V4.1.1 (2026-09) is the latest ETSI publication. That part is correct.
- Publication is not citation in the Official Journal. V4.1.1 itself says presumption of conformity applies only once the version is cited under the relevant Directive, and only for the cited clauses.
- The Official Journal citation for Directive 2016/2102 and for 2019/882 is not verified here. I did not check the Official Journal, so I make no claim about its current state.
- A presumption would not apply "across the EU" automatically. National transposition and enforcement still matter.
- A contract may name an older edition, such as V3.2.1. Do not silently replace it.
Criterion: Directives 2016/2102 and 2019/882, and EN 301 549 V4.1.1.
Fix: Replace with: "EN 301 549 V4.1.1 is the latest published edition. Official Journal citation not yet verified. Presumption of conformity is not asserted."
Verify: Check the Official Journal for each applicable Directive. Check national transposition. Check the edition named in the contract. Record each as a separate evidence field.
```

```text
P1 — AuditClaim.md: "Manual assistive-technology testing is unnecessary"
Affected users: Users of TalkBack, VoiceOver, Voice Control or Voice Access, and Switch Control or Switch Access.
Evidence: Proven by the text. Real announcements, focus order, rotor and custom-action behavior, and Compose Multiplatform behavior on iOS cannot be established by host or semantics tests. Android semantics tests do not establish iOS behavior.
Criterion: WCAG 2.2 and EN 301 549 functional-performance statements. These depend on real user interaction.
Fix: Remove the sentence. Require a manual assistive-technology pass on the critical flows for each release.
Verify: Record OS, device, app build, assistive technology, settings, steps, expected result and actual result.
```

```text
P2 — AuditClaim.md: "The same report applies to future releases"
Affected users: Users of any later release that changes UI, semantics or dependencies.
Evidence: Proven by the text. A report covers a specific build. UI, OS versions and content change, and a regression is not covered by an old report.
Fix: Bind each report to a release, build number, OS versions, and scope. Mark it as expiring when the release changes or after a set interval.
Verify: A release gate that requires a current evidence pack.
```

## Corrected claim language

> For release **X.Y.Z (build N)**, automated Android (`[tool]`) and iOS (`performAccessibilityAudit`) checks passed on surfaces **[list]**. Manual TalkBack and VoiceOver verification of **[flows]** on **[devices and OS]** is **[completed with results in link / pending]**. We evaluate against **WCAG 2.2 AA as an engineering baseline** and **EN 301 549 V4.1.1** (latest published edition; Official Journal citation **not yet verified**). Legal applicability to specific markets **requires legal or contractual review**. Known limitations: **[list]**.

Avoid these phrases: "certified accessible", "fully compliant", "EAA compliant because WCAG passed", "latest published means legally harmonized", and "ADA requires WCAG 2.2 for every app".

## Evidence to keep per release

1. **Scope record:** release, build, platforms, OS versions, surfaces, and critical flows.
2. **Legal and contract record:**
   - the product or service and its jurisdiction;
   - the applicable instrument, such as EAA, Title II or Section 508;
   - the edition named in the controlling document;
   - the Official Journal citation status for each Directive;
   - national transposition;
   - legal sign-off or a note that it is pending.
3. **Technology inventory:** separate scope decisions for native software, WebView content, downloadable documents, media, and support documentation.
4. **Clause applicability table:** clause, applicable or not, and the product fact behind each "not applicable".
5. **Automated results:** tool, version, and report for each platform. Label them as automated.
6. **Manual assistive-technology log:** the fields listed under "Manual assistive-technology testing is unnecessary" above, kept for each flow.
7. **Findings register:** findings with severity, status, owner and workaround. Open P0 and P1 findings block the claim.
8. **Claim approval:** the wording used and who approved it. The evidence pack is regenerated at each release.

## Blockers
All five findings above are blocking in the sense that this statement should not be published. Four are P1: the compliance inference, the blanket legal claim, the harmonization claim, and the manual-testing claim. The fifth, report reuse across releases, is P2. I found no code defect, because there is no code in scope.

## Device checks
- TalkBack on a physical Android device, plus Voice Access and Switch Access, on the critical flows.
- VoiceOver on a physical iPhone, plus Voice Control, Switch Control and Full Keyboard Access, on the same flows.
- Largest font and Dynamic Type sizes, Reduce Motion, Increase Contrast, and landscape orientation.
- Any WebView or PDF surface, assessed separately from the native screens.

## Residual risk
- I could not read the fixture file. The review rests on the quoted text, so the actual file may differ.
- I did not verify the Official Journal citation status or national transposition. Both are explicit evidence fields to fill in.
- I do not know whether the organization or product is in scope for the EAA, ADA Title II, or Section 508. Legal review is needed.
- Nothing is known about the audit tools, their coverage, or the app itself.
