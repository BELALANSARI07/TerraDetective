---
name: visual-qa
description: Visual quality assurance procedures, multi-viewport automated testing, console runtime error auditing, and screenshot comparison for production-grade web interfaces. Use during visual verification phases.
---

# Visual Quality Assurance & Multi-Viewport Verification

## 1. Automated Verification Checklist
1. **Multi-Viewport Matrix**:
   - 375 × 812 (Mobile Narrow)
   - 390 × 844 (Mobile Standard)
   - 768 × 1024 (Tablet Portrait)
   - 1366 × 768 (Standard Laptop)
   - 1440 × 900 (Desktop)
   - 1920 × 1080 (FHD Monitor)
2. **Layout & Overflow Invariants**:
   - `document.documentElement.scrollWidth === window.innerWidth` across all viewports.
   - No text collisions, label truncations without ellipsis, or chart legends overflowing viewport bounds.
   - Sticky navigation bars must not block content when jumping to anchors.
3. **Console Telemetry**:
   - Zero runtime warnings or errors (e.g., SVG path parse errors, React missing key warnings, unhandled fetch rejections).
4. **Interactive Verification**:
   - Theme toggle transitions smoothly without flash of unstyled content (FOUC).
   - Dropdown selections update charts and telemetry cards without throwing layout shifts.
   - Modals open and close smoothly, trap focus, and dismiss on Escape or backdrop click.
