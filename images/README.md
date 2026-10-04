# Images Folder Structure

This folder contains all images for the portfolio website.

## Organization

- `project1/` ... `project15/` - one folder per project on the WORK page
- `chandeliers/<piece id>/` - one folder per chandelier shown inside the CHANDELIERS project (project3)
- `available/<piece id>/` - one folder per Available work

## File Naming Convention

**Recommended naming:**
- `main.jpg` or `main.png` - Primary image shown in the work grid
- `detail-1.jpg`, `detail-2.jpg`, etc. - Additional detail images
- `process-1.jpg`, `process-2.jpg`, etc. - Process or behind-the-scenes images

**Supported file types:**
- `.jpg` / `.jpeg`
- `.png`
- `.webp`
- `.gif` (for animations)

## Image Requirements

- **Grid Images**: any shape; images are shown whole (not cropped), minimum 600px on the long side
- **Detail Images**: Any aspect ratio, recommended width 1200-2000px
- **File Size**: Optimize for web, keep under 1MB per image
- **Quality**: 80-90% JPEG quality or equivalent

## Examples

```
project1/
├── main.jpg          # Primary grid image
├── detail-1.jpg      # Close-up detail
├── detail-2.jpg      # Another angle
└── process-1.jpg     # Work in progress shot

project2/
├── main.png          # Primary grid image (PNG format)
├── installation.jpg  # Full installation view
└── detail-macro.jpg  # Macro detail shot
```

The website will automatically detect and display these images in the project detail pages.