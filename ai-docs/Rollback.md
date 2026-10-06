# Rollback Procedures

## Baseline Commit
- **Initial Baseline Commit**: `fa64f0f` (`feat: animated GitHub profile README with ASCII portrait, neofetch card, and live contribution heatmap`)

## Rollback Scenarios

### 1. Broken Script / Corrupted SVG Generation
If an edit to `scripts/` or generated SVGs introduces rendering defects:
```bash
# Discard uncommitted changes to scripts and SVGs
git checkout HEAD -- scripts/ *.svg data/

# Re-run generator suite to verify clean recovery
.venv\Scripts\python scripts\fetch_contributions.py
.venv\Scripts\python scripts\render_heatmap_svg.py
.venv\Scripts\python scripts\make_info_card.py
.venv\Scripts\python scripts\make_ascii_svg.py
```

### 2. Full Revert to Baseline
To revert the repository back to the pristine initial state:
```bash
git reset --hard fa64f0f
```

### 3. Verification After Rollback
- Verify SVG files exist and are non-empty: `contrib-heatmap.svg`, `avi-ascii.svg`, `info-card.svg`.
- Ensure `.venv` dependencies are intact (`requests`, `beautifulsoup4`, `Pillow`).
- Open `preview.html` or inspect SVGs to verify valid XML headers and syntax.
