#!/usr/bin/env python3
"""
Rachael Juzeler Portfolio Content Manager
Automated content management with image handling and HTML file updates
Based on Ocean Bight Content Manager pattern
"""

import os
import shutil
import re
import json
import tempfile
from datetime import datetime
from html import escape, unescape
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Dropdown label -> exact <h2> text in about.html. Explicit because some labels
# are shorter than their heading (Museum Collections).
CV_SECTION_HEADINGS = {
    "Awards & Grants": "AWARDS &amp; GRANTS",
    "Public Works": "PUBLIC WORKS",
    "Museum Collections": "MUSEUM COLLECTIONS | Rasmuson Art Acquisitions",
    "Selected Solo Exhibitions": "SELECTED SOLO EXHIBITIONS",
    "Selected Juried Shows & Group Exhibitions": "SELECTED JURIED SHOWS &amp; GROUP EXHIBITIONS",
    "Selected Education & Training": "SELECTED EDUCATION &amp; TRAINING",
    "Board & Volunteer Positions": "BOARD &amp; VOLUNTEER POSITIONS",
    "Employment History": "EMPLOYMENT HISTORY",
}

# "2011 (ongoing) - text", "1988-1992 - text", "2012-present - text". Only the first
# separator counts because item text has dashes of its own. En/em dashes are accepted
# because text pasted from Word has them.
# Formats every browser shows. TIFF and iPhone HEIC would upload fine and then appear broken.
WEB_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

CV_DATED_LINE = re.compile(
    r'^(\d{4}(?:[-–—](?:\d{4}|present))?(?: \(ongoing\))?)\s+[-–—]\s+(.+)$',
    re.IGNORECASE,
)


def find_cv_list(page, label):
    """Locate the inside of a CV section's <ul>; raises ValueError if it can't be pinned down"""
    pattern = (r'<h2>' + re.escape(CV_SECTION_HEADINGS[label]) + r'</h2>\s*'
               r'<ul class="cv-list">(.*?)</ul>')
    matches = list(re.finditer(pattern, page, re.DOTALL))
    if len(matches) != 1:
        raise ValueError(f"Expected one '{label}' section in about.html, found {len(matches)}.")
    return matches[0]


def cv_section_lines(page, label):
    """Return a CV section's items as the plain-text lines shown in the manager"""
    list_html = find_cv_list(page, label).group(1)
    items = re.findall(r'<li>(.*?)</li>', list_html, re.DOTALL)

    # Saving rewrites the whole list as plain text, so anything this can't represent
    # (a link, a styled <li>, a comment) would be lost. Refuse rather than drop it.
    leftover = re.sub(r'<li>.*?</li>', '', list_html, flags=re.DOTALL).strip()
    plain_items = [re.sub(r'^<strong>([^<]*)</strong>', r'\1', item) for item in items]
    if leftover or any('<' in item for item in plain_items):
        raise ValueError(f"'{label}' has formatting the manager can't edit. "
                         "Edit about.html by hand.")
    return [unescape(item) for item in plain_items]


def cv_line_to_item(line):
    """Turn one plain-text line into <li> markup, bolding a leading date"""
    dated = CV_DATED_LINE.match(line)
    if dated:
        # quote=False: the page keeps raw apostrophes, and escaping them would
        # rewrite existing items that were not edited.
        return (f"<li><strong>{escape(dated.group(1), quote=False)}</strong> - "
                f"{escape(dated.group(2), quote=False)}</li>")
    return f"<li>{escape(line, quote=False)}</li>"


def replace_cv_section(page, label, lines):
    """Return the page with a CV section's list rewritten; the <h2> is left alone"""
    match = find_cv_list(page, label)
    newline = '\r\n' if '\r\n' in page else '\n'
    items = [' ' * 24 + cv_line_to_item(line) for line in lines]
    list_html = newline + newline.join(items) + newline + ' ' * 20
    return page[:match.start(1)] + list_html + page[match.end(1):]


def find_bio(page):
    """Locate the inside of the bio text block; raises ValueError if it can't be pinned down"""
    matches = list(re.finditer(r'<div class="bio-text">(.*?)</div>', page, re.DOTALL))
    if len(matches) != 1:
        raise ValueError(f"Expected one biography block in about.html, found {len(matches)}.")
    return matches[0]


def bio_paragraphs(page):
    """Return the biography as plain-text paragraphs"""
    bio_html = find_bio(page).group(1)
    paragraphs = re.findall(r'<p>(.*?)</p>', bio_html, re.DOTALL)
    # Same reasoning as cv_section_lines: refuse what a plain-text save would lose
    leftover = re.sub(r'<p>.*?</p>', '', bio_html, flags=re.DOTALL).strip()
    if leftover or not paragraphs or any('<' in text for text in paragraphs):
        raise ValueError("The biography has formatting the manager can't edit. "
                         "Edit about.html by hand.")
    return [unescape(text) for text in paragraphs]


def replace_bio(page, paragraphs):
    """Return the page with the biography rewritten; the photo beside it is left alone"""
    match = find_bio(page)
    newline = '\r\n' if '\r\n' in page else '\n'
    items = [' ' * 28 + f"<p>{escape(text, quote=False)}</p>" for text in paragraphs]
    bio_html = newline + (newline * 2).join(items) + newline + ' ' * 24
    return page[:match.start(1)] + bio_html + page[match.end(1):]


def read_contact_details(page):
    """Read the current contact details from contact.html, which is their reference copy"""
    def block(css_class):
        found = re.search(rf'<div class="{css_class}">(.*?)</div>', page, re.DOTALL)
        return found.group(1) if found else ''

    emails = re.findall(r'href="mailto:([^"]+)"', block('contact-emails'))
    handles = re.findall(r'<p>(@[^<]+)</p>', block('contact-social-handles'))
    links = block('contact-social-links')
    instagram = re.search(r'href="([^"]+)"[^>]*>\[ig\]', links)
    facebook = re.search(r'href="([^"]+)"[^>]*>\[fb\]', links)
    if len(emails) != 2 or len(handles) != 2 or not instagram or not facebook:
        raise ValueError("contact.html no longer has the layout the manager expects "
                         "(two emails, two handles, [ig] and [fb] links).")
    return {
        'personal_email': emails[0],
        'business_email': emails[1],
        'instagram_handle': handles[0],
        'second_instagram_handle': handles[1],
        'instagram_url': instagram.group(1),
        'facebook_url': facebook.group(1),
    }


def contact_problem(details):
    """Return what is wrong with the contact details, or None. They go straight into page markup."""
    for key, name in (('personal_email', 'Personal email'), ('business_email', 'Business email')):
        if not re.fullmatch(r'[^@\s"<>]+@[^@\s"<>]+\.[^@\s"<>]+', details[key]):
            return f"{name} doesn't look like an email address."
    if details['personal_email'] == details['business_email']:
        return "The two email addresses must be different."
    for key, name in (('instagram_handle', 'Instagram handle'),
                      ('second_instagram_handle', 'Second Instagram handle')):
        if not re.fullmatch(r'@[\w.]+', details[key]):
            return f"{name} should look like @name."
    for key, name in (('instagram_url', 'Instagram URL'), ('facebook_url', 'Facebook URL')):
        if not re.fullmatch(r'https://[^\s"<>]+', details[key]):
            return f"{name} should be a full web address starting with https://"
    return None


def contact_replacements(old, new):
    """Map old page text to new page text for the details that changed"""
    replacements = {}
    for key in old:
        if old[key] != new[key]:
            if key.endswith('handle'):
                # Only the contact page lists handles; the <p> keeps this from touching other text
                replacements[f"<p>{old[key]}</p>"] = f"<p>{new[key]}</p>"
            else:
                replacements[old[key]] = new[key]
    return replacements


def apply_replacements(page, replacements):
    """Replace everything in one pass, so swapping two emails doesn't merge them"""
    pattern = '|'.join(re.escape(old) for old in sorted(replacements, key=len, reverse=True))
    return re.sub(pattern, lambda found: replacements[found.group(0)], page)


def find_home_tile(page, project_id):
    """Locate a project's tile in index.html; None if it has no tile"""
    return re.search(r'(<a class="work-item"[^>]*data-project="' + re.escape(project_id) +
                     r'"[^>]*aria-label=")([^"]*)(">.*?<div class="work-item-title">)(.*?)(</div>)',
                     page, re.DOTALL)


def replace_home_tile(page, project_id, project_title, home_title):
    """Return the page with a tile's text updated, or None if the project has no tile.

    Tile text is separate from the project title on purpose (PILCHUCK is "Pilchuck Glass
    School Studies"). Pass None for a value that should stay as it is.
    """
    tile = find_home_tile(page, project_id)
    if not tile:
        return None
    label, text = tile.group(2), tile.group(4)
    if project_title:
        label = "View project: " + escape(project_title, quote=False).replace('"', '&quot;')
    if home_title and home_title != unescape(text):
        text = escape(home_title, quote=False)
    return (page[:tile.start()] + tile.group(1) + label + tile.group(3) + text + tile.group(5)
            + page[tile.end():])


def move_entry(entries, key, step):
    """Return a dict with one entry moved; dict order is the order shown on the site"""
    keys = list(entries)
    index = keys.index(key)
    target = index + step
    if not 0 <= target < len(keys):
        return entries
    keys[index], keys[target] = keys[target], keys[index]
    return {name: entries[name] for name in keys}


class RachaelContentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Rachael Juzeler Portfolio Content Manager")
        self.root.geometry("900x700")
        self.root.configure(bg="#786E00")  # Brand gold

        # Set up paths
        self.project_dir = Path(__file__).parent

        # Website files
        self.index_html = self.project_dir / "index.html"
        self.about_html = self.project_dir / "about.html"
        self.contact_html = self.project_dir / "contact.html"
        self.news_html = self.project_dir / "updates.html"
        self.available_html = self.project_dir / "available.html"
        self.available_detail_html = self.project_dir / "available-piece.html"
        self.project_html = self.project_dir / "project.html"
        self.script_js = self.project_dir / "script.js"
        self.news_data_js = self.project_dir / "news-data.js"
        self.available_data_js = self.project_dir / "available-data.js"
        self.project_data_js = self.project_dir / "project-data.js"
        self.project_pieces_js = self.project_dir / "project-pieces-data.js"
        self.sitemap_xml = self.project_dir / "sitemap.xml"

        # Data storage
        self.data_dir = self.project_dir / "admin_data"
        self.data_dir.mkdir(exist_ok=True)
        self.projects_data_file = self.data_dir / "projects.json"
        # Individual works shown as a clickable grid inside a project (e.g. CHANDELIERS).
        # Kept out of projects.json so editing a project here never drops them.
        self.project_pieces_file = self.data_dir / "project_pieces.json"
        self.cv_data_file = self.data_dir / "cv_sections.json"
        self.news_data_file = self.data_dir / "news.json"
        self.available_data_file = self.data_dir / "available_works.json"
        self.contact_data_file = self.data_dir / "contact_info.json"

        # Project folders for images
        self.projects_base_dir = self.project_dir / "images"
        self.projects_base_dir.mkdir(exist_ok=True)
        self.available_base_dir = self.projects_base_dir / "available"
        self.available_base_dir.mkdir(exist_ok=True)

        # Style configuration
        self.configure_styles()

        # Create UI
        self.create_widgets()

        # Initialize tracking variables
        self.current_project_id = None
        self.current_news_id = None
        self.current_available_id = None
        self.current_cv_section = None
        self.current_piece_id = None
        self.current_pieces_project = None
        self.new_piece_image_paths = []
        self.pieces_data = {}
        self.edit_image_paths = []
        self.new_image_paths = []
        self.edit_available_image_paths = []
        self.new_available_image_paths = []
        self.projects_data = {}
        self.news_data = {}
        self.available_data = {}

        # Load existing data
        self.load_data()

    def configure_styles(self):
        """Configure ttk styles for Rachael's brand theme matching website header"""
        style = ttk.Style()

        # Configure colors to match website theme exactly (gold/black)
        style.configure('Rachael.TNotebook',
                       background='#786E00',
                       borderwidth=0)
        style.configure('Rachael.TNotebook.Tab',
                       background='#786E00',
                       foreground='#000000',
                       padding=[20, 15],
                       borderwidth=0,
                       focuscolor='#000000')
        style.map('Rachael.TNotebook.Tab',
                 background=[('selected', '#000000'), ('active', '#000000')],
                 foreground=[('selected', '#786E00'), ('active', '#786E00')],
                 expand=[('selected', [1, 1, 1, 0])])

        style.configure('Rachael.TLabel',
                       background='#786E00',
                       foreground='#000000',
                       font=('EB Garamond', 10, 'bold'))

        style.configure('Rachael.TButton',
                       background='#000000',
                       foreground='#786E00',
                       font=('EB Garamond', 10, 'bold'))

    def create_widgets(self):
        """Create the main UI"""
        # Header
        header_frame = tk.Frame(self.root, bg='#786E00')
        header_frame.pack(fill='x', padx=10, pady=10)

        # Title
        title_label = tk.Label(header_frame,
                              text="RACHAEL JUZELER",
                              font=('EB Garamond', 20, 'bold'),
                              bg='#786E00', fg='#000000')
        title_label.pack(pady=2)

        subtitle_label = tk.Label(header_frame,
                                 text="dba RATCHET CONSTRUCTS, LLC",
                                 font=('EB Garamond', 12),
                                 bg='#786E00', fg='#000000')
        subtitle_label.pack()

        mgmt_label = tk.Label(header_frame,
                             text="Portfolio Content Management System",
                             font=('EB Garamond', 10, 'italic'),
                             bg='#786E00', fg='#333333')
        mgmt_label.pack(pady=(5, 0))

        # Main notebook for tabs
        notebook = ttk.Notebook(self.root, style='Rachael.TNotebook')
        notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.root.bind_all('<MouseWheel>', self.on_mousewheel)

        # Create tabs
        self.create_projects_tab(notebook)
        self.create_pieces_tab(notebook)
        self.create_cv_tab(notebook)
        self.create_news_tab(notebook)
        self.create_contact_tab(notebook)
        self.create_available_tab(notebook)

    def make_scrollable_tab(self, notebook, title):
        """Add a tab and return the frame to build it in, scrolled by a scrollbar and the wheel"""
        main_frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(main_frame, text=title)

        canvas = tk.Canvas(main_frame, bg='#786E00', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#786E00')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return scrollable_frame

    def on_mousewheel(self, event):
        """Scroll the tab under the pointer. Bound globally because the wheel event goes
        to whichever widget is under the pointer, which is almost never the canvas itself."""
        widget = event.widget
        # The dropdown's popup list arrives as a plain string; boxes and lists scroll themselves
        if isinstance(widget, str) or widget.winfo_class() in ('Text', 'Listbox', 'TCombobox'):
            return
        while widget is not None:
            if isinstance(widget, tk.Canvas):
                widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return
            widget = widget.master

    def add_entry(self, parent, label):
        """Add a labeled one-line field and return it"""
        tk.Label(parent, text=label, font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        entry = tk.Entry(parent, width=60, font=('EB Garamond', 10),
                         bg='#786E00', fg='#000000', insertbackground='#000000')
        entry.pack(pady=5, padx=10)
        return entry

    def add_text(self, parent, label, height=5):
        """Add a labeled multi-line box and return it"""
        tk.Label(parent, text=label, font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        box = scrolledtext.ScrolledText(parent, width=60, height=height, wrap='word',
                                        font=('EB Garamond', 10), bg='#786E00', fg='#000000',
                                        insertbackground='#000000')
        box.pack(pady=5, padx=10)
        return box

    def add_button(self, parent, text, command, danger=False):
        """Add a button to a button row"""
        tk.Button(parent, text=text, command=command,
                  bg='#8B0000' if danger else '#000000',
                  fg='#FFFFFF' if danger else '#786E00',
                  font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

    def create_projects_tab(self, notebook):
        """Create projects management tab with scrolling"""
        frame = self.make_scrollable_tab(notebook, 'WORK/PROJECTS')

        # Title
        tk.Label(frame, text="Manage Your Projects",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        # Existing projects dropdown
        existing_frame = tk.LabelFrame(frame, text="Edit Existing Project",
                                      bg='#786E00', fg='#000000',
                                      font=('EB Garamond', 12, 'bold'))
        existing_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(existing_frame, text="Select Project:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))

        self.project_select = ttk.Combobox(existing_frame, width=60,
                                          font=('EB Garamond', 10),
                                          state='readonly')
        self.project_select.pack(pady=5, padx=10)
        self.project_select.bind('<<ComboboxSelected>>', self.on_project_selected)

        self.project_editing_label = tk.Label(
            existing_frame,
            text="No project selected",
            font=('EB Garamond', 10, 'italic'),
            bg='#786E00',
            fg='#333333'
        )
        self.project_editing_label.pack(anchor='w', padx=10, pady=(0, 10))

        # Project editing fields
        tk.Label(existing_frame, text="Project Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_project_title = tk.Entry(existing_frame, width=60, font=('EB Garamond', 10),
                                          bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_project_title.pack(pady=5, padx=10)

        tk.Label(existing_frame, text="Subtitle:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_project_subtitle = tk.Entry(existing_frame, width=60, font=('EB Garamond', 10),
                                             bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_project_subtitle.pack(pady=5, padx=10)

        self.edit_project_home_title = self.add_entry(existing_frame, "Title on Home Page Tile:")

        tk.Label(existing_frame, text="Description:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_project_description = scrolledtext.ScrolledText(existing_frame, width=60, height=4,
                                                                 font=('EB Garamond', 10),
                                                                 bg='#786E00', fg='#000000',
                                                                 insertbackground='#000000')
        self.edit_project_description.pack(pady=5, padx=10)

        tk.Label(existing_frame, text="Current Folder:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_project_folder_label = tk.Label(
            existing_frame,
            text="No project selected",
            font=('EB Garamond', 10),
            bg='#786E00',
            fg='#333333'
        )
        self.edit_project_folder_label.pack(anchor='w', padx=10)

        tk.Label(existing_frame, text="Images in Folder:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_project_image_list = tk.Listbox(
            existing_frame,
            height=5,
            bg='#786E00',
            fg='#000000',
            font=('EB Garamond', 9),
            selectbackground='#000000',
            selectforeground='#786E00'
        )
        self.edit_project_image_list.pack(fill='x', padx=10, pady=5)

        tk.Button(existing_frame, text="Remove Selected Image",
                 command=self.remove_project_image,
                 bg='#8B0000', fg='#FFFFFF',
                 font=('EB Garamond', 9, 'bold')).pack(anchor='w', padx=10)

        # Image management for existing projects
        img_frame = tk.Frame(existing_frame, bg='#786E00')
        img_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(img_frame, text="Add Images (optional, existing images are kept):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w')

        self.edit_image_paths = []
        tk.Button(img_frame, text="Browse for Images",
                 command=self.browse_project_images_edit,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack(pady=5)

        # Update and delete buttons
        btn_frame = tk.Frame(existing_frame, bg='#786E00')
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Update Project",
                 command=self.update_project,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold'),
                 padx=20).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Delete Project",
                 command=self.delete_project,
                 bg='#8B0000', fg='#FFFFFF',  # Dark red
                 font=('EB Garamond', 12, 'bold'),
                 padx=20).pack(side='left', padx=5)

        # Add new project section
        new_frame = tk.LabelFrame(frame, text="Add New Project",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        new_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(new_frame, text="Project Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_project_title = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                         bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_project_title.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Subtitle:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_project_subtitle = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                            bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_project_subtitle.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Description:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_project_description = scrolledtext.ScrolledText(new_frame, width=60, height=4,
                                                                font=('EB Garamond', 10),
                                                                bg='#786E00', fg='#000000',
                                                                insertbackground='#000000')
        self.new_project_description.pack(pady=5, padx=10)

        # New project images
        new_img_frame = tk.Frame(new_frame, bg='#786E00')
        new_img_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(new_img_frame, text="Project Images:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w')

        self.new_image_paths = []
        tk.Label(new_img_frame, text="Selected Images:",
                font=('EB Garamond', 9, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w')

        self.new_image_list = tk.Listbox(new_img_frame, height=4,
                                        bg='#786E00', fg='#000000',
                                        font=('EB Garamond', 9),
                                        selectbackground='#000000',
                                        selectforeground='#786E00')
        self.new_image_list.pack(fill='x', pady=5)

        img_btn_frame = tk.Frame(new_img_frame, bg='#786E00')
        img_btn_frame.pack(fill='x')

        tk.Button(img_btn_frame, text="Browse for Images",
                 command=self.browse_project_images_new,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack(side='left')

        tk.Button(img_btn_frame, text="Clear Images",
                 command=self.clear_new_images,
                 bg='#8B0000', fg='#FFFFFF',
                 font=('EB Garamond', 9, 'bold')).pack(side='left', padx=(10, 0))

        # Create project button
        tk.Button(new_frame, text="Create Project",
                 command=self.create_project,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold'),
                 pady=10).pack(pady=20)

    def create_pieces_tab(self, notebook):
        """Create the tab for individual works inside a project, such as each chandelier"""
        frame = self.make_scrollable_tab(notebook, 'PIECES')

        tk.Label(frame, text="Manage Individual Pieces",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)
        tk.Label(frame, text="Works shown as a clickable grid inside a project, such as each chandelier.",
                font=('EB Garamond', 10, 'italic'),
                bg='#786E00', fg='#333333').pack(pady=(0, 10))

        edit_frame = tk.LabelFrame(frame, text="Edit Piece",
                                   bg='#786E00', fg='#000000',
                                   font=('EB Garamond', 12, 'bold'))
        edit_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(edit_frame, text="Project:", font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.pieces_project_select = ttk.Combobox(edit_frame, width=60, font=('EB Garamond', 10),
                                                  state='readonly')
        self.pieces_project_select.pack(pady=5, padx=10)
        self.pieces_project_select.bind('<<ComboboxSelected>>', self.on_pieces_project_selected)

        tk.Label(edit_frame, text="Select Piece (listed in page order):",
                 font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.piece_select = ttk.Combobox(edit_frame, width=60, font=('EB Garamond', 10),
                                         state='readonly')
        self.piece_select.pack(pady=5, padx=10)
        self.piece_select.bind('<<ComboboxSelected>>', self.on_piece_selected)

        self.edit_piece_fields = {
            'title': self.add_entry(edit_frame, "Title:"),
            'year': self.add_entry(edit_frame, "Year:"),
            'medium': self.add_entry(edit_frame, "Medium:"),
            'size': self.add_entry(edit_frame, "Size:"),
        }
        self.edit_piece_description = self.add_text(
            edit_frame, "Description (leave a blank line between paragraphs):")

        tk.Label(edit_frame, text="Images (first one is the main image):",
                 font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_piece_image_list = tk.Listbox(edit_frame, height=5, bg='#786E00', fg='#000000',
                                                font=('EB Garamond', 9),
                                                selectbackground='#000000',
                                                selectforeground='#786E00')
        self.edit_piece_image_list.pack(fill='x', padx=10, pady=5)

        image_buttons = tk.Frame(edit_frame, bg='#786E00')
        image_buttons.pack(pady=5)
        self.add_button(image_buttons, "Add Images", self.add_piece_images)
        self.add_button(image_buttons, "Remove Selected Image", self.remove_piece_image, danger=True)

        buttons = tk.Frame(edit_frame, bg='#786E00')
        buttons.pack(pady=15)
        self.add_button(buttons, "Update Piece", self.update_piece)
        self.add_button(buttons, "Delete Piece", self.delete_piece, danger=True)
        self.add_button(buttons, "Move Up", lambda: self.move_piece(-1))
        self.add_button(buttons, "Move Down", lambda: self.move_piece(1))

        new_frame = tk.LabelFrame(frame, text="Add New Piece",
                                  bg='#786E00', fg='#000000',
                                  font=('EB Garamond', 12, 'bold'))
        new_frame.pack(fill='x', padx=20, pady=10)

        self.new_piece_fields = {
            'title': self.add_entry(new_frame, "Title:"),
            'year': self.add_entry(new_frame, "Year:"),
            'medium': self.add_entry(new_frame, "Medium:"),
            'size': self.add_entry(new_frame, "Size:"),
        }
        self.new_piece_description = self.add_text(
            new_frame, "Description (leave a blank line between paragraphs):")

        tk.Label(new_frame, text="Selected Images (optional; first one is the main image):",
                 font=('EB Garamond', 10, 'bold'),
                 bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.new_piece_image_list = tk.Listbox(new_frame, height=4, bg='#786E00', fg='#000000',
                                               font=('EB Garamond', 9),
                                               selectbackground='#000000',
                                               selectforeground='#786E00')
        self.new_piece_image_list.pack(fill='x', padx=10, pady=5)

        new_image_buttons = tk.Frame(new_frame, bg='#786E00')
        new_image_buttons.pack(pady=5)
        self.add_button(new_image_buttons, "Browse for Images", self.browse_new_piece_images)
        self.add_button(new_image_buttons, "Clear Images", self.clear_new_piece_images, danger=True)

        tk.Button(new_frame, text="Add Piece (goes to the end of the page)",
                  command=self.create_piece,
                  bg='#000000', fg='#786E00',
                  font=('EB Garamond', 12, 'bold')).pack(pady=15)

    def create_cv_tab(self, notebook):
        """Create CV management tab with scrolling"""
        frame = self.make_scrollable_tab(notebook, 'ABOUT/CV')

        # Title
        tk.Label(frame, text="Manage Your CV & About Content",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        # Bio section
        bio_frame = tk.LabelFrame(frame, text="Edit Biography",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        bio_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(bio_frame, text="About/Bio Text (leave a blank line between paragraphs):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.bio_text = scrolledtext.ScrolledText(bio_frame, width=60, height=14, wrap='word',
                                                 font=('EB Garamond', 10),
                                                 bg='#786E00', fg='#000000',
                                                 insertbackground='#000000')
        self.bio_text.pack(pady=5, padx=10)

        tk.Button(bio_frame, text="Update Bio",
                 command=self.update_bio,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(pady=10)

        # CV sections
        cv_frame = tk.LabelFrame(frame, text="Edit CV Sections",
                                bg='#786E00', fg='#000000',
                                font=('EB Garamond', 12, 'bold'))
        cv_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tk.Label(cv_frame, text="Select CV Section:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))

        self.cv_section_select = ttk.Combobox(cv_frame, width=60,
                                             font=('EB Garamond', 10),
                                             state='readonly',
                                             values=list(CV_SECTION_HEADINGS))
        self.cv_section_select.pack(pady=5, padx=10)
        self.cv_section_select.bind('<<ComboboxSelected>>', self.on_cv_section_selected)

        tk.Label(cv_frame, text="Section Content (one item per line, newest at top, e.g. 2026 - Name of award):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.cv_content = scrolledtext.ScrolledText(cv_frame, width=60, height=14, wrap='word',
                                                   font=('EB Garamond', 10),
                                                   bg='#786E00', fg='#000000',
                                                   insertbackground='#000000')
        self.cv_content.pack(pady=5, padx=10)

        tk.Button(cv_frame, text="Update CV Section",
                 command=self.update_cv_section,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(pady=10)

    def create_news_tab(self, notebook):
        """Create news management tab"""
        # Scrolls because the edit and add forms together are taller than the window
        frame = self.make_scrollable_tab(notebook, 'NEWS')

        # Title
        tk.Label(frame, text="Manage News",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        # Edit existing news items
        edit_frame = tk.LabelFrame(frame, text="Edit Existing News Item",
                                  bg='#786E00', fg='#000000',
                                  font=('EB Garamond', 12, 'bold'))
        edit_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(edit_frame, text="Select News Item:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.news_select = ttk.Combobox(edit_frame, width=60,
                                        font=('EB Garamond', 10),
                                        state='readonly')
        self.news_select.pack(pady=5, padx=10)
        self.news_select.bind('<<ComboboxSelected>>', self.on_news_selected)

        self.news_editing_label = tk.Label(
            edit_frame,
            text="No news item selected",
            font=('EB Garamond', 10, 'italic'),
            bg='#786E00',
            fg='#333333'
        )
        self.news_editing_label.pack(anchor='w', padx=10, pady=(0, 10))

        tk.Label(edit_frame, text="Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_title = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_title.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="One-Sentence Intro:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_intro = scrolledtext.ScrolledText(edit_frame, width=60, height=4,
                                                         font=('EB Garamond', 10),
                                                         bg='#786E00', fg='#000000',
                                                         insertbackground='#000000')
        self.edit_news_intro.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Link URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_url = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_url.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Source:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_source = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                         bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_source.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Category:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_category = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                           bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_category.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Year or Date Label (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_year = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_year.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Preview Image (optional; a web address, or Browse for your own photo):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_image = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_image.pack(pady=5, padx=10)
        tk.Button(edit_frame, text="Browse for Image",
                 command=lambda: self.browse_news_image(self.edit_news_image),
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack()

        tk.Label(edit_frame, text="Button Label (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_news_link_label = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                             bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_news_link_label.pack(pady=5, padx=10)

        # Update buttons
        edit_btn_frame = tk.Frame(edit_frame, bg='#786E00')
        edit_btn_frame.pack(pady=10)

        tk.Button(edit_btn_frame, text="Update News",
                 command=self.update_news_item,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        tk.Button(edit_btn_frame, text="Delete News",
                 command=self.delete_news_item,
                 bg='#8B0000', fg='#FFFFFF',  # Dark red
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        self.add_button(edit_btn_frame, "Move Up", lambda: self.move_news_item(-1))
        self.add_button(edit_btn_frame, "Move Down", lambda: self.move_news_item(1))

        # Add new news item
        new_frame = tk.LabelFrame(frame, text="Add New News Item",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        new_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(new_frame, text="Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_title = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_title.pack(pady=5, padx=10)

        tk.Label(new_frame, text="One-Sentence Intro:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_intro = scrolledtext.ScrolledText(new_frame, width=60, height=4,
                                                        font=('EB Garamond', 10),
                                                        bg='#786E00', fg='#000000',
                                                        insertbackground='#000000')
        self.new_news_intro.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Link URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_url = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                     bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_url.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Source:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_source = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_source.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Category:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_category = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                          bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_category.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Year or Date Label (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_year = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_year.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Preview Image (optional; a web address, or Browse for your own photo):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_image = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_image.pack(pady=5, padx=10)
        tk.Button(new_frame, text="Browse for Image",
                 command=lambda: self.browse_news_image(self.new_news_image),
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack()

        tk.Label(new_frame, text="Button Label (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_news_link_label = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                            bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_news_link_label.pack(pady=5, padx=10)

        tk.Button(new_frame, text="Add News Item",
                 command=self.create_news_item,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold')).pack(pady=15)

    def create_contact_tab(self, notebook):
        """Create contact management tab"""
        frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(frame, text='CONTACT')

        # Title
        tk.Label(frame, text="Manage Contact Information",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        contact_frame = tk.LabelFrame(frame, text="Contact Details",
                                     bg='#786E00', fg='#000000',
                                     font=('EB Garamond', 12, 'bold'))
        contact_frame.pack(fill='x', padx=20, pady=20)

        # Email fields
        email_frame = tk.Frame(contact_frame, bg='#786E00')
        email_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(email_frame, text="Personal Email:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=0, column=0, sticky='w', pady=5)
        self.personal_email = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.personal_email.grid(row=0, column=1, padx=10)

        tk.Label(email_frame, text="Business Email:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=1, column=0, sticky='w', pady=5)
        self.business_email = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.business_email.grid(row=1, column=1, padx=10)

        # Social media
        tk.Label(email_frame, text="Instagram Handle:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=2, column=0, sticky='w', pady=5)
        self.instagram_handle = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.instagram_handle.grid(row=2, column=1, padx=10)

        tk.Label(email_frame, text="Second Instagram Handle:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=3, column=0, sticky='w', pady=5)
        self.second_instagram_handle = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                               bg='#786E00', fg='#000000', insertbackground='#000000')
        self.second_instagram_handle.grid(row=3, column=1, padx=10)

        tk.Label(email_frame, text="Instagram URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=4, column=0, sticky='w', pady=5)
        self.instagram_url = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                     bg='#786E00', fg='#000000', insertbackground='#000000')
        self.instagram_url.grid(row=4, column=1, padx=10)

        tk.Label(email_frame, text="Facebook URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=5, column=0, sticky='w', pady=5)
        self.facebook_url = tk.Entry(email_frame, width=60, font=('EB Garamond', 10),
                                    bg='#786E00', fg='#000000', insertbackground='#000000')
        self.facebook_url.grid(row=5, column=1, padx=10)

        tk.Button(contact_frame, text="Update Contact Info",
                 command=self.update_contact,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold')).pack(pady=20)

    def create_available_tab(self, notebook):
        """Create available works management tab with scrolling"""
        frame = self.make_scrollable_tab(notebook, 'AVAILABLE')

        # Title
        tk.Label(frame, text="Manage Available Works",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        intro_label = tk.Label(
            frame,
            text="Choose images, enter the artwork details, and the website files will update automatically.",
            font=('EB Garamond', 10, 'italic'),
            bg='#786E00',
            fg='#333333'
        )
        intro_label.pack(pady=(0, 10))

        # Edit existing work
        edit_frame = tk.LabelFrame(frame, text="Edit Available Work",
                                  bg='#786E00', fg='#000000',
                                  font=('EB Garamond', 12, 'bold'))
        edit_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(edit_frame, text="Select Work:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.available_select = ttk.Combobox(edit_frame, width=60,
                                            font=('EB Garamond', 10),
                                            state='readonly')
        self.available_select.pack(pady=5, padx=10)
        self.available_select.bind('<<ComboboxSelected>>', self.on_available_selected)

        self.available_editing_label = tk.Label(
            edit_frame,
            text="No work selected",
            font=('EB Garamond', 10, 'italic'),
            bg='#786E00',
            fg='#333333'
        )
        self.available_editing_label.pack(anchor='w', padx=10, pady=(0, 10))

        # Work fields
        work_fields_frame = tk.Frame(edit_frame, bg='#786E00')
        work_fields_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(work_fields_frame, text="Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=0, column=0, sticky='w', pady=2)
        self.edit_work_title = tk.Entry(work_fields_frame, width=40, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_work_title.grid(row=0, column=1, sticky='w', padx=10)

        tk.Label(work_fields_frame, text="Price:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=1, column=0, sticky='w', pady=2)
        self.edit_work_price = tk.Entry(work_fields_frame, width=40, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_work_price.grid(row=1, column=1, sticky='w', padx=10)

        tk.Label(work_fields_frame, text="Size:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=2, column=0, sticky='w', pady=2)
        self.edit_work_size = tk.Entry(work_fields_frame, width=40, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_work_size.grid(row=2, column=1, sticky='w', padx=10)

        tk.Label(work_fields_frame, text="Status:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=3, column=0, sticky='w', pady=2)
        self.edit_work_status = ttk.Combobox(work_fields_frame, width=15,
                                            font=('EB Garamond', 10),
                                            values=["Available", "SOLD", "On Hold"])
        self.edit_work_status.grid(row=3, column=1, sticky='w', padx=10)

        tk.Label(edit_frame, text="Description:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_work_description = scrolledtext.ScrolledText(
            edit_frame,
            width=60,
            height=5,
            font=('EB Garamond', 10),
            bg='#786E00',
            fg='#000000',
            insertbackground='#000000'
        )
        self.edit_work_description.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Current Folder:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_work_folder_label = tk.Label(
            edit_frame,
            text="No work selected",
            font=('EB Garamond', 10),
            bg='#786E00',
            fg='#333333'
        )
        self.edit_work_folder_label.pack(anchor='w', padx=10)

        tk.Label(edit_frame, text="Images in Folder:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.edit_available_image_list = tk.Listbox(
            edit_frame,
            height=5,
            bg='#786E00',
            fg='#000000',
            font=('EB Garamond', 9),
            selectbackground='#000000',
            selectforeground='#786E00'
        )
        self.edit_available_image_list.pack(fill='x', padx=10, pady=5)

        # Image upload for existing
        tk.Label(edit_frame, text="Replace Images (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))

        edit_img_frame = tk.Frame(edit_frame, bg='#786E00')
        edit_img_frame.pack(fill='x', padx=10)

        tk.Button(edit_img_frame, text="Browse for Images",
                 command=self.browse_available_images_edit,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack(side='left')
        tk.Button(edit_img_frame, text="Clear Selection",
                 command=self.clear_available_images_edit,
                 bg='#8B0000', fg='#FFFFFF',
                 font=('EB Garamond', 9, 'bold')).pack(side='left', padx=5)

        # Update/Delete buttons
        edit_btn_frame = tk.Frame(edit_frame, bg='#786E00')
        edit_btn_frame.pack(pady=15)

        tk.Button(edit_btn_frame, text="Update Work",
                 command=self.update_available_work,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        tk.Button(edit_btn_frame, text="Delete Work",
                 command=self.delete_available_work,
                 bg='#8B0000', fg='#FFFFFF',  # Dark red
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        self.add_button(edit_btn_frame, "Move Up", lambda: self.move_available_work(-1))
        self.add_button(edit_btn_frame, "Move Down", lambda: self.move_available_work(1))

        # Add new work
        new_frame = tk.LabelFrame(frame, text="Add New Available Work",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        new_frame.pack(fill='x', padx=20, pady=10)

        # New work fields
        new_work_fields = tk.Frame(new_frame, bg='#786E00')
        new_work_fields.pack(fill='x', padx=10, pady=10)

        tk.Label(new_work_fields, text="Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=0, column=0, sticky='w', pady=2)
        self.new_work_title = tk.Entry(new_work_fields, width=40, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_work_title.grid(row=0, column=1, sticky='w', padx=10)

        tk.Label(new_work_fields, text="Price:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=1, column=0, sticky='w', pady=2)
        self.new_work_price = tk.Entry(new_work_fields, width=40, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_work_price.grid(row=1, column=1, sticky='w', padx=10)

        tk.Label(new_work_fields, text="Size:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=2, column=0, sticky='w', pady=2)
        self.new_work_size = tk.Entry(new_work_fields, width=40, font=('EB Garamond', 10),
                                     bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_work_size.grid(row=2, column=1, sticky='w', padx=10)

        tk.Label(new_work_fields, text="Status:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=3, column=0, sticky='w', pady=2)
        self.new_work_status = ttk.Combobox(new_work_fields, width=15,
                                           font=('EB Garamond', 10),
                                           values=["Available", "SOLD", "On Hold"])
        self.new_work_status.grid(row=3, column=1, sticky='w', padx=10)
        self.new_work_status.set("Available")

        tk.Label(new_frame, text="Description:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10, 0))
        self.new_work_description = scrolledtext.ScrolledText(
            new_frame,
            width=60,
            height=5,
            font=('EB Garamond', 10),
            bg='#786E00',
            fg='#000000',
            insertbackground='#000000'
        )
        self.new_work_description.pack(pady=5, padx=10)

        # Image upload for new
        tk.Label(new_frame, text="Images:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))

        self.new_available_image_list = tk.Listbox(
            new_frame,
            height=5,
            bg='#786E00',
            fg='#000000',
            font=('EB Garamond', 9),
            selectbackground='#000000',
            selectforeground='#786E00'
        )
        self.new_available_image_list.pack(fill='x', padx=10, pady=5)

        new_img_frame = tk.Frame(new_frame, bg='#786E00')
        new_img_frame.pack(fill='x', padx=10)

        tk.Button(new_img_frame, text="Browse for Images",
                 command=self.browse_available_images_new,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 9, 'bold')).pack(side='left', padx=5)
        tk.Button(new_img_frame, text="Clear Images",
                 command=self.clear_available_images_new,
                 bg='#8B0000', fg='#FFFFFF',
                 font=('EB Garamond', 9, 'bold')).pack(side='left', padx=5)

        tk.Button(new_frame, text="Add Available Work",
                 command=self.create_available_work,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold')).pack(pady=15)

    def browse_image(self, path_var):
        """Browse for single image file"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if filename:
            path_var.set(filename)

    def pick_images(self, title):
        """Ask for image files and keep only the ones a browser can show"""
        filenames = filedialog.askopenfilenames(
            title=title,
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.webp *.bmp"),
                ("All files", "*.*")
            ]
        )
        usable = [name for name in filenames if Path(name).suffix.lower() in WEB_IMAGE_EXTENSIONS]
        rejected = [Path(name).name for name in filenames if name not in usable]
        if rejected:
            messagebox.showerror("Error", "Web browsers can't show these files, so they were "
                                          "skipped. Save them as JPG first:\n\n" + "\n".join(rejected))
        return usable

    def browse_project_images_edit(self):
        """Browse for multiple images for editing project"""
        filenames = self.pick_images("Select Project Images")
        if filenames:
            self.edit_image_paths = list(filenames)
            messagebox.showinfo("Images Selected", f"Selected {len(filenames)} images")

    def browse_project_images_new(self):
        """Browse for multiple images for new project"""
        filenames = self.pick_images("Select Project Images (First image will be the main grid image)")
        if filenames:
            # Add to existing list rather than replacing
            for filename in filenames:
                if filename not in self.new_image_paths:
                    self.new_image_paths.append(filename)
                    self.new_image_list.insert(tk.END, Path(filename).name)

            # Show helpful info
            if len(self.new_image_paths) > 0:
                first_image = Path(self.new_image_paths[0]).name
                messagebox.showinfo("Images Selected",
                                   f"Selected {len(self.new_image_paths)} image(s).\n\n"
                                   f"Main grid image: {first_image}")

    def clear_new_images(self):
        """Clear selected images for new project"""
        self.new_image_paths = []
        self.new_image_list.delete(0, tk.END)

    def browse_available_images_new(self):
        """Browse for multiple images for a new available work"""
        filenames = self.pick_images("Select Available Work Images (first image will be used as the main image)")
        if filenames:
            for filename in filenames:
                if filename not in self.new_available_image_paths:
                    self.new_available_image_paths.append(filename)
            self.refresh_selected_available_images(self.new_available_image_list, self.new_available_image_paths)

    def browse_available_images_edit(self):
        """Browse for multiple images to replace an existing available work image set"""
        filenames = self.pick_images("Select Replacement Images")
        if filenames:
            self.edit_available_image_paths = list(filenames)
            self.refresh_selected_available_images(self.edit_available_image_list, self.edit_available_image_paths)

    def clear_available_images_new(self):
        """Clear selected images for a new available work"""
        self.new_available_image_paths = []
        self.refresh_selected_available_images(self.new_available_image_list, [])

    def clear_available_images_edit(self):
        """Clear selected replacement images for an existing available work"""
        self.edit_available_image_paths = []
        if self.current_available_id and hasattr(self, 'available_data'):
            work = self.available_data.get(self.current_available_id)
            if work:
                self.refresh_existing_available_images(work.get('images', []))
                return
        self.refresh_selected_available_images(self.edit_available_image_list, [])

    def refresh_selected_available_images(self, listbox, image_paths):
        """Populate a listbox with selected image file names"""
        listbox.delete(0, tk.END)
        for image_path in image_paths:
            listbox.insert(tk.END, Path(image_path).name)

    def get_project_image_names(self, folder_name):
        """Return project images in display order"""
        if not folder_name:
            return []

        folder_path = self.projects_base_dir / folder_name
        if not folder_path.exists():
            return []

        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        image_files = [path.name for path in folder_path.iterdir() if path.is_file() and path.suffix.lower() in supported_exts]

        def image_sort_key(name):
            # main first (main.png before main.jpg, matching the home-page grid),
            # then natural order so detail-2 precedes detail-10
            path = Path(name.lower())
            parts = [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', path.name)]
            if path.stem == 'main':
                return (0, path.suffix != '.png', parts)
            return (1, False, parts)

        images = sorted(image_files, key=image_sort_key)
        # Several folders hold both main.png and main.jpg; only one can be the hero,
        # so drop any extra main.* rather than pushing it into the gallery
        mains = [name for name in images if Path(name.lower()).stem == 'main']
        return mains[:1] + [name for name in images if name not in mains]

    def sanitize_filename(self, text):
        """Convert text to safe filename"""
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        sanitized = re.sub(r'\s+', '-', sanitized)
        return sanitized.lower().strip('-')[:50]

    def slugify(self, text):
        """Create a stable ID from a title"""
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'-{2,}', '-', slug)
        return slug[:80] or "available-work"

    def make_available_folder_name(self, title):
        """Create a web-safe folder name for available works"""
        return self.slugify(title)

    def supported_available_image_extensions(self):
        """Image extensions accepted for available works"""
        return {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

    def find_available_folder_path(self, folder_name):
        """Find an available-work folder, tolerating older case mismatches"""
        if not folder_name:
            return None

        direct_path = self.available_base_dir / folder_name
        if direct_path.exists():
            return direct_path

        folder_name_lower = folder_name.lower()
        for candidate in self.available_base_dir.iterdir():
            if candidate.is_dir() and candidate.name.lower() == folder_name_lower:
                return candidate

        return direct_path

    def ensure_available_folder(self, title, preferred_folder_name=None, create_if_missing=True):
        """Resolve an available-work folder path and normalize it to the canonical slug"""
        canonical_folder_name = self.make_available_folder_name(title)
        canonical_folder_path = self.available_base_dir / canonical_folder_name

        candidate_names = [preferred_folder_name, title, canonical_folder_name]
        for candidate_name in candidate_names:
            folder_path = self.find_available_folder_path(candidate_name)
            if not folder_path or not folder_path.exists():
                continue

            if folder_path.resolve() == canonical_folder_path.resolve():
                if create_if_missing:
                    canonical_folder_path.mkdir(parents=True, exist_ok=True)
                return canonical_folder_name, canonical_folder_path

            if canonical_folder_path.exists():
                canonical_images = self.get_available_image_names(canonical_folder_path)
                folder_images = self.get_available_image_names(folder_path)
                if folder_images and not canonical_images:
                    for image_name in folder_images:
                        shutil.move(str(folder_path / image_name), str(canonical_folder_path / image_name))
                    try:
                        folder_path.rmdir()
                    except OSError:
                        pass
                return canonical_folder_name, canonical_folder_path

            folder_path.rename(canonical_folder_path)
            return canonical_folder_name, canonical_folder_path

        if create_if_missing:
            canonical_folder_path.mkdir(parents=True, exist_ok=True)
        return canonical_folder_name, canonical_folder_path

    def get_available_image_names(self, folder_path):
        """Return available work images in display order"""
        if not folder_path.exists():
            return []

        supported_exts = self.supported_available_image_extensions()
        image_files = [path.name for path in folder_path.iterdir() if path.is_file() and path.suffix.lower() in supported_exts]

        def image_sort_key(name):
            lower = name.lower()
            # Natural order so detail-2 precedes detail-10
            parts = [int(p) if p.isdigit() else p for p in re.split(r'(\d+)', lower)]
            if 'main' in lower:
                return (0, parts)
            if 'detail' in lower:
                return (2, parts)
            return (1, parts)

        return sorted(image_files, key=image_sort_key)

    def scan_available_folders(self):
        """Build draft available work entries from folder structure"""
        scanned = {}
        for folder in sorted(self.available_base_dir.iterdir(), key=lambda p: p.name.lower()):
            if not folder.is_dir():
                continue

            images = self.get_available_image_names(folder)
            if not images:
                continue

            title = folder.name
            work_id = self.slugify(title)
            scanned[work_id] = {
                'id': work_id,
                'title': title,
                'price': '',
                'size': '',
                'description': '',
                'status': 'Available',
                'folder': folder.name,
                'images': images
            }

        return scanned

    def load_available_data(self):
        """Load available work data from JSON and existing folders"""
        self.available_data = {}

        if self.available_data_file.exists():
            try:
                with open(self.available_data_file, 'r', encoding='utf-8') as f:
                    stored_data = json.load(f)
                    if isinstance(stored_data, list):
                        self.available_data = {item['id']: item for item in stored_data if 'id' in item}
                    elif isinstance(stored_data, dict):
                        self.available_data = stored_data
            except Exception as e:
                print(f"Error loading available works: {e}")
                self.available_data = {}

        normalized_stored_data = {}
        for work_id, work in self.available_data.items():
            if not isinstance(work, dict):
                continue

            title = work.get('title', '')
            canonical_folder_name, folder_path = self.ensure_available_folder(title, work.get('folder', ''), create_if_missing=False)
            normalized_stored_data[work_id] = {
                'id': work.get('id', work_id),
                'title': title,
                'price': work.get('price', ''),
                'size': work.get('size', ''),
                'description': work.get('description', ''),
                'status': work.get('status', 'Available'),
                'folder': canonical_folder_name,
                'images': self.get_available_image_names(folder_path) if folder_path.exists() else work.get('images', [])
            }

        self.available_data = normalized_stored_data
        scanned_data = self.scan_available_folders()
        new_from_folders = {}

        for work_id, scanned in scanned_data.items():
            existing = self.available_data.get(work_id, {})
            merged = {
                'id': work_id,
                'title': existing.get('title') or scanned['title'],
                'price': existing.get('price', ''),
                'size': existing.get('size', ''),
                'description': existing.get('description', ''),
                'status': existing.get('status', 'Available'),
                'folder': existing.get('folder') or scanned['folder'],
                'images': scanned['images']
            }
            if work_id in self.available_data:
                self.available_data[work_id] = merged  # existing key keeps its position
            else:
                new_from_folders[work_id] = merged

        self.available_data = {**new_from_folders, **self.available_data}

        # Refresh image lists for entries whose folders already exist
        for work_id, work in list(self.available_data.items()):
            folder_name, folder_path = self.ensure_available_folder(work.get('title', ''), work.get('folder', ''), create_if_missing=False)
            work['folder'] = folder_name
            if folder_path.exists():
                work['images'] = self.get_available_image_names(folder_path)

        self.save_available_data()

    def save_available_data(self):
        """Persist available work data to JSON.

        Dict order is the display order on the Available page: newest at the top.
        """
        with open(self.available_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.available_data, f, indent=2, ensure_ascii=False)

    def refresh_available_dropdown(self):
        """Refresh the combobox choices for available works"""
        work_names = [f"{work_id}: {data['title']}" for work_id, data in sorted(self.available_data.items(), key=lambda item: item[1].get('title', '').lower())]
        self.available_select['values'] = work_names

    def refresh_project_image_list(self, image_names):
        """Show the images currently assigned to a project"""
        self.edit_project_image_list.delete(0, tk.END)
        for image_name in image_names:
            self.edit_project_image_list.insert(tk.END, image_name)

    def refresh_existing_available_images(self, image_names):
        """Show the images currently assigned to an available work"""
        self.edit_available_image_list.delete(0, tk.END)
        for image_name in image_names:
            self.edit_available_image_list.insert(tk.END, image_name)

    def copy_available_images_to_folder(self, image_paths, folder_path):
        """Copy selected available work images into the target folder using website-friendly names"""
        supported_exts = self.supported_available_image_extensions()
        folder_path.mkdir(parents=True, exist_ok=True)

        # Copy everything aside before deleting: the chosen files may be the ones in this
        # folder, and a missing file should fail before the current images are gone.
        with tempfile.TemporaryDirectory() as staging:
            saved_names = []
            for index, image_path in enumerate(image_paths):
                source = Path(image_path)
                extension = source.suffix.lower()
                filename = f"main{extension}" if index == 0 else f"detail-{index}{extension}"
                shutil.copy2(source, Path(staging) / filename)
                saved_names.append(filename)

            for existing in folder_path.iterdir():
                if existing.is_file() and existing.suffix.lower() in supported_exts:
                    existing.unlink()

            for filename in saved_names:
                shutil.move(str(Path(staging) / filename), str(folder_path / filename))

        return saved_names

    def sync_available_outputs(self):
        """Rebuild available-work JSON, JS, and sitemap from current folder contents"""
        for work_id, work in list(self.available_data.items()):
            folder_name, folder_path = self.ensure_available_folder(work.get('title', ''), work.get('folder', ''), create_if_missing=False)
            work['id'] = work_id
            work['folder'] = folder_name
            work['images'] = self.get_available_image_names(folder_path) if folder_path.exists() else []

        self.save_available_data()
        self.generate_available_data_js()
        self.regenerate_sitemap()
        self.refresh_available_dropdown()

    def generate_available_data_js(self):
        """Generate the frontend data file used by the available pages"""
        works = []
        for work_id, work in self.available_data.items():
            works.append({
                'id': work_id,
                'title': work.get('title', ''),
                'price': work.get('price', ''),
                'size': work.get('size', ''),
                'description': work.get('description', ''),
                'status': work.get('status', 'Available'),
                'folder': work.get('folder', ''),
                'images': work.get('images', [])
            })

        content = "window.availableWorks = " + json.dumps(works, indent=2, ensure_ascii=False) + ";\n"
        with open(self.available_data_js, 'w', encoding='utf-8') as f:
            f.write(content)

    def regenerate_sitemap(self):
        """Regenerate the sitemap including available work detail pages"""
        base_urls = [
            "https://rachaeljuzeler.com/",
            "https://rachaeljuzeler.com/about.html",
            "https://rachaeljuzeler.com/contact.html",
            "https://rachaeljuzeler.com/updates.html",
            "https://rachaeljuzeler.com/available.html"
        ]

        project_urls = [
            f"https://rachaeljuzeler.com/project.html?id={project_id}"
            for project_id in sorted(self.projects_data.keys(), key=lambda value: int(re.sub(r'[^0-9]', '', value) or 0))
        ]
        available_urls = [
            f"https://rachaeljuzeler.com/available-piece.html?id={work_id}"
            for work_id in sorted(self.available_data.keys())
        ]

        piece_urls = [
            f"https://rachaeljuzeler.com/piece.html?project={project_id}&amp;id={piece['id']}"
            for project_id, entry in sorted((self.load_project_pieces() or {}).items())
            if project_id in self.projects_data
            for piece in entry.get('pieces', [])
        ]

        url_lines = []
        for url in base_urls + project_urls + piece_urls + available_urls:
            url_lines.append("  <url>")
            url_lines.append(f"    <loc>{url}</loc>")
            url_lines.append("  </url>")

        sitemap_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        sitemap_content += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        sitemap_content += "\n".join(url_lines)
        sitemap_content += "\n</urlset>\n"

        with open(self.sitemap_xml, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

    def load_data(self):
        """Load project, news, and available-work data and refresh the generated site files"""
        self.check_data_files()

        # admin_data/projects.json is the source of truth for projects; project-data.js
        # is generated from it (same pattern as available works).
        self.load_projects_data()
        self.sync_project_outputs()

        # Load news data and refresh related files
        self.load_news_data()
        self.sync_news_outputs()

        # Load available works data and refresh related files
        self.load_available_data()
        self.sync_available_outputs()

        self.load_pieces_data()
        self.load_bio()
        self.load_contact_fields()

    def check_data_files(self):
        """Stop before anything is saved if a data file can't be read.

        Startup rewrites every generated file, so carrying on with an unreadable file
        (usually git merge conflict markers) would replace its contents with nothing.
        """
        for data_file in (self.projects_data_file, self.project_pieces_file,
                          self.news_data_file, self.available_data_file):
            if not data_file.exists():
                continue
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except (OSError, ValueError) as e:
                messagebox.showerror(
                    "Cannot Start",
                    f"admin_data/{data_file.name} can't be read, so the manager is closing "
                    f"without changing anything. Fix or restore that file first.\n\n{e}"
                )
                raise SystemExit(1)

    def load_projects_data(self):
        """Load projects from the JSON store"""
        self.projects_data = {}
        if not self.projects_data_file.exists():
            return

        try:
            with open(self.projects_data_file, 'r', encoding='utf-8') as f:
                stored = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not read {self.projects_data_file.name}: {e}")
            return

        for project_id, project in stored.items():
            self.projects_data[project_id] = {
                'title': project.get('title', ''),
                'subtitle': project.get('subtitle', ''),
                'description': project.get('description', ''),
                'folder': project.get('folder', project_id),
                'images': project.get('images', [])
            }

    def save_projects_data(self):
        """Save projects data to JSON file"""
        with open(self.projects_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.projects_data, f, indent=2, ensure_ascii=False)

    def project_sort_key(self, project_id):
        return int(re.sub(r'[^0-9]', '', project_id) or 0)

    def next_project_id(self):
        """Next unused projectN id (len()-based ids collide after a delete)"""
        highest = max((self.project_sort_key(pid) for pid in self.projects_data), default=0)
        return f"project{highest + 1}"

    def refresh_project_dropdown(self):
        project_names = [
            f"{pid}: {self.projects_data[pid]['title']}"
            for pid in sorted(self.projects_data, key=self.project_sort_key)
        ]
        self.project_select['values'] = project_names

    def sync_project_outputs(self):
        """Rebuild project JSON, JS, and sitemap from current folder contents"""
        for project_id, project in self.projects_data.items():
            folder_name = project.get('folder', project_id)
            # Keep the stored list if the folder is missing so a bad path does not wipe it
            if (self.projects_base_dir / folder_name).is_dir():
                project['images'] = self.get_project_image_names(folder_name)

        self.save_projects_data()
        self.generate_project_data_js()
        self.generate_project_pieces_js()
        self.regenerate_sitemap()
        self.refresh_project_dropdown()

    def generate_project_data_js(self):
        """Generate the frontend data file used by project.html"""
        projects = {}
        for project_id in sorted(self.projects_data, key=self.project_sort_key):
            project = self.projects_data[project_id]
            projects[project_id] = {
                'title': project.get('title', ''),
                'subtitle': project.get('subtitle', ''),
                'description': project.get('description', ''),
                'folder': project.get('folder', project_id),
                'images': project.get('images', [])
            }

        content = "window.projectData = " + json.dumps(projects, indent=2, ensure_ascii=False) + ";\n"
        with open(self.project_data_js, 'w', encoding='utf-8') as f:
            f.write(content)

    def load_project_pieces(self):
        """Read admin_data/project_pieces.json ({project_id: {"pieces": [...]}})"""
        if not self.project_pieces_file.exists():
            return {}
        try:
            with open(self.project_pieces_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not read {self.project_pieces_file.name}: {e}")
            return None

    def load_pieces_data(self):
        """Load pieces for the PIECES tab and select the first project that has any"""
        self.pieces_data = self.load_project_pieces() or {}
        self.pieces_project_select['values'] = [
            f"{project_id}: {self.projects_data.get(project_id, {}).get('title', project_id)}"
            for project_id in self.pieces_data
        ]
        if self.pieces_data:
            self.pieces_project_select.current(0)
            self.on_pieces_project_selected(None)

    def on_pieces_project_selected(self, event):
        """Show the chosen project's pieces"""
        self.current_pieces_project = self.pieces_project_select.get().split(':')[0]
        self.clear_piece_form()
        self.refresh_piece_dropdown()

    def project_piece_list(self):
        """Pieces of the chosen project, in page order"""
        return self.pieces_data.get(self.current_pieces_project, {}).get('pieces', [])

    def current_piece(self):
        """The piece being edited, or None"""
        return next((piece for piece in self.project_piece_list()
                     if piece['id'] == self.current_piece_id), None)

    def piece_label(self, piece):
        return f"{piece['id']}: {piece.get('title', '')}"

    def refresh_piece_dropdown(self):
        self.piece_select['values'] = [self.piece_label(piece) for piece in self.project_piece_list()]

    def piece_folder(self, piece):
        """A piece's image folder, resolved the same way as getPieceImagePath in script.js"""
        entry = self.pieces_data[self.current_pieces_project]
        return (self.projects_base_dir / (entry.get('image_dir') or self.current_pieces_project)
                / (piece.get('folder') or piece['id']))

    def rescan_piece_images(self, piece):
        folder_path = self.piece_folder(piece)
        piece['images'] = self.get_project_image_names(folder_path.relative_to(self.projects_base_dir))

    def sync_piece_outputs(self):
        """Save pieces and rebuild the files the site reads"""
        with open(self.project_pieces_file, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(self.pieces_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        self.generate_project_pieces_js()
        self.regenerate_sitemap()
        self.refresh_piece_dropdown()

    def clear_piece_form(self):
        """Empty the edit form so nothing can be saved over the wrong piece"""
        self.current_piece_id = None
        self.piece_select.set('')
        for field in self.edit_piece_fields.values():
            field.delete(0, tk.END)
        self.edit_piece_description.delete('1.0', tk.END)
        self.edit_piece_image_list.delete(0, tk.END)

    def refresh_piece_images(self, piece):
        self.edit_piece_image_list.delete(0, tk.END)
        for image_name in piece.get('images', []):
            self.edit_piece_image_list.insert(tk.END, image_name)

    def on_piece_selected(self, event):
        """Load the selected piece into the form"""
        self.current_piece_id = self.piece_select.get().split(':')[0]
        piece = self.current_piece()
        if not piece:
            return
        for key, field in self.edit_piece_fields.items():
            field.delete(0, tk.END)
            field.insert(0, piece.get(key, ''))
        self.edit_piece_description.delete('1.0', tk.END)
        self.edit_piece_description.insert('1.0', piece.get('description', ''))
        self.refresh_piece_images(piece)

    def update_piece(self):
        """Save the form. The id and folder stay put so existing links and photos keep working."""
        piece = self.current_piece()
        if not piece:
            messagebox.showerror("Error", "Please select a piece to update.")
            return
        values = {key: field.get().strip() for key, field in self.edit_piece_fields.items()}
        if not values['title']:
            messagebox.showerror("Error", "Please enter a title.")
            return

        piece.update(values)
        piece['description'] = self.edit_piece_description.get('1.0', 'end-1c').strip()
        try:
            self.sync_piece_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            return
        self.piece_select.set(self.piece_label(piece))
        messagebox.showinfo("Success", f"Updated '{piece['title']}'.")

    def add_piece_images(self):
        """Add photos to the selected piece; saved right away, existing photos are kept"""
        piece = self.current_piece()
        if not piece:
            messagebox.showerror("Error", "Please select a piece first.")
            return
        filenames = self.pick_images("Select Images (the first becomes main if there is none yet)")
        if not filenames:
            return
        try:
            self.copy_project_images_to_folder(filenames, self.piece_folder(piece))
            self.rescan_piece_images(piece)
            self.sync_piece_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to add images: {e}")
            return
        self.refresh_piece_images(piece)

    def remove_piece_image(self):
        """Delete the image selected in the piece's list"""
        piece = self.current_piece()
        selected = self.edit_piece_image_list.curselection()
        if not piece or not selected:
            messagebox.showerror("Error", "Select a piece and click an image in its list first.")
            return
        image_name = self.edit_piece_image_list.get(selected[0])
        if not messagebox.askyesno("Remove Image", f"Delete {image_name} from this piece?",
                                   icon='warning'):
            return
        try:
            self.remove_image_file(self.piece_folder(piece), image_name)
            self.rescan_piece_images(piece)
            self.sync_piece_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to remove image: {e}")
            return
        self.refresh_piece_images(piece)

    def move_piece(self, step):
        """Move the selected piece in the grid"""
        pieces = self.project_piece_list()
        piece = self.current_piece()
        if not piece:
            messagebox.showerror("Error", "Please select a piece to move.")
            return
        index = pieces.index(piece)
        target = index + step
        if 0 <= target < len(pieces):
            # `num` is left alone: it is Rachael's own catalog number and the site doesn't read it
            pieces[index], pieces[target] = pieces[target], pieces[index]
            self.sync_piece_outputs()

    def delete_piece(self):
        """Delete a piece and its photo folder"""
        piece = self.current_piece()
        if not piece:
            messagebox.showerror("Error", "Please select a piece to delete.")
            return
        if not messagebox.askyesno("Delete Piece",
                                   f"Delete '{piece.get('title', '')}' from the site?\n\n"
                                   "This also removes its image folder.", icon='warning'):
            return
        try:
            folder_path = self.piece_folder(piece)
            if folder_path.exists():
                shutil.rmtree(folder_path)
            self.project_piece_list().remove(piece)
            self.sync_piece_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to delete piece: {e}")
            return
        self.clear_piece_form()
        messagebox.showinfo("Success", "Piece deleted.")

    def browse_new_piece_images(self):
        for filename in self.pick_images("Select Images (the first becomes the main image)"):
            if filename not in self.new_piece_image_paths:
                self.new_piece_image_paths.append(filename)
                self.new_piece_image_list.insert(tk.END, Path(filename).name)

    def clear_new_piece_images(self):
        self.new_piece_image_paths = []
        self.new_piece_image_list.delete(0, tk.END)

    def create_piece(self):
        """Add a piece at the end of the chosen project's grid"""
        if self.current_pieces_project not in self.pieces_data:
            messagebox.showerror("Error", "No project with pieces is selected.")
            return
        values = {key: field.get().strip() for key, field in self.new_piece_fields.items()}
        if not values['title']:
            messagebox.showerror("Error", "Please enter a title.")
            return

        piece_id = self.slugify(values['title'])
        pieces = self.project_piece_list()
        if any(piece['id'] == piece_id for piece in pieces):
            messagebox.showerror("Error", "A piece with this title already exists. Please use a different title.")
            return

        piece = {
            'num': max((item.get('num', 0) for item in pieces), default=0) + 1,
            'id': piece_id,
            'title': values['title'],
            'year': values['year'],
            'medium': values['medium'],
            'size': values['size'],
            'description': self.new_piece_description.get('1.0', 'end-1c').strip(),
            'folder': piece_id,
            'images': []
        }
        try:
            if self.new_piece_image_paths:
                self.copy_project_images_to_folder(self.new_piece_image_paths, self.piece_folder(piece))
                self.rescan_piece_images(piece)
            pieces.append(piece)
            self.sync_piece_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to add piece: {e}")
            return

        for field in self.new_piece_fields.values():
            field.delete(0, tk.END)
        self.new_piece_description.delete('1.0', tk.END)
        self.clear_new_piece_images()
        note = "" if piece['images'] else "\n\nNo photos yet, so the site shows a stand-in image."
        messagebox.showinfo("Success", f"Added '{piece['title']}'. Use Move Up to place it.{note}")

    def generate_project_pieces_js(self):
        """Generate project-pieces-data.js used by project.html and piece.html"""
        pieces = self.load_project_pieces()
        if pieces is None:
            # Unreadable JSON: leave the existing JS alone rather than publishing an empty grid
            return
        content = "window.projectPieces = " + json.dumps(pieces, indent=2, ensure_ascii=False) + ";\n"
        with open(self.project_pieces_js, 'w', encoding='utf-8') as f:
            f.write(content)

    def copy_project_images_to_folder(self, image_paths, folder_path):
        """Copy images into a project folder using the names the site looks for.

        Existing images are kept: the first new image becomes main.* only if the
        folder has no main image yet, the rest continue the detail-N sequence.
        """
        folder_path.mkdir(parents=True, exist_ok=True)
        existing = self.get_project_image_names(folder_path.relative_to(self.projects_base_dir))
        has_main = any(Path(name).stem.lower() == 'main' for name in existing)
        detail_numbers = [
            int(m.group(1)) for m in (re.match(r'detail-(\d+)$', Path(name).stem.lower()) for name in existing) if m
        ]
        next_detail = max(detail_numbers, default=0) + 1

        saved_names = []
        for image_path in image_paths:
            source = Path(image_path)
            if not source.exists():
                messagebox.showwarning("Warning", f"Image not found, skipped: {source.name}")
                continue
            extension = source.suffix.lower()
            if not has_main:
                filename = f"main{extension}"
                has_main = True
            else:
                filename = f"detail-{next_detail}{extension}"
                next_detail += 1
            shutil.copy2(source, folder_path / filename)
            saved_names.append(filename)

        return saved_names

    def html_escape(self, text):
        return (str(text).replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))

    def add_project_to_index(self, project_id, title):
        """Append a work tile for a new project to the index.html grid"""
        with open(self.index_html, 'r', encoding='utf-8') as f:
            html = f.read()

        marker = "            <!-- Add more work items as needed -->"
        if marker not in html or f'data-project="{project_id}"' in html:
            return False

        safe_title = self.html_escape(title)
        tile = (
            f"            <!-- Work Item {self.project_sort_key(project_id)} -->\n"
            f"            <div class=\"work-container\">\n"
            f"                <a class=\"work-item\" href=\"project.html?id={project_id}\" data-project=\"{project_id}\" aria-label=\"View project: {safe_title}\">\n"
            f"                    <div class=\"work-item-image\"></div>\n"
            f"                </a>\n"
            f"                <div class=\"work-item-title\">{safe_title}</div>\n"
            f"            </div>\n\n"
        )
        html = html.replace(marker, tile + marker, 1)
        with open(self.index_html, 'w', encoding='utf-8') as f:
            f.write(html)
        return True

    def remove_project_from_index(self, project_id):
        """Remove a project's work tile from the index.html grid"""
        with open(self.index_html, 'r', encoding='utf-8') as f:
            html = f.read()

        anchor = html.find(f'data-project="{project_id}"')
        if anchor == -1:
            return False

        # Tile = "<!-- Work Item N -->" comment through the work-container's closing
        # </div>, which sits at the same 12-space indent as the comment.
        start = html.rfind("            <!-- Work Item", 0, anchor)
        end = html.find("\n            </div>\n", anchor)
        if start == -1 or end == -1:
            return False
        end += len("\n            </div>\n")
        if html[end:end + 1] == "\n":
            end += 1

        with open(self.index_html, 'w', encoding='utf-8') as f:
            f.write(html[:start] + html[end:])
        return True

    def normalize_news_item(self, item_id, item):
        """Normalize a news record to the fields used by the site"""
        if not isinstance(item, dict):
            item = {}

        return {
            'id': item.get('id', item_id),
            'title': item.get('title', '').strip(),
            'intro': item.get('intro', '').strip(),
            'url': item.get('url', '').strip(),
            'source': item.get('source', '').strip(),
            'category': item.get('category', '').strip(),
            'year': item.get('year', '').strip(),
            'image': item.get('image', '').strip(),
            'linkLabel': item.get('linkLabel', '').strip()
        }

    def load_news_data(self):
        """Load news data from JSON"""
        self.news_data = {}

        if not self.news_data_file.exists():
            return

        try:
            with open(self.news_data_file, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
        except Exception as e:
            print(f"Error loading news data: {e}")
            return

        if isinstance(stored_data, list):
            for index, item in enumerate(stored_data, start=1):
                if not isinstance(item, dict):
                    continue
                item_id = item.get('id') or self.slugify(item.get('title', '')) or f"news-{index}"
                self.news_data[item_id] = self.normalize_news_item(item_id, item)
        elif isinstance(stored_data, dict):
            for item_id, item in stored_data.items():
                self.news_data[item_id] = self.normalize_news_item(item_id, item)

    def save_news_data(self):
        """Persist news data to JSON"""
        with open(self.news_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.news_data, f, indent=2, ensure_ascii=False)

    def generate_news_data_js(self):
        """Generate the frontend data file used by the News page"""
        items = []
        for item_id, item in self.news_data.items():
            normalized = self.normalize_news_item(item_id, item)
            normalized['id'] = item_id
            items.append(normalized)

        content = "window.newsItems = " + json.dumps(items, indent=2, ensure_ascii=False) + ";\n"
        with open(self.news_data_js, 'w', encoding='utf-8') as f:
            f.write(content)

    def refresh_news_dropdown(self):
        """Refresh the combobox choices for news entries"""
        self.news_select['values'] = [f"{item_id}: {item.get('title', item_id)}" for item_id, item in self.news_data.items()]

    def sync_news_outputs(self):
        """Save news data, rebuild the frontend file, and refresh related UI"""
        normalized_items = {}
        for item_id, item in self.news_data.items():
            normalized_items[item_id] = self.normalize_news_item(item_id, item)

        self.news_data = normalized_items
        self.save_news_data()
        self.generate_news_data_js()
        self.regenerate_sitemap()
        self.refresh_news_dropdown()

    def populate_news_form(self, item_id):
        """Load a news item into the edit form"""
        item = self.news_data.get(item_id)
        if not item:
            return

        self.current_news_id = item_id
        self.news_editing_label.config(text=f"Currently editing: {item.get('title', item_id)} ({item_id})")

        self.edit_news_title.delete(0, tk.END)
        self.edit_news_title.insert(0, item.get('title', ''))

        self.edit_news_intro.delete('1.0', tk.END)
        self.edit_news_intro.insert('1.0', item.get('intro', ''))

        self.edit_news_url.delete(0, tk.END)
        self.edit_news_url.insert(0, item.get('url', ''))

        self.edit_news_source.delete(0, tk.END)
        self.edit_news_source.insert(0, item.get('source', ''))

        self.edit_news_category.delete(0, tk.END)
        self.edit_news_category.insert(0, item.get('category', ''))

        self.edit_news_year.delete(0, tk.END)
        self.edit_news_year.insert(0, item.get('year', ''))

        self.edit_news_image.delete(0, tk.END)
        self.edit_news_image.insert(0, item.get('image', ''))

        self.edit_news_link_label.delete(0, tk.END)
        self.edit_news_link_label.insert(0, item.get('linkLabel', ''))

    def clear_news_form(self):
        """Clear the add-news fields after a successful save"""
        self.new_news_title.delete(0, tk.END)
        self.new_news_intro.delete('1.0', tk.END)
        self.new_news_url.delete(0, tk.END)
        self.new_news_source.delete(0, tk.END)
        self.new_news_category.delete(0, tk.END)
        self.new_news_year.delete(0, tk.END)
        self.new_news_image.delete(0, tk.END)
        self.new_news_link_label.delete(0, tk.END)

    def on_project_selected(self, event):
        """Handle project selection and populate form fields with existing data"""
        selection = self.project_select.get()
        if not selection:
            return

        project_id = selection.split(':')[0]
        if project_id in self.projects_data:
            project = self.projects_data[project_id]
            project_images = project.get('images') or self.get_project_image_names(project.get('folder', project_id))

            # Clear and populate title field
            self.edit_project_title.delete(0, tk.END)
            self.edit_project_title.insert(0, project.get('title', ''))

            # Clear and populate subtitle field
            self.edit_project_subtitle.delete(0, tk.END)
            self.edit_project_subtitle.insert(0, project.get('subtitle', ''))

            # Clear and populate description field
            self.edit_project_description.delete('1.0', tk.END)
            self.edit_project_description.insert('1.0', project.get('description', ''))

            self.edit_project_home_title.delete(0, tk.END)
            self.edit_project_home_title.insert(0, self.home_tile_title(project_id))

            # Images picked for the previous project must not land in this one
            self.edit_image_paths = []

            # Store the current project ID for updates
            self.current_project_id = project_id
            self.project_editing_label.config(text=f"Currently editing: {project.get('title', project_id)} ({project_id})")
            self.edit_project_folder_label.config(text=f"images/{project.get('folder', project_id)}")
            self.refresh_project_image_list(project_images)

    def on_cv_section_selected(self, event):
        """Load the selected CV section into the box, keeping any unsaved text if asked"""
        label = self.cv_section_select.get()
        typed_text = self.cv_content.get('1.0', 'end-1c').strip()
        if typed_text and self.cv_content.edit_modified():
            if not messagebox.askyesno("Unsaved Text",
                                       f"The box has unsaved text. Replace it with the current "
                                       f"'{label}' list?"):
                self.cv_section_select.set(self.current_cv_section or '')
                return
        self.load_cv_section(label)

    def read_page(self, path):
        """Read a page; newline='' keeps its line endings exactly as they are"""
        with open(path, 'r', encoding='utf-8', newline='') as f:
            return f.read()

    def write_page(self, path, page):
        """Write a page without changing its line endings"""
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(page)

    def load_cv_section(self, label):
        """Fill the box with a section's current items so saving keeps them"""
        self.current_cv_section = None
        self.cv_content.delete('1.0', tk.END)
        try:
            lines = cv_section_lines(self.read_page(self.about_html), label)
        except (OSError, ValueError) as e:
            self.cv_section_select.set('')
            self.cv_content.edit_modified(False)
            messagebox.showerror("Error", f"Could not load '{label}': {e}")
            return

        self.cv_content.insert('1.0', "\n".join(lines))
        self.cv_content.edit_modified(False)
        self.current_cv_section = label

    def on_news_selected(self, event):
        """Handle news selection"""
        selection = self.news_select.get()
        if not selection:
            return

        item_id = selection.split(':')[0]
        self.populate_news_form(item_id)

    def on_available_selected(self, event):
        """Handle available work selection"""
        selection = self.available_select.get()
        if not selection:
            return

        work_id = selection.split(':')[0]
        work = self.available_data.get(work_id)
        if not work:
            return

        self.current_available_id = work_id
        self.edit_work_title.delete(0, tk.END)
        self.edit_work_title.insert(0, work.get('title', ''))

        self.edit_work_price.delete(0, tk.END)
        self.edit_work_price.insert(0, work.get('price', ''))

        self.edit_work_size.delete(0, tk.END)
        self.edit_work_size.insert(0, work.get('size', ''))

        self.edit_work_status.set(work.get('status', 'Available'))

        self.edit_work_description.delete('1.0', tk.END)
        self.edit_work_description.insert('1.0', work.get('description', ''))

        folder_name, folder_path = self.ensure_available_folder(work.get('title', ''), work.get('folder', ''), create_if_missing=False)
        work['folder'] = folder_name
        work['images'] = self.get_available_image_names(folder_path) if folder_path.exists() else []
        self.available_editing_label.config(text=self.available_editing_text())
        self.edit_work_folder_label.config(text=f"images/available/{folder_name}")
        self.edit_available_image_paths = []
        self.refresh_existing_available_images(work.get('images', []))

    def create_project(self):
        """Create new project"""
        title = self.new_project_title.get().strip()
        subtitle = self.new_project_subtitle.get().strip()
        description = self.new_project_description.get('1.0', 'end-1c').strip()

        if not title or not description:
            messagebox.showerror("Error", "Please fill in title and description")
            return

        if not self.new_image_paths:
            messagebox.showerror("Error", "Please select at least one image for the project")
            return

        project_id = self.next_project_id()
        project_folder = self.projects_base_dir / project_id

        try:
            image_filenames = self.copy_project_images_to_folder(self.new_image_paths, project_folder)
            if not image_filenames:
                messagebox.showerror("Error", "None of the selected images could be copied.")
                return

            self.projects_data[project_id] = {
                'title': title,
                'subtitle': subtitle,
                'description': description,
                'folder': project_id,
                'images': image_filenames
            }

            self.sync_project_outputs()
            added_tile = self.add_project_to_index(project_id, title)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {e}")
            return

        messagebox.showinfo("Success",
                            f"Project '{title}' created successfully!\n\n"
                            f"Project ID: {project_id}\n"
                            f"Images copied: {len(image_filenames)}\n"
                            f"Folder created: images/{project_id}/\n"
                            f"Home page tile: {'added' if added_tile else 'NOT added (edit index.html by hand)'}")

        # Clear form
        self.new_project_title.delete(0, tk.END)
        self.new_project_subtitle.delete(0, tk.END)
        self.new_project_description.delete('1.0', tk.END)
        self.new_image_paths = []
        self.new_image_list.delete(0, tk.END)

    def home_tile_title(self, project_id):
        """Current text on a project's home page tile, blank if it has none"""
        try:
            tile = find_home_tile(self.read_page(self.index_html), project_id)
        except OSError:
            return ''
        return unescape(tile.group(4)) if tile else ''

    def update_home_tile(self, project_id, project_title, home_title):
        """Write a project's tile text to index.html; False if it has no tile"""
        page = self.read_page(self.index_html)
        new_page = replace_home_tile(page, project_id, project_title, home_title)
        if new_page is None:
            return False
        if new_page != page:
            self.write_page(self.index_html, new_page)
        return True

    def remove_image_file(self, folder_path, image_name):
        """Delete an image; the next one becomes main.* because the home page tile needs one"""
        (folder_path / image_name).unlink()
        if Path(image_name).stem.lower() != 'main':
            return
        remaining = self.get_project_image_names(folder_path.relative_to(self.projects_base_dir))
        if remaining and not any(Path(name).stem.lower() == 'main' for name in remaining):
            first = folder_path / remaining[0]
            first.rename(folder_path / f"main{first.suffix.lower()}")

    def remove_project_image(self):
        """Delete the image selected in the project's list"""
        project = self.projects_data.get(self.current_project_id)
        selected = self.edit_project_image_list.curselection()
        if not project or not selected:
            messagebox.showerror("Error", "Select a project and click an image in its list first.")
            return

        image_name = self.edit_project_image_list.get(selected[0])
        if self.edit_project_image_list.size() == 1:
            messagebox.showerror("Error", "A project must keep at least one image.")
            return
        if not messagebox.askyesno("Remove Image", f"Delete {image_name} from this project?",
                                   icon='warning'):
            return

        try:
            folder_path = self.projects_base_dir / project.get('folder', self.current_project_id)
            self.remove_image_file(folder_path, image_name)
            self.sync_project_outputs()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to remove image: {e}")
            return
        self.refresh_project_image_list(project.get('images', []))

    def update_project(self):
        """Update existing project with new data"""
        if not self.current_project_id or self.current_project_id not in self.projects_data:
            messagebox.showerror("Error", "Please select a project to update")
            return

        # Get updated values from form
        title = self.edit_project_title.get().strip()
        subtitle = self.edit_project_subtitle.get().strip()
        description = self.edit_project_description.get('1.0', 'end-1c').strip()

        if not title or not description:
            messagebox.showerror("Error", "Please fill in title and description")
            return

        project = self.projects_data[self.current_project_id]
        old_title = project.get('title', '')
        home_title = self.edit_project_home_title.get().strip()
        # A tile that matched the old title follows the rename; a custom one stays
        if home_title == old_title:
            home_title = title

        try:
            project.update({
                'title': title,
                'subtitle': subtitle,
                'description': description
            })

            added = []
            if self.edit_image_paths:
                project_folder = self.projects_base_dir / project.get('folder', self.current_project_id)
                added = self.copy_project_images_to_folder(self.edit_image_paths, project_folder)
                self.edit_image_paths = []

            # Writes projects.json, project-data.js, sitemap.xml and rescans the folder
            self.sync_project_outputs()
            has_tile = self.update_home_tile(self.current_project_id,
                                             title if title != old_title else None, home_title)

            self.project_select.set(f"{self.current_project_id}: {title}")
            self.refresh_project_image_list(project.get('images', []))
            self.edit_project_home_title.delete(0, tk.END)
            self.edit_project_home_title.insert(0, self.home_tile_title(self.current_project_id))

            messagebox.showinfo("Success",
                                f"Project '{title}' updated.\n\n"
                                f"Images added: {len(added)}\n"
                                f"Home page tile: {'updated' if has_tile else 'NOT found (edit index.html by hand)'}\n"
                                f"project-data.js regenerated. Commit and push to publish.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update project: {e}")

    def delete_project(self):
        """Delete project with confirmation"""
        if not self.current_project_id:
            messagebox.showerror("Error", "Please select a project to delete")
            return

        project = self.projects_data.get(self.current_project_id)
        if not project:
            messagebox.showerror("Error", "Project not found")
            return

        # Confirmation dialog
        result = messagebox.askyesno(
            "Delete Project",
            f"Are you sure you want to delete the project:\n\n'{project['title']}'\n\n"
            f"This removes it from the site. The image folder images/{project.get('folder', self.current_project_id)}/ is left in place.",
            icon='warning'
        )

        if result:
            try:
                deleted_id = self.current_project_id
                del self.projects_data[deleted_id]
                self.sync_project_outputs()
                removed_tile = self.remove_project_from_index(deleted_id)

                # Clear the form
                self.edit_project_title.delete(0, tk.END)
                self.edit_project_subtitle.delete(0, tk.END)
                self.edit_project_description.delete('1.0', tk.END)
                self.edit_project_home_title.delete(0, tk.END)
                self.refresh_project_image_list([])
                self.project_editing_label.config(text="No project selected")
                self.edit_project_folder_label.config(text="No project selected")
                self.project_select.set('')
                self.current_project_id = None

                messagebox.showinfo("Success",
                                    f"Project '{project['title']}' has been deleted.\n\n"
                                    f"Home page tile: {'removed' if removed_tile else 'NOT found (edit index.html by hand)'}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project: {e}")

    def load_bio(self):
        """Fill the bio box from about.html"""
        self.bio_text.delete('1.0', tk.END)
        try:
            paragraphs = bio_paragraphs(self.read_page(self.about_html))
        except (OSError, ValueError) as e:
            messagebox.showwarning("Warning", f"Could not load the biography: {e}")
            return
        self.bio_text.insert('1.0', "\n\n".join(paragraphs))

    def update_bio(self):
        """Rewrite the biography in about.html from the box"""
        text = self.bio_text.get('1.0', 'end-1c')
        # A paragraph is one <p>, so line breaks inside it (pasted text) become spaces
        paragraphs = [' '.join(block.split()) for block in re.split(r'\n\s*\n', text) if block.strip()]
        if not paragraphs:
            messagebox.showerror("Error", "The box is empty, so the biography was not changed.")
            return

        try:
            page = self.read_page(self.about_html)
            bio_paragraphs(page)  # refuses a bio holding formatting this would drop
            self.write_page(self.about_html, replace_bio(page, paragraphs))
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to update the biography: {e}")
            return

        self.load_bio()
        messagebox.showinfo("Success", f"Updated the biography ({len(paragraphs)} paragraphs).")

    def update_cv_section(self):
        """Rewrite the loaded CV section in about.html from the box"""
        label = self.current_cv_section
        if not label:
            messagebox.showerror("Error", "Select a CV section first. Its current items will "
                                          "load into the box so you can add to them.")
            return

        lines = [line.strip() for line in self.cv_content.get('1.0', 'end-1c').splitlines()
                 if line.strip()]
        if not lines:
            messagebox.showerror("Error", f"The box is empty, so '{label}' was not changed.")
            return

        try:
            page = self.read_page(self.about_html)
            old_lines = cv_section_lines(page, label)
            new_page = replace_cv_section(page, label, lines)
            new_lines = cv_section_lines(new_page, label)
            self.write_page(self.about_html, new_page)
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to update '{label}': {e}")
            return

        # Reload so the box shows what was saved (blank lines gone, dashes normalized)
        self.load_cv_section(label)
        added = len(set(new_lines) - set(old_lines))
        removed = len(set(old_lines) - set(new_lines))
        messagebox.showinfo("Success", f"Updated '{label}': {len(new_lines)} items "
                                       f"({added} added, {removed} removed).")

    def browse_news_image(self, entry):
        """Copy a chosen photo into images/news and put its path in the field"""
        filenames = self.pick_images("Select News Preview Image")
        if not filenames:
            return

        source = Path(filenames[0])
        extension = source.suffix.lower()
        stem = self.slugify(source.stem)
        folder_path = self.projects_base_dir / "news"
        destination = folder_path / f"{stem}{extension}"
        # Another news item may already use this name, and overwriting would change its picture
        counter = 2
        while destination.exists():
            destination = folder_path / f"{stem}-{counter}{extension}"
            counter += 1

        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        except OSError as e:
            messagebox.showerror("Error", f"Failed to copy image: {e}")
            return
        entry.delete(0, tk.END)
        entry.insert(0, f"images/news/{destination.name}")

    def move_news_item(self, step):
        """Move the selected item on the News page (dropdown order is page order)"""
        if not self.current_news_id:
            messagebox.showerror("Error", "Please select a news item to move.")
            return
        self.news_data = move_entry(self.news_data, self.current_news_id, step)
        self.sync_news_outputs()

    def create_news_item(self):
        """Create a new news item"""
        title = self.new_news_title.get().strip()
        intro = self.new_news_intro.get('1.0', 'end-1c').strip()
        url = self.new_news_url.get().strip()
        source = self.new_news_source.get().strip()
        category = self.new_news_category.get().strip()
        year = self.new_news_year.get().strip()
        image = self.new_news_image.get().strip()
        link_label = self.new_news_link_label.get().strip()

        if not title or not intro or not url:
            messagebox.showerror("Error", "Please enter a title, intro, and link URL.")
            return

        item_id = self.slugify(title) or f"news-{len(self.news_data) + 1}"
        if item_id in self.news_data:
            messagebox.showerror("Error", "A news item with this title already exists. Please use a different title.")
            return

        self.news_data[item_id] = self.normalize_news_item(item_id, {
            'id': item_id,
            'title': title,
            'intro': intro,
            'url': url,
            'source': source,
            'category': category,
            'year': year,
            'image': image,
            'linkLabel': link_label
        })

        self.sync_news_outputs()
        self.clear_news_form()
        self.news_select.set(f"{item_id}: {title}")
        self.populate_news_form(item_id)
        messagebox.showinfo("Success", f"Added '{title}' to News.")

    def update_news_item(self):
        """Update an existing news item"""
        if not self.current_news_id:
            messagebox.showerror("Error", "Please select a news item to update.")
            return

        title = self.edit_news_title.get().strip()
        intro = self.edit_news_intro.get('1.0', 'end-1c').strip()
        url = self.edit_news_url.get().strip()
        source = self.edit_news_source.get().strip()
        category = self.edit_news_category.get().strip()
        year = self.edit_news_year.get().strip()
        image = self.edit_news_image.get().strip()
        link_label = self.edit_news_link_label.get().strip()

        if not title or not intro or not url:
            messagebox.showerror("Error", "Please enter a title, intro, and link URL.")
            return

        new_item_id = self.slugify(title) or self.current_news_id
        if new_item_id != self.current_news_id and new_item_id in self.news_data:
            messagebox.showerror("Error", "Another news item already uses this title. Please choose a different title.")
            return

        updated_item = self.normalize_news_item(new_item_id, {
            'id': new_item_id,
            'title': title,
            'intro': intro,
            'url': url,
            'source': source,
            'category': category,
            'year': year,
            'image': image,
            'linkLabel': link_label
        })

        if new_item_id != self.current_news_id:
            items = list(self.news_data.items())
            rebuilt = {}
            for item_id, item in items:
                if item_id == self.current_news_id:
                    rebuilt[new_item_id] = updated_item
                else:
                    rebuilt[item_id] = item
            self.news_data = rebuilt
            self.current_news_id = new_item_id
        else:
            self.news_data[self.current_news_id] = updated_item

        self.sync_news_outputs()
        self.news_select.set(f"{self.current_news_id}: {title}")
        self.populate_news_form(self.current_news_id)
        messagebox.showinfo("Success", f"Updated '{title}'.")

    def delete_news_item(self):
        """Delete a news item"""
        if not self.current_news_id:
            messagebox.showerror("Error", "Please select a news item to delete.")
            return

        item = self.news_data.get(self.current_news_id)
        if not item:
            messagebox.showerror("Error", "Selected news item could not be found.")
            return

        result = messagebox.askyesno(
            "Delete News Item",
            f"Delete '{item.get('title', '')}' from the News page?",
            icon='warning'
        )

        if not result:
            return

        deleted_title = item.get('title', self.current_news_id)
        del self.news_data[self.current_news_id]
        self.current_news_id = None
        self.news_select.set('')
        self.news_editing_label.config(text="No news item selected")
        self.edit_news_title.delete(0, tk.END)
        self.edit_news_intro.delete('1.0', tk.END)
        self.edit_news_url.delete(0, tk.END)
        self.edit_news_source.delete(0, tk.END)
        self.edit_news_category.delete(0, tk.END)
        self.edit_news_year.delete(0, tk.END)
        self.edit_news_image.delete(0, tk.END)
        self.edit_news_link_label.delete(0, tk.END)
        self.sync_news_outputs()
        messagebox.showinfo("Success", f"Deleted '{deleted_title}'.")

    def contact_fields(self):
        """Contact tab fields, keyed like read_contact_details"""
        return {
            'personal_email': self.personal_email,
            'business_email': self.business_email,
            'instagram_handle': self.instagram_handle,
            'second_instagram_handle': self.second_instagram_handle,
            'instagram_url': self.instagram_url,
            'facebook_url': self.facebook_url,
        }

    def load_contact_fields(self):
        """Fill the contact tab from contact.html"""
        try:
            details = read_contact_details(self.read_page(self.contact_html))
        except (OSError, ValueError) as e:
            messagebox.showwarning("Warning", f"Could not load contact details: {e}")
            return
        for key, field in self.contact_fields().items():
            field.delete(0, tk.END)
            field.insert(0, details[key])

    def update_contact(self):
        """Change contact details everywhere they appear; every page repeats them in its footer"""
        details = {key: field.get().strip() for key, field in self.contact_fields().items()}
        for key in ('instagram_handle', 'second_instagram_handle'):
            if details[key] and not details[key].startswith('@'):
                details[key] = '@' + details[key]

        problem = contact_problem(details)
        if problem:
            messagebox.showerror("Error", f"{problem} Nothing was changed.")
            return

        try:
            replacements = contact_replacements(read_contact_details(self.read_page(self.contact_html)),
                                                details)
            if not replacements:
                messagebox.showinfo("No Changes", "The contact details already match the website.")
                return

            # Work out every page before writing any, so a read error can't leave them mixed
            changed = {}
            for path in sorted(self.project_dir.glob('*.html')):
                page = self.read_page(path)
                new_page = apply_replacements(page, replacements)
                if new_page != page:
                    changed[path] = new_page
            for path, new_page in changed.items():
                self.write_page(path, new_page)
        except (OSError, ValueError) as e:
            messagebox.showerror("Error", f"Failed to update contact details: {e}")
            return

        self.load_contact_fields()
        messagebox.showinfo("Success", f"Updated contact details on {len(changed)} pages.")

    def available_editing_text(self):
        """Editing label; the dropdown is alphabetical, so this is where page order shows"""
        work = self.available_data[self.current_available_id]
        position = list(self.available_data).index(self.current_available_id) + 1
        return (f"Currently editing: {work.get('title', self.current_available_id)} "
                f"(position {position} of {len(self.available_data)} on the page)")

    def move_available_work(self, step):
        """Move the selected work on the Available page"""
        if not self.current_available_id:
            messagebox.showerror("Error", "Please select a work to move.")
            return
        self.available_data = move_entry(self.available_data, self.current_available_id, step)
        self.sync_available_outputs()
        self.available_editing_label.config(text=self.available_editing_text())

    def create_available_work(self):
        """Create new available work"""
        title = self.new_work_title.get().strip()
        price = self.new_work_price.get().strip()
        size = self.new_work_size.get().strip()
        description = self.new_work_description.get('1.0', 'end-1c').strip()
        status = self.new_work_status.get().strip() or "Available"

        if not title:
            messagebox.showerror("Error", "Please enter a title for the available work.")
            return

        work_id = self.slugify(title)
        if work_id in self.available_data:
            messagebox.showerror("Error", "A work with this title already exists. Please use a different title.")
            return

        folder_name, folder_path = self.ensure_available_folder(title)

        try:
            if self.new_available_image_paths:
                images = self.copy_available_images_to_folder(self.new_available_image_paths, folder_path)
            else:
                images = self.get_available_image_names(folder_path)

            if not images:
                messagebox.showerror(
                    "Error",
                    "Please select images, or place images in the artwork folder before creating the entry."
                )
                return

            new_work = {
                'id': work_id,
                'title': title,
                'price': price,
                'size': size,
                'description': description,
                'status': status,
                'folder': folder_name,
                'images': images
            }
            # Newest work first on the Available page
            self.available_data = {work_id: new_work, **self.available_data}

            self.sync_available_outputs()

            messagebox.showinfo(
                "Success",
                f"Added '{title}' to Available Work.\n\n"
                f"Folder: images/available/{folder_name}\n"
                f"Images: {len(images)}"
            )

            self.new_work_title.delete(0, tk.END)
            self.new_work_price.delete(0, tk.END)
            self.new_work_size.delete(0, tk.END)
            self.new_work_description.delete('1.0', tk.END)
            self.new_work_status.set("Available")
            self.clear_available_images_new()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create available work: {e}")

    def update_available_work(self):
        """Update existing available work"""
        if not self.current_available_id:
            messagebox.showerror("Error", "Please select a work to update.")
            return

        title = self.edit_work_title.get().strip()
        price = self.edit_work_price.get().strip()
        size = self.edit_work_size.get().strip()
        description = self.edit_work_description.get('1.0', 'end-1c').strip()
        status = self.edit_work_status.get().strip() or "Available"

        if not title:
            messagebox.showerror("Error", "Please enter a title for the available work.")
            return

        work = self.available_data.get(self.current_available_id)
        if not work:
            messagebox.showerror("Error", "Selected work could not be found.")
            return

        new_work_id = self.slugify(title)
        if new_work_id != self.current_available_id and new_work_id in self.available_data:
            messagebox.showerror("Error", "Another available work already uses this title. Please choose a different title.")
            return

        old_folder_name = work.get('folder', self.make_available_folder_name(work.get('title', title)))

        try:
            new_folder_name, new_folder_path = self.ensure_available_folder(title, old_folder_name)

            if self.edit_available_image_paths:
                images = self.copy_available_images_to_folder(self.edit_available_image_paths, new_folder_path)
            else:
                images = self.get_available_image_names(new_folder_path)

            if not images:
                messagebox.showerror("Error", "This available work must have at least one image.")
                return

            if new_work_id != self.current_available_id:
                self.available_data = {
                    (new_work_id if key == self.current_available_id else key): value
                    for key, value in self.available_data.items()
                }
                self.current_available_id = new_work_id
                work = self.available_data[self.current_available_id]

            work.update({
                'id': self.current_available_id,
                'title': title,
                'price': price,
                'size': size,
                'description': description,
                'status': status,
                'folder': new_folder_name,
                'images': images
            })

            self.sync_available_outputs()

            self.available_select.set(f"{self.current_available_id}: {title}")
            self.edit_work_folder_label.config(text=f"images/available/{new_folder_name}")
            self.edit_available_image_paths = []
            self.refresh_existing_available_images(images)

            messagebox.showinfo("Success", f"Updated '{title}'.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update available work: {e}")

    def delete_available_work(self):
        """Delete available work"""
        if not self.current_available_id:
            messagebox.showerror("Error", "Please select a work to delete.")
            return

        work = self.available_data.get(self.current_available_id)
        if not work:
            messagebox.showerror("Error", "Selected work could not be found.")
            return

        result = messagebox.askyesno(
            "Delete Available Work",
            f"Delete '{work.get('title', '')}' from the available page?\n\n"
            "This will also remove the artwork's image folder.",
            icon='warning'
        )

        if not result:
            return

        try:
            _, folder_path = self.ensure_available_folder(work.get('title', ''), work.get('folder', ''), create_if_missing=False)
            if folder_path.exists():
                shutil.rmtree(folder_path)

            del self.available_data[self.current_available_id]
            self.sync_available_outputs()

            self.available_select.set('')
            self.current_available_id = None
            self.edit_work_title.delete(0, tk.END)
            self.edit_work_price.delete(0, tk.END)
            self.edit_work_size.delete(0, tk.END)
            self.edit_work_status.set('')
            self.edit_work_description.delete('1.0', tk.END)
            self.edit_work_folder_label.config(text="No work selected")
            self.refresh_existing_available_images([])

            messagebox.showinfo("Success", "Available work deleted.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete available work: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RachaelContentManager(root)
    root.mainloop()
