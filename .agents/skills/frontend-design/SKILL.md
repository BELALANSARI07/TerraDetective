---
name: frontend-design
description: Design principles and methodologies to avoid generic AI-generated interfaces ("AI slop") and create distinct, production-grade, bespoke visual identities. Use when designing web components, layouts, color systems, or typography.
---

# Frontend Design & Visual Identity Standard

## 1. Purpose & Core Philosophy
Eliminate generic, cookie-cutter AI aesthetics (uninspired purple gradients, gratuitous glassmorphism blur, floating blobs, unmotivated cards, and repetitive layouts). Replace them with deliberate, editorial or domain-grounded visual design systems tailored to the actual product domain.

## 2. Key Principles
1. **Domain-Grounded Metaphors**:
   - Scientific/environmental tools must look like authoritative field publications or high-density aerospace telemetry consoles, not generic SaaS marketing landing pages.
2. **Typography with Intent**:
   - Limit to 2–3 typefaces with clear roles:
     - Expressive Editorial Serif (e.g., Instrument Serif, Newsreader) for narrative headlines and paradox statements.
     - Neutral, highly legible Sans-Serif (e.g., Plus Jakarta Sans, Inter) for interface controls, body copy, and navigation.
     - Technical Tabular Monospace (e.g., JetBrains Mono) for numerical telemetry, sensor IDs, DOIs, and statistical p-values.
   - Always use `tabular-nums` on dynamic numerical data to prevent horizontal jitter.
3. **Restrained Color Palettes**:
   - 1 background canvas, 1-2 elevated surface tones, 1 sharp border rule.
   - Functional semantic accents: Terracotta for thermal anomalies / heat, Viridian for vegetation / moisture, Cyan for aerospace telemetry, Amber for warnings / highlights.
   - High-contrast rules: Contrast ratio must exceed 4.5:1 for normal text and 3:1 for large text (WCAG 2.1 AA).
4. **Structured Composition**:
   - Asymmetric grids that guide the eye rather than repetitive uniform cards.
   - Deliberate whitespace rhythm (multiples of 4px / 8px).
   - Crisp 1px border lines rather than heavy drop-shadows.
