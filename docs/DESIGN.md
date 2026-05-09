---
name: Bio-Synthetic Noir
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#383939'
  surface-container-lowest: '#0d0e0f'
  surface-container-low: '#1b1c1c'
  surface-container: '#1f2020'
  surface-container-high: '#292a2a'
  surface-container-highest: '#343535'
  on-surface: '#e3e2e2'
  on-surface-variant: '#e4beb4'
  inverse-surface: '#e3e2e2'
  inverse-on-surface: '#303031'
  outline: '#ab8980'
  outline-variant: '#5b4039'
  surface-tint: '#ffb5a0'
  primary: '#ffb5a0'
  on-primary: '#5f1500'
  primary-container: '#ff5722'
  on-primary-container: '#541200'
  inverse-primary: '#b02f00'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#474746'
  on-secondary-container: '#b7b5b4'
  tertiary: '#c9c6c5'
  on-tertiary: '#313030'
  tertiary-container: '#929090'
  on-tertiary-container: '#2a2a29'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdbd1'
  primary-fixed-dim: '#ffb5a0'
  on-primary-fixed: '#3b0900'
  on-primary-fixed-variant: '#862200'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474746'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c9c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474646'
  background: '#121414'
  on-background: '#e3e2e2'
  surface-variant: '#343535'
typography:
  display-lg:
    fontFamily: Montserrat
    fontSize: 72px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  title-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.1em
spacing:
  unit: 8px
  gutter: 24px
  margin-desktop: 64px
  margin-mobile: 20px
  container-max: 1280px
---

## Brand & Style

This design system embodies a "Bio-Synthetic Noir" aesthetic—a fusion of high-performance technology and organic wellness. The personality is clinical yet aggressive, positioning biological solutions (felines) as advanced hardware upgrades for the human condition. 

The visual style is **High-Contrast Minimalism**. It utilizes deep, obsidian-like surfaces to create an atmosphere of premium mystery, punctuated by high-visibility safety accents. The vibe is intentionally "edgy" to reflect the disruptive nature of the product, utilizing sharp corners and technical data-display metaphors. It should evoke a sense of sophisticated urgency and elite bio-hacking.

## Colors

The palette is strictly architectural, relying on a "True Black" foundation to maximize the luminosity of the primary accent.

*   **Primary (Safety Orange):** Reserved for critical actions, hardware status indicators, and high-level branding. It represents the "energy" and "alertness" of the bio-units.
*   **Surface Layers:** A hierarchy of deep grays (`#0A0A0A` for background, `#1A1A1A` for cards) provides depth without breaking the dark-mode immersion.
*   **Text & Accents:** High-contrast white is used for primary titles, while muted grays are used for technical metadata and secondary body copy to maintain a clean, uncluttered interface.

## Typography

Typography follows a "Technical Editorial" approach. **Montserrat** provides the geometric, bold structure needed for authoritative headlines, appearing almost like industrial stencil work when used in caps. **Inter** handles all functional and body text, ensuring legibility against the dark backgrounds.

Key hierarchy rules:
*   Use `label-caps` for small "tag-style" callouts (e.g., "S24 PORTFOLIO COMPANY").
*   Primary headlines should use tight letter-spacing to feel dense and impactful.
*   Large display text should be "Optical White" (#FFFFFF) to contrast against the obsidian background.

## Layout & Spacing

This design system utilizes a **Fixed Grid** system for desktop to maintain a cinematic, controlled composition. 

*   **Desktop:** 12-column grid with a wide 24px gutter. Content is often center-aligned or dramatically asymmetrical to emphasize specific imagery.
*   **Mobile:** 4-column grid with 20px margins.
*   **Rhythm:** An 8px linear scale is used for all internal padding and margins. Large vertical "breathing room" (80px+) is encouraged between major sections to mimic the premium feel of high-end tech slides.

## Elevation & Depth

Depth is conveyed through **Tonal Layering** and **Subtle Outlines** rather than traditional shadows. 

1.  **Base (Level 0):** `#000000` — Pure black for global backgrounds.
2.  **Container (Level 1):** `#0A0A0A` — For major sections or sidebars.
3.  **Floating Element (Level 2):** `#1A1A1A` with a 1px solid border of `#333333`. This creates a "machined" look.

Avoid soft shadows; if a shadow is required for a floating modal, use a sharp, 0-blur "hard shadow" in pure black to maintain the brutalist edge. Semi-transparent overlays should use a subtle backdrop blur (8px) to suggest a glass-like hardware interface.

## Shapes

The shape language is **Sharp (0px)**. To align with the "Biological Tech" theme, the UI avoids friendly, rounded corners in favor of aggressive, precision-cut angles. 

*   **Buttons:** Perfectly rectangular. 
*   **Cards:** Sharp 90-degree corners. 
*   **Tags:** Use a "clipped corner" or simple rectangle to denote a hardware-tag feel.
*   **Exceptions:** Icons and biological imagery may remain organic, providing a stark contrast to the rigid, geometric container of the UI.

## Components

*   **Buttons:** Primary buttons are solid `#FF5722` with black text (`#000000`). Secondary buttons are "Ghost" style: sharp 1px white or orange borders with no fill.
*   **Cards:** Use the `#1A1A1A` surface. Headers within cards should be set in `label-caps` using the primary orange color.
*   **Inputs:** Bottom-border only or 1px dark gray outline. Focus state triggers a solid `#FF5722` border.
*   **Status Indicators:** Small square pips. Glowing/pulsing animations are encouraged for "active" bio-units to suggest a "heartbeat."
*   **Data Visualization:** Use thin lines and monospaced numeric readouts to enhance the "hardware diagnostic" feel.