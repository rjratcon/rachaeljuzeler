# Adding Images to Your Portfolio

## Quick Start

1. **Choose your project folder** (project1, project2, ... project9)
2. **Add your images** to that folder with these recommended names:
   - `main.png` or `main.jpg` - Primary image shown in the work grid
   - `detail-1.png`, `detail-2.png`, etc. - Additional detail shots
   - `process-1.png` - Process or behind-the-scenes shots

## Supported File Types

- `.png` (best for graphics with transparency)
- `.jpg` / `.jpeg` (best for photographs)
- `.webp` (modern format, smaller file sizes)
- `.gif` (for animations)

## Image Organization

```
images/
├── project1/
│   ├── main.png          ← Shows in work grid
│   ├── detail-1.png      ← Shows in project page
│   ├── detail-2.png      ← Shows in project page
│   └── process-1.png     ← Shows in project page
├── project2/
│   ├── main.jpg
│   └── detail-1.jpg
└── project3/
    ├── main.png
    ├── detail-1.png
    ├── detail-2.png
    └── installation.png
```

## How It Works

### Work Grid (Homepage)
- The system automatically looks for `main.png`, `main.jpg`, `primary.png`, etc.
- First image found becomes the background for that project square
- If no image is found, shows the default gold background

### Project Detail Pages
- The content manager scans the project folder and lists every image in `project-data.js`
- `main` is shown first, then the rest in natural order (detail-2 before detail-10); there is no limit
- Every image is shown whole inside its box (nothing is cropped), so any shape works
- If no images are found, displays a helpful message

## Image Recommendations

### Grid Images (main.png/jpg)
- **Size**: 800x800px minimum (square format)
- **File size**: Under 500KB
- **Content**: Clear view of the artwork that represents the project well

### Detail Images
- **Size**: 1200px wide minimum
- **File size**: Under 1MB each
- **Content**: Close-ups, different angles, installation views, process shots

## Example Names That Work

The system recognizes these image names (in order of preference):
- `main` - Primary project image
- `primary` - Alternative primary image
- `hero` - Hero/feature image
- `detail-1`, `detail-2`, `detail-3`, etc. - Detail shots
- `process-1`, `process-2` - Process documentation
- `installation` - Installation/context shots
- `overview` - Wide overview shots
- `close-up` - Close-up detail shots
- `macro` - Macro photography
- `environment` - Environmental context
- `context` - Contextual shots

## Tips

1. **Use descriptive names**: `glass-detail-1.png` is better than `IMG001.png`
2. **Optimize file sizes**: Use image compression tools before uploading
3. **Test different formats**: PNG for graphics, JPG for photos
4. **Any shape works**: images are shown whole and scaled to fit their box
5. **Consistent naming**: Makes organization easier

## Troubleshooting

**Grid image not showing?**
- Check that the image is named `main.png`, `main.jpg`, `primary.png`, or `hero.png`
- Ensure the file is in the correct project folder
- Verify the file extension is supported

**Project page shows "Images will be added soon"?**
- Add at least one image with a recognized name to the project folder
- Wait a moment for the page to load the images
- Check that file names don't have spaces or special characters

## Available Work

Available pieces live in one folder per piece, named from the title:

```text
images/available/herring/
images/available/mini-imperial-chandelier/
```

Inside each piece folder:
- The first image becomes the main image on the Available page
- Extra images appear on the piece detail page

You do not need to name these by hand. The content manager will copy and rename them automatically.

## Updating Available Work with the Python App

Run the content manager from Command Prompt / PowerShell in the website folder:

```powershell
py -3.13 rachael_content_manager.py
```

Then:
1. Open the `AVAILABLE` tab
2. Enter the piece title, price, size, and description
3. Click `Browse for Images`
4. Select the images from the computer
5. Click `Add Available Work`

For updates:
1. Open the `AVAILABLE` tab
2. Choose the piece from the dropdown
3. Edit the information
4. Optionally replace the images
5. Click `Update Work`

The app updates:
- `admin_data/available_works.json`
- `available-data.js`
- `sitemap.xml`

The website pages then read that information automatically.

**Order on the Available page:** new works appear at the top. To rearrange existing works, change the
order of the entries in `admin_data/available_works.json`, then open the content manager once so it
rewrites `available-data.js`.

## Chandeliers

The CHANDELIERS project page shows a grid of individual chandeliers; clicking one opens `piece.html`
with its photos and text.

- Text and photo lists: `admin_data/project_pieces.json` (one entry per chandelier, in display order)
- Photos: `images/chandeliers/<piece id>/main.jpg`, `detail-1.jpg`, ...

The content manager does not have a screen for these yet. Edit the JSON file by hand, then open the
content manager once; it rewrites `project-pieces-data.js` and `sitemap.xml`.
