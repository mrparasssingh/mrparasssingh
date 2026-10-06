# Feature: Animated Profile README Setup

## Scope & Objective
Create an animated GitHub profile README system for `@mrparasssingh` based on terminal aesthetic:
1. Animated contribution heatmap with real scraped contribution metrics and daily GitHub Actions cron.
2. Animated monochrome ASCII portrait typing itself row by row.
3. Animated neofetch-style terminal info card.
4. Clean GitHub-dark palette integration with zero-token / zero-script constraints.

## Implementation Steps & Verification
1. **Scraper (`scripts/fetch_contributions.py`)**:
   - Initialized to scrape public HTML calendar.
   - Tested against `mrparasssingh`. Successfully parsed contribution activity into `data/contributions.json`.
2. **Heatmap Renderer (`scripts/render_heatmap_svg.py`)**:
   - Built SVG renderer generating standard GitHub dark tiles with `@keyframes slideReveal`.
   - Verified valid output generation into `contrib-heatmap.svg`.
3. **Info Card (`scripts/make_info_card.py`)**:
   - Configured with profile details for `mrparasssingh` / `Paras Singh`.
   - Verified animated SVG output in `info-card.svg`.
4. **ASCII Generator (`scripts/make_ascii_svg.py` & `scripts/prep_photo.py`)**:
   - Configured 100x53 character grid with density ramp.
   - Tested fallback gradient generation into `avi-ascii.svg`.
5. **Automation (`.github/workflows/update-profile-art.yml`)**:
   - Configured daily schedule (`17 6 * * *`) and auto-commit action.

## Status
Complete and operational. All unit generators execute cleanly and produce valid SVG XML.
