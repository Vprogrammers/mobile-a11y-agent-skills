# US regulatory scope review: `USComplianceClaim.md`

This is a technical and documentation review, not legal advice. Have counsel confirm applicability and the wording of any public statement.

## Corrections to unsupported statements

| Claim in fixture | Problem | Supportable replacement |
|---|---|---|
| "Passed an automated WCAG 2.2 scan, so it complies with ADA Title II, ADA Title III, and Section 508." | An automated scan covers only a subset of WCAG success criteria. It can't show conformance, and it can't show legal compliance. The ADA doesn't contain a technical standard that a scan result satisfies. | "An automated WCAG 2.2 scan of [release/build, date, tool and version, screens covered] found [N] issues. Manual and assistive-technology testing is [completed/in progress/not yet done]." |
| "Complies with ADA Title II, Title III, and Section 508 throughout the United States." | These laws apply to different entities and contexts, and the claim treats them as one. Title II covers state and local governments. Title III covers places of public accommodation. Section 508 mainly covers federal agencies' own ICT and federal procurement. Many apps fall under only one of these, or none directly. | Name only the frameworks that apply to the product and its context, after that is determined. Otherwise say which standard the product was tested against. |
| "These laws all require WCAG 2.2 for every native mobile application." | This is inaccurate. The DOJ's Title II web and mobile app rule (2024) adopts WCAG 2.1 Level AA, not 2.2, and it applies to covered public entities, with phased compliance dates. Title III has no regulation that names a technical standard. WCAG is commonly used as a benchmark in settlements and litigation, but it isn't mandated by the statute. Section 508 (Revised 508 Standards) incorporates WCAG 2.0 A/AA by reference for web content and software, and it adds other requirements. Verify current rule text and dates before publishing. | "WCAG 2.2 AA is the accessibility target the team chose. It's not stated as a legal requirement." Cite the specific legal standard only where it applies. |
| "Section 508 does not require any software interoperability or functional-performance review beyond WCAG." | This is wrong. The Revised 508 Standards include Chapter 5 (software), which covers interoperability with assistive technology, platform accessibility features, and user preferences. They also include Chapter 3 functional performance criteria and Chapter 6 support documentation and services. WCAG doesn't replace any of these. | State that 508 conformance is assessed against the Chapter 3, 4, 5, and 6 provisions that apply, which is commonly documented in an Accessibility Conformance Report (ACR/VPAT). |
| "The same scan proves that third-party SDK screens and future releases are compliant." | A scan is a point-in-time test of the screens it covered. It says nothing about screens it didn't reach, such as SDK-rendered UI, webviews, or login and payment flows. It also says nothing about later builds. A "proves" claim has no basis here. | "Results apply only to build [X]. Third-party components [were/were not] tested. Each release is re-evaluated." |

## Context needed to determine applicability

Collect these facts before anyone decides which laws apply:

1. **Entity type.** Is the owner or operator a state or local government (Title II), a private business that is a place of public accommodation (Title III), a federal agency, or a vendor selling to federal agencies (Section 508 via procurement)?
2. **Who uses the app, and how.** Is it public-facing or internal? Is it offered on behalf of a public entity? Is it used by employees (Title I and Section 504 may matter) or by customers?
3. **Nexus to a physical place or service.** Which services or goods the app offers, and how they relate to a business's physical locations. This is relevant to Title III case law, which differs by jurisdiction.
4. **Contracts and funding.** Federal contracts, federal funding (Section 504), or state procurement requirements that name a standard.
5. **Dates.** Which Title II compliance date applies, based on the entity's population size, and the release date relative to it.
6. **Scope of the claim.** Platforms (iOS, Android), app versions, locales, and which features are in or out.
7. **Third-party content.** SDKs, webviews, embedded payment or identity flows, and who controls them contractually.
8. **State and local laws.** Other US laws that may apply, such as the Unruh Act (California) and similar state statutes.
9. **Intended use of the statement.** Marketing, a VPAT/ACR, a procurement response, or a public accessibility page. The wording requirements differ.

## Release-specific evidence

Tie evidence to each release (version, build number, and date). Prior results don't carry over.

- **Identification:** app version and build, OS versions and devices tested, and the test date range.
- **Scope:** a list of screens and flows tested, with the criteria for choosing them and the exclusions, including third-party screens.
- **Automated results:** tool name and version, rule set, raw output, and triage of each finding (fixed, false positive, or open).
- **Manual testing:** a check of each applicable WCAG success criterion, including those scans can't test, such as meaningful labels, focus order, and error identification.
- **Assistive technology testing:** results with VoiceOver, TalkBack, Switch Control, Voice Control, and larger text or display scaling. Include the AT versions.
- **Section 508 mapping, if relevant:** a completed ACR covering Chapters 3, 4, 5, and 6. This includes interoperability with platform accessibility services, functional performance criteria, and support documentation.
- **Third-party components:** vendor ACRs or test results for SDKs, the contract terms covering accessibility, and the remediation plan for any gaps.
- **Defects:** open issues with severity, owner, and target release, plus the known limitations disclosed in the statement.
- **Release gate:** sign-off that regression testing passed for this build, and a record that the statement was reviewed against the evidence.
- **Feedback and conformance contact:** a working channel for accessibility feedback, and the response process.

## Suggested replacement statement

> "We aim to make this app conform to WCAG 2.2 Level AA. For version [X] (tested [date]), we ran automated scans and [manual and assistive technology testing on iOS/Android]. Known limitations: [list, including third-party screens not yet evaluated]. We re-evaluate each release. Contact [address] for accessibility feedback."

Any legal-compliance claim should be added only after counsel has reviewed it against the applicability facts above.
