# Review of the audit claim

**Verdict:** The statement can't stand as written. Each sentence either overclaims or is wrong. I did not edit the fixture, and I treated its text as data only.

## Problems and corrections

| Claim | Problem | Supportable wording |
|---|---|---|
| "Automated audits are green. Therefore… compliant." | Automated tools detect only a minority of WCAG failures. They can't judge alt-text quality, focus order, reading order, gesture alternatives, custom-control semantics, or screen-reader or voice-control behavior. "Green" also depends on the tool, rules, and screens covered. | "Automated scans of [scope, tool, version, date] reported no failures in the rules tested. Manual testing results are in [report]." |
| "WCAG 2.2 compliant" | Conformance is per success criterion, per screen or flow, at a stated level (A/AA). WCAG is written for web content, so mobile apps are assessed through W3C's guidance on applying WCAG to mobile (WCAG2ICT-style interpretation). | "Evaluated against WCAG 2.2 Level AA for [flows]. N criteria pass, M fail, K not applicable. Known gaps are listed in [doc]." |
| "EAA, ADA, Section 508, EN 301 549 compliant in every market" | These are different kinds of instruments (see next section). No single test run establishes legal compliance, and "every market" is untestable. | Describe technical conformance only. Leave legal conclusions to counsel and to the conformity process. |
| "EN 301 549 V4.1.1 is newest, so automatically harmonized and creates a presumption of conformity" | Being the newest edition does not make a standard harmonised. A European standard gives a presumption of conformity only when its reference is cited in the Official Journal under the relevant legislation. That presumption covers only the requirements the standard addresses. It is also rebuttable, and it is not "across the EU" in a blanket sense. I can't confirm the citation status of V4.1.1 from here, and the date of this review is not enough to assume it. | "We map to EN 301 549 [version verified against the OJ citation list on date]. Where a presumption applies, it covers only the requirements the standard addresses." |
| "Manual assistive-technology testing is unnecessary" | EN 301 549 and WCAG criteria need human judgment, and real behavior with VoiceOver, TalkBack, Switch Control, Voice Control, and Full Keyboard Access can't be inferred from scans. | Make manual AT testing a release gate for changed or critical flows. |
| "The same report applies to future releases" | A report describes one build. UI, content, and dependency changes invalidate it. | "This report applies to build [version/hash] only." |

## Technical standards vs. legal applicability

- **WCAG 2.2** is a W3C technical specification. It is not law, and it has no certification body.
- **EN 301 549** is a European technical standard for ICT accessibility. It is law-relevant only through citation in EU legislation or implementing decisions, or through contract and procurement requirements. Which edition is cited, and under which instrument, must be checked. The Web Accessibility Directive, which covers public-sector bodies, and the EAA are separate instruments.
- **EAA (Directive 2019/882)** is a law. It applies to specified products and services, with member-state transposition differences, microenterprise exemptions for services, and disproportionate-burden and fundamental-alteration provisions. Whether this app is in scope depends on what it does (for example e-commerce, banking, or e-books) and on the company's size. The standards support a presumption of conformity, and the manufacturer or provider still owns the technical documentation and the conformity assessment.
- **ADA** is a US civil-rights law. Title III has no official technical standard for private-sector mobile apps. WCAG is used through DOJ positions, settlements, and case law. The 2024 DOJ Title II rule adopts WCAG 2.1 AA for state and local governments, which does not extend to private businesses.
- **Section 508** applies to US federal agencies' ICT development, procurement, and use. Vendors usually express conformance through an ACR/VPAT, and the Revised 508 Standards incorporate WCAG 2.0 A/AA. WCAG 2.2 evidence is generally a superset but should be mapped explicitly.

## Evidence that can be maintained per release

1. **Scope record:** build ID, platforms and OS versions, devices, and the list of screens and flows. Mark critical user journeys such as onboarding, sign-in, purchase, and settings.
2. **Automated results:** tool names and versions, rule sets, and raw output stored per build in CI. Treat these as regression signals only.
3. **Manual AT test log:** VoiceOver (iOS) and TalkBack (Android) at minimum. Add Switch Control, Voice Control or Voice Access, keyboard, large text and display scaling, and reduced motion where relevant. Record tester, device, date, steps, and pass/fail per criterion. Run full passes on a schedule (for example each major release) and targeted passes on changed flows every release.
4. **Criterion-level conformance matrix:** each WCAG 2.2 AA criterion, and the EN 301 549 clauses that apply to mobile, with status, evidence link, and known issues. Carry results forward only for unchanged components, with a change-impact note.
5. **Issue register:** known barriers with severity, owner, remediation date, and workaround. This also supports any disproportionate-burden assessment under the EAA.
6. **Accessibility statement and feedback channel:** published for the app and kept in step with the register.
7. **Regulatory applicability memo:** prepared by counsel per market, covering which laws apply, which standard editions are cited, and the date checked. Review it on a schedule and whenever a standard edition or Official Journal citation changes.
8. **Release gate:** no release without a refreshed scope record, no new critical or serious regressions, and sign-off. Automated checks block merges, and the manual log is attached to the release.
9. **ACR/VPAT:** produced from items 1–5 for US federal and procurement needs. Date it and tie it to a version.

## Suggested replacement statement

> "For release [version], we evaluated [flows] on [iOS/Android versions] against WCAG 2.2 Level AA using automated scanning and manual testing with VoiceOver and TalkBack. Results, known issues, and the evaluation date are in [report]. This report applies to this release only. We map our results to EN 301 549 [version] and to Section 508 for procurement purposes. Legal applicability in each market is assessed separately."

I did not research the current Official Journal citation status of EN 301 549 V4.1.1 or the current state of ADA case law. Verify both before publishing anything.
