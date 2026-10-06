# System Architecture

## Overview
The project is a zero-JavaScript, zero-token GitHub Profile README system.
Because GitHub strips `<script>` tags and sanitizes inline styles from profile READMEs, all visual effects and animations are embedded inside standalone SVG images rendered via standard markdown `<img>` tags.

## Components & Modules

```
                    +------------------------------------+
                    |  GitHub Profile README (README.md) |
                    +------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
+------------------+         +------------------+         +------------------+
| contrib-heatmap  |         |    avi-ascii     |         |    info-card     |
|      (.svg)      |         |      (.svg)      |         |      (.svg)      |
+------------------+         +------------------+         +------------------+
         ^                            ^                            ^
         |                            |                            |
+---------------------+      +---------------------+      +---------------------+
| render_heatmap_svg  |      |   make_ascii_svg    |      |   make_info_card    |
+---------------------+      +---------------------+      +---------------------+
         ^                            ^
         |                            |
+---------------------+      +---------------------+
| fetch_contributions |      |     prep_photo      |
+---------------------+      +---------------------+
         ^                            ^
         |                            |
  GitHub Public HTML           Input Image File
  (/users/:user/contributions) (JPG/PNG)
```

### 1. Contribution Heatmap Subsystem
- **`scripts/fetch_contributions.py`**: Scrapes the user's public contribution calendar from `https://github.com/users/<username>/contributions` without requiring GitHub Personal Access Tokens. Outputs structured metrics into `data/contributions.json`.
- **`scripts/render_heatmap_svg.py`**: Reads `data/contributions.json` and produces `contrib-heatmap.svg` featuring CSS keyframe animations that reveal weeks sequentially.
- **GitHub Actions Workflow (`.github/workflows/update-profile-art.yml`)**: Daily cron job running on GitHub Actions to keep the heatmap refreshed automatically.

### 2. Monochromatic ASCII Portrait Subsystem
- **`scripts/prep_photo.py`**: Scales, crops, normalizes, and contrasts raw portrait images into optimal grayscale inputs.
- **`scripts/make_ascii_svg.py`**: Converts the prepped image into an ASCII grid using a custom density ramp and generates an animated SVG (`avi-ascii.svg`) utilizing SMIL `<clipPath>` wipes with cursor simulation.

### 3. Terminal Neofetch Info Card Subsystem
- **`scripts/make_info_card.py`**: Generates `info-card.svg` displaying developer profile metadata, stack, and contact points styled as a clean terminal output with staggered CSS reveal animations.

## Data Flow
1. **Build/Local Generation**:
   Raw image / GitHub scraping -> Python Generators -> Standalone SVG files.
2. **Runtime on GitHub**:
   GitHub CDN serves `README.md` -> Browser requests SVGs -> Browser SVG engine executes SMIL/CSS animations natively inside `<img>` sandbox.
