# Presentation Studio User Guide

Welcome to the **Presentation Studio** user guide. This guide explains how to use the interactive Analytical Presentation Board to perform real-time reviews, annotate flock metrics, and prepare high-fidelity PowerPoint-like chart decks for flock performance reviews.

---

## 🧭 1. How to Access the Studio

The Presentation Studio is a standalone analytical workspace integrated throughout the Breeder and Executive dashboards.

1. **Direct Navigation:** Open the main sidebar or top navigation menu. Under **Breeder** or **Executive/Management** sections, click **Presentation Studio**.
2. **From Flock Details:** When viewing any flock's details (`flock_detail.html` or `flock_detail_modern.html`), click the prominent **Presentation Studio** button in the header actions.
3. **Flock Switcher Dropdown:** On the top-left of the Presentation Studio page, a flock selector dropdown lets you switch between all active houses instantly without returning to the main dashboard.

---

## 📊 2. The Multi-Chart Stacked Deck

The Presentation Board aggregates **6 specialized charts** stacked vertically. Scroll through the board to analyze and annotate all Breeder performance domains:

1. **Female Depletion & Egg Production %:** Overlays female depletion bar metrics against egg production percentages and standard benchmark curves.
2. **Male Depletion %:** Tracks male culls and mortality rates.
3. **Culls & Hatch Eggs %:** Compares female depletion cull logs directly with hatchery intake receipts.
4. **Water & Feed Consumption:** Displays water consumption (ml/bird) alongside feed allocation for both males and females.
5. **Female Body Weight & Uniformity:** Evaluates female body weight (g) curves alongside flock uniformity percentages.
6. **Male Body Weight & Uniformity:** Evaluates male body weight (g) curves alongside flock uniformity percentages.

---

## 🖱️ 3. Interactive vs. Draw Modes (Hover Tooltips)

To give you the best experience during actual presentation reviews, each chart card has a mode toggle in the top-right corner:

### 🔵 Interactive Mode (Default)
- **Purpose:** Standard analytical reading.
- **Behavior:** The PowerPoint drawing overlay is bypassed. When you hover over lines or bars on the chart, standard Chart.js tooltips appear instantly, showing exact daily dates and values.
- **Tip:** Use this mode when presenting data trends to the team.

### 🎨 Draw / Annotate Mode
- **Purpose:** PowerPoint-style customization.
- **Behavior:** Activates the drawing overlay. The mouse can be used to select, drag, resize, rotate, and write annotations.
- **Tip:** Switch to this mode when you want to label a specific event, highlight a drop in production, or add arrows.

---

## 🛠️ 4. Using the PowerPoint Floating Toolbar

When you click **Draw / Annotate** on any chart, a sleek floating PowerPoint Toolbar opens on the right side of the card. This toolbar lets you place and style objects:

### 1. Adding Materials
- **Text Box:** Click **Text** to drop a transparent label box. Double-click the text box to enter editing mode and write custom notes.
- **Arrow:** Click **Arrow** to add a directional indicator. Scale it or rotate it by dragging the corners of the bounding box.
- **Rect (Rectangle):** Click **Rect** to insert a rectangle. Adjust opacity to create translucent highlights (ideal for shading specific weeks).
- **Circle:** Click **Circle** to insert a round indicator to encircle anomalous points.
- **Callout:** Click **Callout** to drop a pre-styled speech bubble complete with a pointing arrow and editable text.

### 2. Styling Controls
- **Vibrant HSL Palette:** Click color swatches to apply pre-configured modern colors (Clean Blue, Warning Red, Healthy Green, Accent Orange, Deep Slate, Pure White) or click the custom color picker for finer tuning.
- **Opacity Slider:** Slide from 10% to 100% to create transparent background highlights or highly visible arrows.
- **Font Sizing:** Click **+** or **-** to adjust text labels quickly.
- **Layer Depth:** Click **Front** or **Back** to rearrange objects that overlap.
- **Delete Selected:** Select any shape and click **Delete** to erase it from the canvas and permanently delete it from the database.

---

## 🎯 5. Date-String Anchoring & Hiding Rules

The most powerful background feature of this Presentation Studio is **Anti-Drift Anchoring**:

- **No Date Drifting:** The studio translates the coordinates of your shapes into an exact **Date String** (e.g. `2026-05-15`) and a **Y-Value** (e.g. `85.5g`).
- **Visible Range Hiding:** If you filter the date range of the chart (e.g., viewing only the last 7 days), **any annotation that belongs to a date outside of the visible range is automatically hidden**. 
- **Automatic Reappearance:** If you expand the range again, the annotation will reappear at its exact coordinate **without moving or drifting**.

---

## 📅 6. Changing Chart Ranges

You can adjust ranges in two ways:

1. **Global Shared Range:** At the top of the board, select a Start/End date and click **Apply** (or click presets like **7 Days**, **14 Days**, **30 Days**, **All Time**). This instantly refilters all 6 charts simultaneously.
2. **Chart-Specific Tuning:** Click **Fine Tune** on the top-right of any chart card to reveal dedicated date selectors. You can filter the range of that specific chart to focus on localized details.
