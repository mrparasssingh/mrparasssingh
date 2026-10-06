# Execution Flow

## 1. Local Generation Workflow

### A. Heatmap Generation
1. `python scripts/fetch_contributions.py [--username mrparasssingh]`
   - Queries `https://github.com/users/<username>/contributions` via `requests`.
   - Parses `td.ContributionCalendar-day` using `BeautifulSoup`.
   - Calculates streaks, total contributions, active days, and best day.
   - Saves output to `data/contributions.json`.
2. `python scripts/render_heatmap_svg.py`
   - Reads `data/contributions.json`.
   - Generates SVG grid layout (53 weeks x 7 days) and color scales (GitHub dark levels).
   - Generates CSS `@keyframes slideReveal` with week-based animation delays (`0.02s` stagger).
   - Writes `contrib-heatmap.svg`.

### B. ASCII Portrait Generation
1. `python scripts/prep_photo.py <input-image-path>` (Optional for custom photo)
   - Resizes and crops to target aspect ratio (monochrome grayscale).
   - Enhances contrast and normalizes histogram.
   - Saves intermediate processed photo.
2. `python scripts/make_ascii_svg.py [--input <path>]`
   - Maps 0–255 grayscale values to character density ramp (` .`:-=+*cs#%@`).
   - If no image supplied, falls back to smooth radial demo gradient.
   - For each row, constructs a `<clipPath>` with SMIL `<animate>` wipe and trailing cursor rect `<animate>`.
   - Writes `avi-ascii.svg`.

### C. Neofetch Info Card Generation
1. `python scripts/make_info_card.py`
   - Formats user metadata: Role, Stack, Editor, Shell, and Highlights.
   - Computes layout positions and applies staggered `@keyframes fadeSlideIn` timing.
   - Writes `info-card.svg`.

## 2. GitHub Actions Automated Refresh Workflow

Triggered via cron (`17 6 * * *`), manual dispatch, or push to `main`:
1. Checkout repository (`actions/checkout@v4`).
2. Setup Python environment (`actions/setup-python@v5`).
3. Install dependencies (`pip install requests beautifulsoup4`).
4. Execute `python scripts/fetch_contributions.py`.
5. Execute `python scripts/render_heatmap_svg.py`.
6. Commit & push changes to `data/contributions.json` and `contrib-heatmap.svg` with `[skip ci]`.
