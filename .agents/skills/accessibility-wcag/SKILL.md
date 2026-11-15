---
name: accessibility-wcag
description: Accessibility standards (WCAG 2.1 AA), keyboard navigation, focus management, semantic ARIA attributes, color contrast verification, and screen reader compatibility. Use when building or auditing accessible interfaces.
---

# Accessibility & WCAG 2.1 AA Standard

## 1. Compliance Mandates
1. **Focus Visibility (WCAG 2.4.7)**:
   - Interactive elements (`button`, `a`, `input`, `select`, `textarea`, custom triggers) must have an explicit, visible `:focus-visible` ring.
   - Example Tailwind: `focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-900`.
   - Never use `outline-none` or `focus:outline-none` without an immediate `:focus-visible` replacement.
2. **Color Contrast (WCAG 1.4.3)**:
   - Body copy and interactive labels must have a minimum contrast ratio of 4.5:1 against their background.
   - Large text ($\ge 18\text{pt}$ / $24\text{px}$ regular, or $\ge 14\text{pt}$ / $18.66\text{px}$ bold) must have at least 3:1 contrast.
   - Avoid low-opacity text (e.g. `text-muted/70`) on subtle background tints.
3. **Semantic HTML & Screen Reader Semantics**:
   - Form inputs must have an associated `<label htmlFor="id">` or explicit `aria-label`.
   - Icon-only buttons must have `aria-label="Action description"`.
   - Modals and dialogs must have `role="dialog"`, `aria-modal="true"`, `aria-labelledby="dialog-title"`, and respond to the `Escape` key.
4. **Motion Sensitivity (WCAG 2.3.3)**:
   - Respect `@media (prefers-reduced-motion: reduce)`.
   - Disable or minimize infinite pulse animations, spinning radars, and decorative transitions for users requesting reduced motion.
