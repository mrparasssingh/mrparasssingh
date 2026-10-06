# Test Checklist

Run the following checks to verify system integrity before marking tasks complete:

## 1. Contribution Fetch Test
- **Command**:
  ```powershell
  .venv\Scripts\python scripts\fetch_contributions.py --username mrparasssingh
  ```
- **Expected Output**:
  - `Fetched ... days of contribution data for mrparasssingh`
  - Output summary: Total contributions, Active days, Current streak, Longest streak, Best day.
  - File updated: `data/contributions.json`.

## 2. Heatmap Render Test
- **Command**:
  ```powershell
  .venv\Scripts\python scripts\render_heatmap_svg.py
  ```
- **Expected Output**:
  - `Heatmap SVG generated -> contrib-heatmap.svg`
  - File updated: `contrib-heatmap.svg` (~37KB, valid XML, `<svg...`).

## 3. Info Card Render Test
- **Command**:
  ```powershell
  .venv\Scripts\python scripts\make_info_card.py
  ```
- **Expected Output**:
  - `Info card SVG generated -> info-card.svg`
  - File updated: `info-card.svg` (~4KB, valid XML, `<svg...`).

## 4. ASCII Portrait Render Test
- **Command**:
  ```powershell
  .venv\Scripts\python scripts\make_ascii_svg.py
  ```
- **Expected Output**:
  - `No input image specified, using demo gradient...`
  - `ASCII SVG generated -> avi-ascii.svg`
  - File updated: `avi-ascii.svg` (~41KB, valid XML, `<svg...`).

## 5. SVG XML Syntax Validation
- **Command**:
  ```powershell
  .venv\Scripts\python -c "import xml.etree.ElementTree as ET; [ET.parse(f) for f in ['contrib-heatmap.svg', 'info-card.svg', 'avi-ascii.svg']]; print('ALL SVGS VALID XML')"
  ```
- **Expected Output**:
  - `ALL SVGS VALID XML` (no XML parse error).
