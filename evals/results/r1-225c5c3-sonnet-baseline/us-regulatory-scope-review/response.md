# Review of `USComplianceClaim.md`

This is a scope and evidence review, not legal advice. Counsel should confirm applicability and current deadlines. I did not edit the fixture.

## Corrections to the claims

| Claim | Problem | Supportable replacement |
|---|---|---|
| "Passed an automated WCAG 2.2 scan, so it complies with ADA Title II, Title III, and Section 508" | A scan is not a compliance determination. Automated tools detect only part of WCAG, and many criteria need manual or assistive-technology testing. The laws also apply to different entities and in different ways. | "Automated WCAG 2.2 scan of version X on date Y found Z issues. Manual and assistive-technology testing covered [scope]." |
| "Throughout the United States" | These laws don't apply to everyone everywhere. Title II covers state and local governments and their programs. Title III covers places of public accommodation. Section 508 covers federal agencies, and reaches vendors mainly through procurement requirements. | State which law, if any, applies to which deployment, and why. |
| "These laws all require WCAG 2.2 for every native mobile app" | This is incorrect. The DOJ Title II rule (28 CFR part 35, subpart H) sets WCAG 2.1 Level AA for state and local government web content and mobile apps, with phased compliance dates and exceptions. Title III has no codified technical standard for web or mobile apps, and WCAG is used as a benchmark or in settlements. Revised Section 508 (36 CFR part 1194) incorporates WCAG 2.0 A/AA, not 2.2. | Name the standard for each law separately. Describe WCAG 2.2 AA as a voluntary target that exceeds those baselines, not a legal requirement. |
| "Section 508 does not require any interoperability or functional-performance review beyond WCAG" | This is incorrect. Revised 508 also includes Chapter 3 (functional performance criteria), Chapter 5 (software, including interoperability with assistive technology and platform accessibility features), and Chapter 6 (support documentation and services). Conformance is usually reported as an ACR/VPAT. | State that 508 assessment covers WCAG-mapped criteria plus the functional-performance, software, and support-documentation criteria that apply. |
| "The same scan proves third-party SDK screens and future releases are compliant" | A scan only reflects the build and screens it tested. It can't cover code or content that changes later. Third-party SDK screens must be inventoried and tested, and the organization remains responsible for them. | Make the claim release-specific, and list SDK screens as tested, excluded, or remediation-tracked. |

## Context needed to determine applicability

1. **Who operates or offers the app.** Is it a state or local government entity or a contractor for one (Title II)? A private business or nonprofit that is a public accommodation (Title III)? A federal agency, or a vendor selling to one (Section 508)?
2. **How it is used.** Is it a government service or program, a commercial service, an employee tool, or a procurement deliverable?
3. **Size and dates.** For Title II, the entity's population size or special-district status determines the compliance date. Verify the current dates, since DOJ has revisited the schedule.
4. **Funding and contracts.** Federal financial assistance can bring in Section 504. Contract language may require an ACR/VPAT or a specific standard.
5. **Scope of the app.** Which platforms and OS versions (iOS, Android), which user groups (public or employees), and whether content is archived, third-party, or exempt.
6. **Contractual and state-law overlays.** State accessibility laws and customer-specific requirements may apply.

## Release-specific evidence to define

Tie each record to an app version, build number, platform, and date:

- **Scope statement:** the screens and flows tested, plus exclusions with reasons.
- **Standard and target:** for example, WCAG 2.2 AA as the internal target, with the legal baseline mapped separately per law.
- **Automated results:** tool and version, raw output, triaged findings.
- **Manual testing:** VoiceOver and TalkBack, switch access, keyboard, zoom and text scaling, contrast, orientation, and reduced motion. Record testers, devices, and pass/fail per criterion.
- **Section 508 mapping, where relevant:** an ACR/VPAT covering WCAG, functional performance, software and interoperability criteria, and support documentation.
- **Third-party inventory:** each SDK, webview, and embedded screen, with its test result or a documented gap and owner.
- **Defects:** known issues, severity, remediation plan and dates, and an accessible feedback channel.
- **Release gating:** regression checks per release, with sign-off recording that the statement was re-validated or marked "not re-tested".

## Suggested replacement wording

> "Version X.Y (build N, iOS/Android) was evaluated on [date] against WCAG 2.2 AA using automated scanning and manual testing with [assistive technologies]. Results and known issues are documented in [ACR/report]. Third-party components [listed] were [tested/not tested]. This statement applies only to this release. Applicability of ADA Title II, Title III, or Section 508 depends on the operator and context and has not been determined by this statement."
