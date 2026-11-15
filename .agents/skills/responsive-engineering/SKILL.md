---
name: responsive-engineering
description: Responsive engineering standards, mobile-first layouts, tablet navigation, flexbox/grid layout constraints, and eliminating horizontal body overflow across all standard screen sizes. Use when building or auditing responsive layouts.
---

# Responsive Engineering Standard

## 1. Core Principles & Breakpoint Governance
All web interfaces must function flawlessly across 6 standard viewports:
1. **Mobile Narrow**: 375 × 812 (iPhone SE / Mini)
2. **Mobile Standard**: 390 × 844 (iPhone 14/15/16)
3. **Tablet Portrait**: 768 × 1024 (iPad Mini / Air)
4. **Laptop Standard**: 1366 × 768 / 1440 × 900
5. **Desktop Standard**: 1440 × 900
6. **Large Display**: 1920 × 1080+

## 2. Zero-Horizontal-Scroll Rule
- The root document element (`html`, `body`) must NEVER exceed the viewport width (`scrollWidth <= innerWidth`).
- Navbars with multiple inline buttons must collapse into compact dropdowns or mobile drawers on viewports $<1024\text{px}$ (`lg`) rather than overflowing horizontally.
- Use `max-w-full overflow-hidden` or `overflow-x-auto` on scrollable sub-components with visible affordance indicators (edge fade shadows).

## 3. Layout Stacking & Sticky Panel Safety
- Desktop multi-column grids (e.g. 5:7 or 4:8) must cleanly collapse to a single column (`grid-cols-1`) on mobile and tablet.
- Sticky panels (`sticky top-X`) must not exceed the viewport height on compact laptop screens (768px height). Either remove sticky on heights $<900\text{px}$ (`max-h-[calc(100vh-2rem)] overflow-y-auto`) or only stick individual hero elements.
- Touch targets must be at least 44 × 44 CSS pixels on touch viewports ($<1024\text{px}$).
