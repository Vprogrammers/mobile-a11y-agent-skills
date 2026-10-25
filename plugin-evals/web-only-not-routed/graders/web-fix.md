---
type: llm
---

PASS if the response replaces the clickable div with a native `<button type="button">` (or gives the element a button role, keyboard activation, and focusability) and gives it an accessible name such as `aria-label="Close"`, while hiding the decorative SVG from assistive technology.

FAIL if it gives Android, iOS, TalkBack, or VoiceOver instructions instead of web fixes, or leaves the control without an accessible name or keyboard access.
