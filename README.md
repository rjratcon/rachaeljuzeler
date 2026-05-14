# Rachael Juzeler Portfolio Website

Your professional portfolio website showcasing your artwork and practice as Rachael Juzeler / Ratchet Constructs, LLC.

## Your Website Pages

- **Work** (`index.html`) - Main page showing all your projects
- **About** (`about.html`) - Your bio, headshot, and full CV
- **Updates** (`updates.html`) - News and announcements
- **Contact** (`contact.html`) - Contact info and social media links
- **Available** (`available.html`) - Artwork for sale

## Making Simple Updates

### Updating Text Content

**To edit your bio or CV:**
1. Open `about.html` in any text editor
2. Find the section you want to change
3. Edit the text between `<p>` and `</p>` tags
4. Save the file

**To add news/updates:**
1. Open `updates.html`
2. Add your new update following the same format as existing ones
3. Save the file

**To update contact information:**
1. Open `contact.html`
2. Change email addresses or social media handles as needed
3. Save the file

### Adding New Project Images

1. Create a new folder in the `images/` directory (e.g., `images/project16/`)
2. Put your project images in that folder
3. Open `index.html` and add a new work item following the same pattern
4. Open `script.js` and add your project info to the `projectData` section

## Your Image Files

All your project images are stored in the `images/` folder:
- Each project has its own subfolder (e.g., `images/project1/`, `images/project2/`)
- Your headshot is at `images/rjuzeler.jpg`
- Keep images under 1MB for faster loading
- Square images work best for the main grid

## Publishing Your Updates

When you make changes:

1. **Save your files** after editing
2. **Upload to GitHub:**
   - Use GitHub Desktop app, or
   - Use the GitHub website to upload changed files
3. **Your website updates automatically** within a few minutes

## Important Files

- `styles.css` - Controls how your website looks (colors, fonts, layout)
- `script.js` - Makes the image galleries work
- `available.js` - Controls the Available page and each available piece detail page
- `available-data.js` - Stores the available work data shown on the website
- `images/` folder - All your photos and artwork
- Each `.html` file - A page on your website
- `launch_content_manager.bat` - Opens the content manager on Windows

## Getting Help

**For simple text changes:** Any text editor works (Notepad, TextEdit, etc.)

**For more complex updates:** Contact your developer or consider hiring a web developer familiar with HTML/CSS.

**Website hosting:** Your site is hosted free on GitHub Pages and updates automatically when you upload changes.

## Backup

Your entire website is backed up in this GitHub repository. Download the whole repository periodically to keep a local backup of all your files.

## Future Enhancements

There's a Python content management tool (`rachael_content_manager.py`) included in the files that could make updates easier, but it needs testing and setup before use. This could be a future improvement to make managing your portfolio even simpler.

---

*Your website is designed to be beautiful, fast, and professional. The clean design puts your artwork first and works perfectly on phones, tablets, and computers.*
