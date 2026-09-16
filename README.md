# Rachael Juzeler

Static portfolio website for artist Rachael Juzeler / Ratchet Constructs, LLC. Hosted on GitHub Pages.

## Pages

- `index.html` - Work grid (home)
- `project.html` - Project detail (`?id=projectN`)
- `about.html` - Biography and CV
- `available.html` / `available-piece.html` - Available work listing and detail
- `updates.html` - News
- `contact.html` - Contact information

## Data files (generated, do not hand-edit)

- `project-data.js` - Project titles, descriptions, and image lists
- `available-data.js` - Available works
- `news-data.js` - News items
- `sitemap.xml`

Source of truth is `admin_data/*.json`. Run `python rachael_content_manager.py` to edit projects, available works, and news; it rewrites the files above. Commit and push everything it changes, including `project-data.js`. The About/CV and Contact tabs in the manager are placeholders; edit `about.html` and `contact.html` directly.

## Images

- `images/projectN/` - `main.*` is the hero and home-grid tile; all other image files appear in the project gallery in natural order
- `images/available/<work>/` - `main.*` then `detail-N.*`

The content manager names copied images automatically.
