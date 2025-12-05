# Rachael Juzeler Portfolio Website

A clean, professional portfolio website for artist Rachael Juzeler doing business as Ratchet Constructs, LLC, with a custom Python content management system for easy updates.

## Design Features

- **Typography**: EB Garamond font family for elegant readability
- **Color Scheme**: Custom gold background (RGB 120, 110, 0) with black text
- **Layout**: Fixed header and footer with scrolling content area
- **Navigation**: Five main sections: Work, About/CV, Updates, Contact, Available
- **Responsive**: Mobile-friendly design that adapts to different screen sizes

## File Structure

```
rachaeljuzeler/
├── Website Files
│   ├── index.html          # Main work portfolio page (homepage)
│   ├── about.html          # About/CV page with artist bio and full CV
│   ├── project.html        # Template for individual project detail pages
│   ├── contact.html        # Contact information page
│   ├── updates.html        # Updates/news page
│   ├── available.html      # Available works for sale page
│   ├── styles.css          # Main stylesheet
│   └── script.js           # JavaScript for navigation and interactions
├── Content Management
│   ├── rachael_content_manager.py  # Python content management system
│   └── admin_data/         # Data storage for content manager
│       ├── projects.json   # Project data
│       ├── cv_sections.json  # CV sections data
│       ├── updates.json    # Updates data
│       ├── available_works.json  # Available works data
│       └── contact_info.json  # Contact information data
├── images/                 # Image assets directory
│   ├── project1/           # Images for project 1
│   ├── project2/           # Images for project 2
│   ├── project3/           # Images for project 3
│   └── ...                 # Additional project folders
└── README.md               # This file
```

## Content Management System

This portfolio includes a custom Python-based content management system that allows Rachael to easily update her website content without technical knowledge.

### Python Content Manager

**File**: `rachael_content_manager.py`

A desktop application with tabs matching the website navigation:

#### Features:
- **Projects Management**: Add/edit/delete projects with image uploading
- **CV Management**: Update biography and all CV sections
- **Updates Management**: Add/edit news and updates
- **Contact Management**: Update contact information and social media
- **Available Works**: Manage artwork for sale with pricing

#### Setup:
1. **Install Python 3.8+** (if not already installed)
2. **Install required packages**:
   ```bash
   pip install tkinter pathlib
   ```
3. **Run the content manager**:
   ```bash
   python rachael_content_manager.py
   ```

#### Usage:
1. Launch the application
2. Use tabs to navigate to different content types
3. Select existing items from dropdown to edit, or create new ones
4. Browse for images when adding projects or available works
5. Click Update/Create buttons to save changes
6. Changes are saved to JSON files and will update the website

### Data Storage

Content is stored in JSON files in the `admin_data/` directory:
- `projects.json` - Project information and image references
- `cv_sections.json` - CV sections and biography text
- `updates.json` - News and updates
- `available_works.json` - Available artwork for sale
- `contact_info.json` - Contact information and social media

## Setup for GitHub Pages

1. **Initialize Git Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial website setup"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub and create a new repository
   - Name it something like "rachaeljuzeler-portfolio"
   - Don't initialize with README (since we already have files)

3. **Connect and Push**:
   ```bash
   git remote add origin https://github.com/USERNAME/REPOSITORY-NAME.git
   git branch -M main
   git push -u origin main
   ```

4. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: main / (root)
   - Save

5. **Custom Domain** (optional):
   - In the Pages settings, add your custom domain
   - Create a CNAME file in the root directory with your domain name

## Customization

### Using the Content Manager

Update content easily through the Python content manager:

1. **Run** `python rachael_content_manager.py`
2. **Use the tabs** to navigate to different content types
3. **Select projects** from dropdowns to edit existing content
4. **Upload images** directly through the interface
5. **Save changes** with the Update/Create buttons

### Manual Updates (Advanced Users)

If you prefer to edit files directly:

#### Adding Projects
1. **Add Images**: Place project images in `images/projectN/` folders
2. **Update JavaScript**: Edit the `projectData` object in `script.js`
3. **Update HTML**: Add new work items to the grid in `index.html`

#### Content Updates
- **About/CV**: Edit `about.html` to update bio, exhibitions, awards, etc.
- **Contact Info**: Update email addresses and social media links in the footer
- **Updates**: Edit `updates.html` to add news items
- **Available Works**: Edit `available.html` to add/remove sale items

### Styling

- **Colors**: Modify CSS variables in `styles.css` (`:root` section)
- **Typography**: Change font family by updating the Google Fonts link and CSS
- **Layout**: Adjust grid sizes, spacing, and responsive breakpoints in CSS

## Image Requirements

- **Format**: JPG or PNG recommended
- **Size**: Optimize for web (under 1MB per image)
- **Dimensions**: Square images work best for the work grid (1:1 aspect ratio)
- **Naming**: Use descriptive filenames (e.g., "herring-catch-detail-1.jpg")

## Browser Support

This website uses modern CSS and JavaScript features and supports:
- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Maintenance

- Regularly update project information
- Optimize images for faster loading
- Keep contact information current
- Back up the repository regularly

## Contact

For website updates and maintenance questions, contact:
- Content: rjuzeler@gmail.com

## License

This project uses a dual licensing approach:

- **Code** (HTML, CSS, JavaScript): Licensed under the [MIT License](LICENSE)
- **Content** (text, images, publications): Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
