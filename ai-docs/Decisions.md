# Decision Log

2026-10-06 | Claude Opus 4.6 | Decision: Use public HTML scraping for contribution calendar instead of GitHub GraphQL API | Why: Eliminates the requirement for GitHub Personal Access Tokens (PATs) and token rotation, making setup effortless and zero-secret | Alternatives considered: GitHub GraphQL API with PAT secret, third-party badges (shields.io, github-readme-stats).

2026-10-06 | Claude Opus 4.6 | Decision: Use SMIL <animate> for ASCII portrait row wipes and cursor | Why: SMIL inside SVGs executes predictably inside GitHub <img> embeds without requiring external CSS loading or JavaScript | Alternatives considered: Pure CSS keyframe animations (less consistent clip-path coordinate support across certain browser SVG renderers).

2026-10-06 | Claude Opus 4.6 | Decision: Adopt GitHub Dark Theme color palette (#0d1117, #30363d, #c9d1d9, #58a6ff, #39d353) | Why: Seamlessly integrates into modern GitHub profile pages without visual jarring or harsh border contrasts | Alternatives considered: Pure black terminal (#000000), light theme.

2026-10-06 | Gemini 3.8 Flash | Decision: Retain local demo gradient fallback when input photo is absent | Why: Guarantees a fully functional and aesthetic baseline immediately upon initialization before the user uploads their own photo | Alternatives considered: Empty placeholder box, erroring out on build.
