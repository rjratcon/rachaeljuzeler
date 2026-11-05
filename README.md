# Rachael Juzeler

Static portfolio website for artist Rachael Juzeler / Ratchet Constructs, LLC. Hosted on GitHub Pages.

## Pages

- `index.html` - Work grid (home)
- `project.html` - Project detail (`?id=projectN`)
- `piece.html` - One work inside a project, e.g. a single chandelier (`?project=projectN&id=<piece id>`)
- `about.html` - Biography and CV
- `available.html` / `available-piece.html` - Available work listing and detail
- `updates.html` - News
- `contact.html` - Contact information

## Data files (generated, do not hand-edit)

- `project-data.js` - Project titles, descriptions, and image lists
- `project-pieces-data.js` - Individual works shown as a clickable grid on a project page (CHANDELIERS)
- `available-data.js` - Available works, in display order (new works are added at the top; reorder with Move Up/Move Down in the manager)
- `news-data.js` - News items
- `sitemap.xml`

Source of truth is `admin_data/*.json`. Run `python rachael_content_manager.py` to edit projects, chandelier pieces, available works, and news; it rewrites the files above. Commit and push everything it changes, including `project-data.js`. The bio, CV sections, contact details, and home page tile titles have no JSON: the manager reads and rewrites them in the HTML pages directly (contact details on every page, because each footer repeats them). The manager refuses to start if a file in `admin_data/` can't be read, which usually means leftover merge conflict markers.

## Images

- `images/projectN/` - `main.*` is the hero and home-grid tile; all other image files appear in the project gallery in natural order
- `images/available/<work>/` - `main.*` then `detail-N.*`
- `images/chandeliers/<piece id>/` - `main.*` then `detail-N.*` for each chandelier
- `images/news/` - preview photos added with Browse for Image on the News tab

Use the PIECES tab in the content manager to add, edit, reorder, or delete project pieces and their photos. It updates `admin_data/project_pieces.json` and regenerates `project-pieces-data.js` and `sitemap.xml`.

The content manager names copied images automatically.
