# Regulatory and standards landscape

Last reviewed: 2026-10-24.

This is engineering guidance, not legal advice. Applicability depends on jurisdiction, organization, product, service, contract, and national implementation. Verify current primary sources before making a compliance claim.

## Recommended engineering baseline

Use WCAG 2.2 Level AA as a forward-looking engineering baseline when contract and law do not specify another version. WCAG is technology-neutral but written for web content; use W3C mobile guidance and platform behavior to interpret it for native apps. Do not claim that passing automated checks proves conformance.

Mobile-relevant WCAG 2.2 additions include Focus Not Obscured, Dragging Movements, Target Size (Minimum), Consistent Help, Redundant Entry, and Accessible Authentication. Preserve paste, autofill, password managers, and alternatives to memory or transcription tasks.

Primary sources:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C mobile accessibility: https://www.w3.org/WAI/standards-guidelines/mobile/

## European Union

### European Accessibility Act

Directive (EU) 2019/882 applies from 28 June 2025 to covered products and services, including areas such as consumer banking, e-commerce, electronic communications, and parts of passenger transport. It does not make every mobile app automatically subject to identical requirements. Check national transposition, scope, exemptions, and enforcement.

- Directive: https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng
- Commission overview: https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/european-accessibility-act-eaa_en

### EN 301 549 version status

The latest published version is **EN 301 549 V4.1.1 (2026-09)**, adopted on 24 August 2026. It updates clauses 9, 10, and 11 to align with WCAG 2.2 and adds annexes that map requirements to Directive (EU) 2016/2102 and Directive (EU) 2019/882.

Publication is not the same as citation in the Official Journal of the European Union. V4.1.1 states that presumption of conformity applies only once the version is cited under the relevant Directive and only within the scope of the cited clauses. Before using the standard for a compliance statement, verify:

- the version cited in the Official Journal for the applicable Directive;
- national transposition and enforcement;
- the version named by the contract, procurement terms, or customer policy;
- which self-scoping software, web, document, hardware, and functional-performance clauses apply.

Do not label a draft, work item, or unpublished number such as V4.2.1 as the current standard. Do not silently replace a legally or contractually named older version with the latest publication.

Primary sources:

- EN 301 549 V4.1.1: https://www.etsi.org/deliver/etsi_en/301500_301599/301549/04.01.01_60/en_301549v040101p.pdf
- ETSI Human Factors overview: https://www.etsi.org/technical-groups/hf/
- Previous EN 301 549 V3.2.1: https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf

### Public-sector apps

Directive (EU) 2016/2102 covers public-sector websites and mobile applications. EN 301 549 provides testable ICT requirements, but the latest published edition must not be described as the legally cited edition without checking the Official Journal.

- Directive: https://eur-lex.europa.eu/eli/dir/2016/2102/oj/eng

For native software, inspect applicable EN 301 549 software, functional-performance, and generic clauses rather than mapping only web clauses. Document clause applicability and evidence; do not produce a blanket pass/fail from a code scan.

## United States

### ADA Title II

The Department of Justice rule for state and local government web content and mobile apps uses WCAG 2.1 Level AA, with compliance dates depending on entity size and current rulemaking. Verify dates at ADA.gov before reporting them.

- Rule overview: https://www.ada.gov/resources/2024-03-08-web-rule/
- Current Title II resources: https://www.ada.gov/title-ii-web-rule/

### Section 508

The refreshed Section 508 Standards apply to federal ICT and incorporate WCAG 2.0 Level A and AA requirements by reference, with additional software and functional-performance provisions. A project may adopt a newer WCAG baseline, but do not misstate that as the incorporated legal version.

- US Access Board ICT standards: https://www.access-board.gov/ict/

### ADA Title III and other obligations

Businesses open to the public must provide accessible services, but do not state that one universal WCAG version is federally mandated for every private native app. Contracts, settlements, state laws, procurement terms, and sector rules may impose more specific duties. Ask for legal review when applicability matters.

## Evidence language

Use:

- “supports evaluation against…”
- “finding maps to…”
- “automated check passed; manual verification remains”
- “applicability requires legal or contractual review”
- “latest published version; Official Journal citation not yet verified”

Avoid:

- “certified accessible”
- “fully compliant”
- “EAA compliant because WCAG passed”
- “latest published means legally harmonized”
- “ADA requires WCAG 2.2 for every app”
