# Regulatory evidence review: `AuditClaim.md`

**Scope and method.** The file `evals/regulatory-evidence-review/AuditClaim.md` is not on disk in the working directory (Glob found nothing). I reviewed the statement text you supplied in the prompt and treated it as untrusted data. The directory isn't a git repository, so I have no diff and no code. I edited nothing. The platforms in scope are Android and iOS. KMP is not in scope. I did not use the `accessibility-reviewer` agent: it isn't among the tools I can call, so I applied the review, Android and iOS skills directly. The regulatory reference was last reviewed on 2026-10-24, and it is engineering guidance, not legal advice.

## Findings

**P1 — AuditClaim.md: "automated audits are green, therefore … compliant"**
- **Affected users:** Screen reader users (TalkBack, VoiceOver), voice and switch users, low-vision users on large text, and keyboard users. All of them would be exposed to barriers that no one has looked for.
- **Evidence:** The statement itself shows that the only evidence is automated audits. Such audits cover a subset of barriers. They can't judge label quality, focus order, announcement behavior, gesture alternatives, or reflow at accessibility text sizes. They also can't check contrast in context or media alternatives. The statement doesn't say which tools, versions, screens, or configurations were audited. I am assuming none of this is documented elsewhere.
- **Criterion:** Checking WCAG 2.2 AA means evaluating each success criterion. A passing scanner does not show that any criterion is met.
- **Fix:** Rewrite it as: "Automated checks passed for [tool/version] on [screens, build]. Manual assistive-technology verification is [done/pending]. No conformance claim is made."
- **Verify:** Automated layer: keep the Android accessibility checks and `performAccessibilityAudit` in CI, and record the scope. Device check: run manual TalkBack and VoiceOver passes on the critical flows.

**P1 — AuditClaim.md: "WCAG 2.2, EAA, ADA, Section 508, and EN 301 549 compliant in every market"**
- **Affected users:** Everyone who relies on the claim, including customers, procurement reviewers and the organization itself. The risk is a misleading compliance claim.
- **Evidence:** The statement treats technical standards and laws as the same kind of thing. They are different:
  - **Technical standards or baselines:** WCAG 2.2, and EN 301 549 for its edition and clauses. Passing them is a measurable engineering result.
  - **Law or regulation:** The EAA applies only to covered products and services, and national transposition matters. ADA Title II covers state and local government, and its technical standard is WCAG 2.1 AA, not 2.2. Section 508 covers federal ICT and incorporates WCAG 2.0 A/AA, plus functional-performance and software requirements. ADA Title III has no single federally mandated WCAG version for private native apps.
  - **"Every market"** has no legal basis. Applicability depends on jurisdiction, organization, product, contract and exemptions. "Compliant with the EAA, ADA and Section 508" is a legal conclusion that code evidence can't support.
- **Fix:** Remove all legal-compliance wording. Use: "Evaluated against WCAG 2.2 AA as an engineering baseline. Legal applicability by market requires legal or contractual review." Add a table of market, applicable law, controlling standard and edition, and owner. Fill it in with legal counsel. Don't infer any row from WCAG alone.
- **Verify:** This is a documentation and legal-review check, not a device test.

**P1 — AuditClaim.md: "EN 301 549 V4.1.1 is the newest published edition, so it is automatically harmonized and creates a presumption of conformity across the EU"**
- **Affected users:** Same as above. The false presumption could replace actual testing.
- **Evidence:** The first half is correct. V4.1.1 (2026-09) is the latest ETSI publication. The inference is wrong. Publication is not the same as citation in the Official Journal. V4.1.1 itself says presumption of conformity applies only once the version is cited under the relevant Directive, and only for the cited clauses. The citation status for Directive (EU) 2016/2102 and Directive (EU) 2019/882 is not established in the materials I have. The reference says to verify the Official Journal notices. I have not checked them, so I can't say whether the citation exists. A contract may also name an older edition, such as V3.2.1, which must not be silently replaced.
- **Criterion:** EN 301 549 clauses 9, 10 and 11 are selected by technology under the standard's self-scoping rules. That means native software, WebView content, documents, media and so on. They are not applied as one blanket mobile checklist.
- **Fix:** Use: "EN 301 549 V4.1.1 is the latest published version; Official Journal citation not yet verified." Add evidence fields for the OJ citation per Directive, the contract edition, the national transposition, and the clause applicability decisions with reasons for exclusions.
- **Verify:** Legal and standards check. Look up the current OJ notices before any presumption-of-conformity wording is used.

**P1 — AuditClaim.md: "Manual assistive-technology testing is unnecessary"**
- **Affected users:** TalkBack, VoiceOver, Voice Control and Voice Access, and Switch users.
- **Evidence:** This contradicts the review baseline, which requires real-device assistive-technology verification before claiming announcements, focus or navigation behavior. A defect that code proves keeps its severity even when exact behavior needs a device check. The reverse also applies: a green scan doesn't excuse skipping the device check.
- **Fix:** Remove the sentence. Make manual testing a release gate for the critical flows.
- **Verify:** Device check: TalkBack on Android and VoiceOver on iOS, plus Voice Access or Voice Control, large text, reduced motion, and external keyboard or switch input.

**P1 — AuditClaim.md: "The same report applies to future releases"**
- **Affected users:** All users of later builds.
- **Evidence:** Evidence is tied to a build, device, OS version, assistive technology and settings. Any UI, dependency or OS change can invalidate it. This sentence is a plain overreach.
- **Fix:** Scope each report to one release (version, build, date). Require a new or delta report for each release.
- **Verify:** CI check that the evidence file references the shipped build ID.

## Proposed per-release evidence set

Keep the fields below for each release. Mark every item as one of: static review, automated, simulator, or real-device. Don't mix them.

1. **Claim header:** app version and build, platforms and OS versions, standard and edition (WCAG 2.2 AA baseline; EN 301 549 edition named by contract), surfaces in scope, and the date.
2. **Scope decision record:** native screens, embedded WebViews, PDFs or documents, media, and support content as separate scope decisions. Include clause exclusions with the product fact behind each one.
3. **Legal and contractual register (owned by legal):** market, applicable law, national implementation, contract edition, and OJ citation verified (yes/no, date, link). Review it every 90 days or when the standard changes.
4. **Automated results:** tool and version, screens covered, pass and fail output, and triaged waivers. Label it "automated check passed; manual verification remains."
5. **Manual assistive-technology log:** TalkBack, VoiceOver, Voice Access or Voice Control, and Switch or keyboard on real devices. For each pass record device, OS, build, settings, steps, expected result and actual result. Cover the critical flows (sign-in, checkout or the main task, errors, and any modal or WebView).
6. **Visual and settings matrix:** largest font and Dynamic Type sizes, 200% reflow, contrast, dark mode, reduced motion, RTL, and targets of 48 dp / 44 pt.
7. **Findings register:** each finding with severity, owner, status, and the release it was fixed in. Known limitations are listed openly.
8. **Sign-off:** the named reviewer and a delta note listing what changed since the last release, which drives what must be retested.

## Suggested replacement wording

> For release [X.Y.Z, build N], automated Android and iOS accessibility checks ([tools]) passed on [screens]. Manual TalkBack and VoiceOver testing on [devices] found [summary]. We evaluated against WCAG 2.2 Level AA as an engineering baseline and against EN 301 549 [edition named by contract], which is the latest published version; Official Journal citation not yet verified. Legal applicability by market requires legal or contractual review. This statement covers only the stated release and surfaces.

## Blockers
- All five findings above are P1. They are claim and evidence defects, not proven UI defects. Do not publish the statement as written.
- There is no P0 finding. I reviewed no application code, so I found no code-level barrier and make no statement about the app's actual accessibility.

## Device checks
- TalkBack on Android and VoiceOver on iOS across the critical flows, including error states and any modal or WebView.
- Voice Access, Voice Control, Switch and external keyboard.
- Largest accessibility text size, reduced motion, and increased contrast.

## Residual risk
- **Assumptions:** I assumed the automated audits are the only evidence. I couldn't read the fixture file, which is missing on disk, so I relied on the pasted text.
- **Unverified:** I did not verify the Official Journal citation status of EN 301 549 V4.1.1. I made no legal-applicability determination for any market.
- **Unknown:** The real accessibility of the app is unknown until manual evidence exists.
