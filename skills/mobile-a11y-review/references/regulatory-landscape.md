# Regulatory and standards landscape

Last reviewed: 2026-10-24.
Review interval: 90 days.

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

| Status item | Verified state on 2026-10-24 |
|---|---|
| Latest ETSI publication | EN 301 549 V4.1.1 (2026-09) |
| Publication status | Published by ETSI |
| Citation for Directive (EU) 2016/2102 | Verify the current Official Journal notice before making a claim |
| Citation for Directive (EU) 2019/882 | Verify the current Official Journal notice before making a claim |
| Contract or procurement baseline | Use the edition named by the controlling document |

Treat every Official Journal and contract row as an explicit evidence field in a compliance report. Never infer it from the ETSI publication row.

Publication is not the same as citation in the Official Journal of the European Union. V4.1.1 states that presumption of conformity applies only once the version is cited under the relevant Directive and only within the scope of the cited clauses. Before using the standard for a compliance statement, verify:

- the version cited in the Official Journal for the applicable Directive;
- national transposition and enforcement;
- the version named by the contract, procurement terms, or customer policy;
- which self-scoping software, web, document, hardware, and functional-performance clauses apply.

Do not label a draft, work item, or unpublished number such as V4.2.1 as the current standard. Do not silently replace a legally or contractually named older version with the latest publication.

#### Scope decision tree

Use the standard's self-scoping rules before selecting clauses. Do not start from a fixed “mobile app checklist.”

1. **Establish the legal and contractual context.** Record the covered product or service, applicable Directive or procurement rule, jurisdiction, national implementation, exemptions, contract version, and the EN 301 549 edition cited for the claim.
2. **Inventory every user-facing technology.** Separate native software, embedded web content, non-web documents, media, real-time communication, hardware, support documentation, and support services. One product can contain several categories.
3. **Select requirements by technology and function.**
   - Evaluate native Android, iOS, and desktop interfaces against applicable common requirements, functional-performance statements, and software requirements.
   - Evaluate HTML content inside a WebView against applicable web requirements as web content; native wrappers do not repair the DOM.
   - Evaluate downloadable PDFs and office documents against applicable non-web document requirements.
   - Evaluate media, two-way voice, hardware, documentation, and support clauses only when those functions or deliverables exist.
4. **Use the relevant Annex mapping.** Map the selected requirements to the applicable Directive only after confirming the cited edition and scope. An Annex mapping supports traceability; it does not decide whether the law applies to the product.
5. **Record exclusions.** For every clause marked not applicable, record the product fact and reasoning. “It is a mobile app” is not sufficient.
6. **Collect evidence per surface and release.** Keep static review, automated checks, simulator results, real-device assistive-technology observations, known limitations, and unresolved findings separate.
7. **Constrain the claim.** State the tested release, surfaces, configurations, standard edition, applicable clauses, evidence limits, and whether Official Journal citation was verified.

Example: a native checkout flow with an embedded payment WebView and downloadable PDF receipt normally requires three separate scope decisions—native software, web content, and non-web document—not one clause 9 audit for the entire product.

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

The Department of Justice rule for covered state and local government web content and mobile apps uses WCAG 2.1 Level AA. As of this review, an April 2026 Interim Final Rule extends the compliance date to 26 April 2027 for public entities with a population of 50,000 or more, and to 26 April 2028 for public entities below 50,000 and special district governments. Verify the current rule, entity category, exceptions, and later rulemaking at ADA.gov before reporting a deadline.

Do not generalize this Title II technical standard to every private, federal, or state-regulated app. Third-party content or mobile apps supplied through contractual, licensing, or other arrangements can still be within a public entity's covered offering.

- Current Title II resources and dates: https://www.ada.gov/title-ii-web-rule/
- 2026 Interim Final Rule: https://www.ada.gov/assets/pdfs/2026-ifr.pdf
- Small-entity compliance guide: https://www.ada.gov/resources/small-entity-compliance-guide/

### Section 508

The refreshed Section 508 Standards apply to covered federal ICT and incorporate WCAG 2.0 Level A and AA requirements for applicable content. A native application assessment must not stop at a WCAG checklist: self-scope the applicable functional-performance criteria, software interoperability and application requirements, content, documentation, and support provisions. Record the federal or procurement context, exceptions, equivalent-facilitation decisions, and which provisions were evaluated.

A project may adopt WCAG 2.1 or 2.2 as an engineering baseline, but do not misstate that newer version as the edition incorporated by Section 508.

- US Access Board ICT standards: https://www.access-board.gov/ict/
- Section 508 standards by chapter: https://www.access-board.gov/ict/#508-chapters-1-and-2-application-and-scoping

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
