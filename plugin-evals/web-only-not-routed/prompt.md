---
max_turns: 6
timeout_seconds: 150
allowed_tools: [Agent, Read, Glob, Grep, Skill]
---

This React web component is used only on our marketing website, not in any mobile app. Make the icon button accessible to screen readers and show the corrected code.

```tsx
export function CloseButton({ onClose }: { onClose: () => void }) {
  return (
    <div className="close" onClick={onClose}>
      <svg viewBox="0 0 16 16"><path d="M2 2l12 12M14 2L2 14" /></svg>
    </div>
  );
}
```
