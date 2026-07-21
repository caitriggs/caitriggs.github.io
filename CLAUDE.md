# CLAUDE.md — caitriggs.github.io

Cait's personal GitHub Pages site — a hand-written static HTML site. The root index.html is an "Ops Board" landing page; each subfolder (camping-weekend-aug-2026/, easement-project/, may-in-la/, wedding-week/, e-myth-book-report/) is a standalone page with its own index.html.

## Stack
- Plain static HTML/CSS (inline <style>, Google Fonts). No framework, no build step, no JS bundler, no dependencies — no package.json, requirements.txt, or _config.yml.

## Build & run locally
- No build. Open an index.html directly in a browser, or serve the folder: `python -m http.server` from the repo root, then visit localhost:8000.

## Deploy
- Automatic on push to main. This is a user Pages repo (caitriggs.github.io), so GitHub Pages publishes the root of main directly. No Actions workflow, CNAME, or .nojekyll — served as-is. Commit and push to main and the live site updates.

## Branch conventions
- main is the published branch — pushing to it is a production deploy. Treat commits to main as going live immediately.
- Remote: github.com/caitriggs/caitriggs.github.io.
- No separate staging branch observed. For anything risky, work on a feature branch and merge to main when ready, since main is live.

## Adding pages
- New trip/itinerary subpage → also add a card to the root index.html "Ops Board" home page, linking to that subpage.
- Ad hoc pages (reports, projects, or anything not a trip/itinerary) → no homepage card or link.

## Do NOT touch
- Don't introduce a build system, bundler, or framework (React/Vue/etc.) or a node_modules/ unless explicitly asked — this site is intentionally plain HTML.
- Don't add Jekyll config or restructure into a Jekyll layout; it's served as static files.
- .git/ — off-limits.
- The working tree currently has uncommitted edits in camping-weekend-aug-2026/index.html and easement-project/index.html — don't discard those changes.
