# Constraints

## Critical Rules & Boundaries

1. **No External Scripting / JavaScript**:
   - GitHub sanitizes `<script>` tags entirely from profile READMEs and blocks scripts inside SVG images when rendered via `<img>`.
   - All animations MUST be declarative: either CSS `@keyframes` or native SVG SMIL (`<animate>`).

2. **No Third-Party Tracker / Badge Dependencies**:
   - Do NOT depend on third-party dynamic badges (e.g., shields.io, github-readme-stats, streaked services) that might suffer outages, rate limits, or latency.
   - Everything must be self-contained within this repository and run locally or via GitHub Actions.

3. **No Secrets / Tokens in Repository**:
   - The contribution scraper MUST only access public endpoints (`https://github.com/users/<username>/contributions`).
   - No GitHub Personal Access Tokens (PATs) or sensitive keys may be checked in or required for public operations.

4. **Monochrome ASCII Design Discipline**:
   - Do NOT add multi-color rainbow character styling to the ASCII portrait. It clutters terminal aesthetic. Keep it clean `#c9d1d9` with an optional blue/accent cursor `#58a6ff`.

5. **Cross-Platform Console Compatibility**:
   - Avoid printing non-ASCII Unicode glyphs directly to Windows terminal standard output without proper encoding safeguards, to prevent `UnicodeEncodeError` on Windows cp1252 shells.

6. **GitHub Actions Hygiene**:
   - Commit messages from GitHub Actions must use `[skip ci]` to prevent recurring CI loops.
   - Restrict write permissions strictly to `contents: write`.
