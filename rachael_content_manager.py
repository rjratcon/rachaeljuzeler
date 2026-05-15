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
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

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
        self.updates_html = self.project_dir / "updates.html"
        self.available_html = self.project_dir / "available.html"
        self.available_detail_html = self.project_dir / "available-piece.html"
        self.project_html = self.project_dir / "project.html"
        self.script_js = self.project_dir / "script.js"
        self.available_data_js = self.project_dir / "available-data.js"
        self.sitemap_xml = self.project_dir / "sitemap.xml"

        # Data storage
        self.data_dir = self.project_dir / "admin_data"
        self.data_dir.mkdir(exist_ok=True)
        self.projects_data_file = self.data_dir / "projects.json"
        self.cv_data_file = self.data_dir / "cv_sections.json"
        self.updates_data_file = self.data_dir / "updates.json"
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
        self.current_available_id = None
        self.edit_image_paths = []
        self.new_image_paths = []
        self.edit_available_image_paths = []
        self.new_available_image_paths = []

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

        # Create tabs
        self.create_projects_tab(notebook)
        self.create_cv_tab(notebook)
        self.create_updates_tab(notebook)
        self.create_contact_tab(notebook)
        self.create_available_tab(notebook)

    def create_projects_tab(self, notebook):
        """Create projects management tab with scrolling"""
        # Main frame
        main_frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(main_frame, text='WORK/PROJECTS')

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg='#786E00', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#786E00')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Now use scrollable_frame as the parent for all content
        frame = scrollable_frame

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
                                          font=('EB Garamond', 10))
        self.project_select.pack(pady=5, padx=10)
        self.project_select.bind('<<ComboboxSelected>>', self.on_project_selected)

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

        tk.Label(existing_frame, text="Description:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_project_description = scrolledtext.ScrolledText(existing_frame, width=60, height=4,
                                                                 font=('EB Garamond', 10),
                                                                 bg='#786E00', fg='#000000',
                                                                 insertbackground='#000000')
        self.edit_project_description.pack(pady=5, padx=10)

        # Image management for existing projects
        img_frame = tk.Frame(existing_frame, bg='#786E00')
        img_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(img_frame, text="Add/Replace Images:",
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

    def create_cv_tab(self, notebook):
        """Create CV management tab with scrolling"""
        # Main frame
        main_frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(main_frame, text='ABOUT/CV')

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg='#786E00', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#786E00')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Now use scrollable_frame as the parent for all content
        frame = scrollable_frame

        # Title
        tk.Label(frame, text="Manage Your CV & About Content",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        # Bio section
        bio_frame = tk.LabelFrame(frame, text="Edit Biography",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        bio_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(bio_frame, text="About/Bio Text:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.bio_text = scrolledtext.ScrolledText(bio_frame, width=60, height=8,
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
                                             values=[
                                                 "Awards & Grants",
                                                 "Public Works",
                                                 "Museum Collections",
                                                 "Selected Solo Exhibitions",
                                                 "Selected Juried Shows & Group Exhibitions",
                                                 "Selected Education & Training",
                                                 "Board & Volunteer Positions",
                                                 "Employment History"
                                             ])
        self.cv_section_select.pack(pady=5, padx=10)
        self.cv_section_select.bind('<<ComboboxSelected>>', self.on_cv_section_selected)

        tk.Label(cv_frame, text="Section Content (one item per line):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.cv_content = scrolledtext.ScrolledText(cv_frame, width=60, height=6,
                                                   font=('EB Garamond', 10),
                                                   bg='#786E00', fg='#000000',
                                                   insertbackground='#000000')
        self.cv_content.pack(pady=5, padx=10)

        tk.Button(cv_frame, text="Update CV Section",
                 command=self.update_cv_section,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(pady=10)

    def create_updates_tab(self, notebook):
        """Create updates management tab"""
        frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(frame, text='UPDATES')

        # Title
        tk.Label(frame, text="Manage Updates",
                font=('EB Garamond', 16, 'bold'),
                bg='#786E00', fg='#000000').pack(pady=10)

        # Edit existing updates
        edit_frame = tk.LabelFrame(frame, text="Edit Existing Update",
                                  bg='#786E00', fg='#000000',
                                  font=('EB Garamond', 12, 'bold'))
        edit_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(edit_frame, text="Select Update:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.update_select = ttk.Combobox(edit_frame, width=60,
                                         font=('EB Garamond', 10))
        self.update_select.pack(pady=5, padx=10)
        self.update_select.bind('<<ComboboxSelected>>', self.on_update_selected)

        tk.Label(edit_frame, text="Update Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_update_title = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                         bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_update_title.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Content:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_update_content = scrolledtext.ScrolledText(edit_frame, width=60, height=4,
                                                            font=('EB Garamond', 10),
                                                            bg='#786E00', fg='#000000',
                                                            insertbackground='#000000')
        self.edit_update_content.pack(pady=5, padx=10)

        tk.Label(edit_frame, text="Link (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.edit_update_link = tk.Entry(edit_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.edit_update_link.pack(pady=5, padx=10)

        # Update buttons
        edit_btn_frame = tk.Frame(edit_frame, bg='#786E00')
        edit_btn_frame.pack(pady=10)

        tk.Button(edit_btn_frame, text="Update",
                 command=self.update_update,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        tk.Button(edit_btn_frame, text="Delete",
                 command=self.delete_update,
                 bg='#8B0000', fg='#FFFFFF',  # Dark red
                 font=('EB Garamond', 11, 'bold')).pack(side='left', padx=5)

        # Add new update
        new_frame = tk.LabelFrame(frame, text="Add New Update",
                                 bg='#786E00', fg='#000000',
                                 font=('EB Garamond', 12, 'bold'))
        new_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(new_frame, text="Update Title:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_update_title = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_update_title.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Content:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_update_content = scrolledtext.ScrolledText(new_frame, width=60, height=4,
                                                           font=('EB Garamond', 10),
                                                           bg='#786E00', fg='#000000',
                                                           insertbackground='#000000')
        self.new_update_content.pack(pady=5, padx=10)

        tk.Label(new_frame, text="Link (optional):",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').pack(anchor='w', padx=10, pady=(10,0))
        self.new_update_link = tk.Entry(new_frame, width=60, font=('EB Garamond', 10),
                                       bg='#786E00', fg='#000000', insertbackground='#000000')
        self.new_update_link.pack(pady=5, padx=10)

        tk.Button(new_frame, text="Add Update",
                 command=self.create_update,
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
        self.personal_email = tk.Entry(email_frame, width=30, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.personal_email.grid(row=0, column=1, padx=10)

        tk.Label(email_frame, text="Business Email:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=1, column=0, sticky='w', pady=5)
        self.business_email = tk.Entry(email_frame, width=30, font=('EB Garamond', 10),
                                      bg='#786E00', fg='#000000', insertbackground='#000000')
        self.business_email.grid(row=1, column=1, padx=10)

        # Social media
        tk.Label(email_frame, text="Instagram Handle:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=2, column=0, sticky='w', pady=5)
        self.instagram_handle = tk.Entry(email_frame, width=30, font=('EB Garamond', 10),
                                        bg='#786E00', fg='#000000', insertbackground='#000000')
        self.instagram_handle.grid(row=2, column=1, padx=10)

        tk.Label(email_frame, text="Instagram URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=3, column=0, sticky='w', pady=5)
        self.instagram_url = tk.Entry(email_frame, width=30, font=('EB Garamond', 10),
                                     bg='#786E00', fg='#000000', insertbackground='#000000')
        self.instagram_url.grid(row=3, column=1, padx=10)

        tk.Label(email_frame, text="Facebook URL:",
                font=('EB Garamond', 10, 'bold'),
                bg='#786E00', fg='#000000').grid(row=4, column=0, sticky='w', pady=5)
        self.facebook_url = tk.Entry(email_frame, width=30, font=('EB Garamond', 10),
                                    bg='#786E00', fg='#000000', insertbackground='#000000')
        self.facebook_url.grid(row=4, column=1, padx=10)

        tk.Button(contact_frame, text="Update Contact Info",
                 command=self.update_contact,
                 bg='#000000', fg='#786E00',
                 font=('EB Garamond', 12, 'bold')).pack(pady=20)

    def create_available_tab(self, notebook):
        """Create available works management tab with scrolling"""
        # Main frame
        main_frame = tk.Frame(notebook, bg='#786E00')
        notebook.add(main_frame, text='AVAILABLE')

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg='#786E00', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#786E00')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Now use scrollable_frame as the parent for all content
        frame = scrollable_frame

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
                                            font=('EB Garamond', 10))
        self.available_select.pack(pady=5, padx=10)
        self.available_select.bind('<<ComboboxSelected>>', self.on_available_selected)

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

    def browse_project_images_edit(self):
        """Browse for multiple images for editing project"""
        filenames = filedialog.askopenfilenames(
            title="Select Project Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if filenames:
            self.edit_image_paths = list(filenames)
            messagebox.showinfo("Images Selected", f"Selected {len(filenames)} images")

    def browse_project_images_new(self):
        """Browse for multiple images for new project"""
        filenames = filedialog.askopenfilenames(
            title="Select Project Images (First image will be the main grid image)",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
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
        filenames = filedialog.askopenfilenames(
            title="Select Available Work Images (first image will be used as the main image)",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
        if filenames:
            for filename in filenames:
                if filename not in self.new_available_image_paths:
                    self.new_available_image_paths.append(filename)
            self.refresh_selected_available_images(self.new_available_image_list, self.new_available_image_paths)

    def browse_available_images_edit(self):
        """Browse for multiple images to replace an existing available work image set"""
        filenames = filedialog.askopenfilenames(
            title="Select Replacement Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("All files", "*.*")
            ]
        )
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

    def get_available_image_names(self, folder_path):
        """Return available work images in display order"""
        if not folder_path.exists():
            return []

        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        image_files = [path.name for path in folder_path.iterdir() if path.is_file() and path.suffix.lower() in supported_exts]

        def image_sort_key(name):
            lower = name.lower()
            if 'main' in lower:
                return (0, lower)
            if 'detail' in lower:
                return (2, lower)
            return (1, lower)

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

        scanned_data = self.scan_available_folders()

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
            self.available_data[work_id] = merged

        # Refresh image lists for entries whose folders already exist
        for work_id, work in list(self.available_data.items()):
            folder_name = work.get('folder', '')
            if not folder_name:
                folder_name = self.make_available_folder_name(work.get('title', ''))
                work['folder'] = folder_name

            folder_path = self.available_base_dir / folder_name
            if folder_path.exists():
                work['images'] = self.get_available_image_names(folder_path)

        self.save_available_data()

    def save_available_data(self):
        """Persist available work data to JSON"""
        ordered_data = dict(sorted(self.available_data.items(), key=lambda item: item[1].get('title', '').lower()))
        with open(self.available_data_file, 'w', encoding='utf-8') as f:
            json.dump(ordered_data, f, indent=2, ensure_ascii=False)

    def refresh_available_dropdown(self):
        """Refresh the combobox choices for available works"""
        work_names = [f"{work_id}: {data['title']}" for work_id, data in sorted(self.available_data.items(), key=lambda item: item[1].get('title', '').lower())]
        self.available_select['values'] = work_names

    def refresh_existing_available_images(self, image_names):
        """Show the images currently assigned to an available work"""
        self.edit_available_image_list.delete(0, tk.END)
        for image_name in image_names:
            self.edit_available_image_list.insert(tk.END, image_name)

    def copy_available_images_to_folder(self, image_paths, folder_path):
        """Copy selected available work images into the target folder using website-friendly names"""
        supported_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        folder_path.mkdir(parents=True, exist_ok=True)

        for existing in folder_path.iterdir():
            if existing.is_file() and existing.suffix.lower() in supported_exts:
                existing.unlink()

        saved_names = []
        for index, image_path in enumerate(image_paths):
            source = Path(image_path)
            extension = source.suffix.lower()
            filename = f"main{extension}" if index == 0 else f"detail-{index}{extension}"
            destination = folder_path / filename
            shutil.copy2(source, destination)
            saved_names.append(filename)

        return saved_names

    def generate_available_data_js(self):
        """Generate the frontend data file used by the available pages"""
        works = []
        for work_id, work in sorted(self.available_data.items(), key=lambda item: item[1].get('title', '').lower()):
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

        url_lines = []
        for url in base_urls + project_urls + available_urls:
            url_lines.append("  <url>")
            url_lines.append(f"    <loc>{url}</loc>")
            url_lines.append("  </url>")

        sitemap_content = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        sitemap_content += "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        sitemap_content += "\n".join(url_lines)
        sitemap_content += "\n</urlset>\n"

        with open(self.sitemap_xml, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)

    def copy_image(self, source_path, dest_name):
        """Copy image to project directory with new name"""
        if not source_path or not os.path.exists(source_path):
            return None

        source = Path(source_path)
        extension = source.suffix.lower()
        dest_path = self.projects_base_dir / f"{dest_name}{extension}"

        try:
            shutil.copy2(source_path, dest_path)
            return dest_path.name
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image: {e}")
            return None

    def load_data(self):
        """Load existing data from script.js and JSON files"""
        # Load existing projects from script.js
        self.load_projects_from_script()

        # Load JSON data if exists
        if self.projects_data_file.exists():
            with open(self.projects_data_file, 'r') as f:
                stored_data = json.load(f)
                # Merge with script.js data
                self.projects_data.update(stored_data)

        # Update project dropdown with real project names
        project_names = [f"{pid}: {data['title']}" for pid, data in self.projects_data.items()]
        self.project_select['values'] = project_names

        # Load available works data and refresh related files
        self.load_available_data()
        self.refresh_available_dropdown()
        self.generate_available_data_js()
        self.regenerate_sitemap()

    def load_projects_from_script(self):
        """Extract project data from script.js file"""
        try:
            if not self.script_js.exists():
                self.projects_data = {}
                return

            with open(self.script_js, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Extract projectData object using regex
            pattern = r'const projectData = \{(.*?)\};'
            match = re.search(pattern, script_content, re.DOTALL)

            if not match:
                self.projects_data = {}
                return

            # Parse the project data (simplified parsing)
            project_section = match.group(1)

            # Extract individual projects
            project_pattern = r'(project\d+):\s*\{([^}]+)\}'
            projects = re.findall(project_pattern, project_section, re.DOTALL)

            self.projects_data = {}
            for project_id, project_content in projects:
                # Extract title, subtitle, description
                title_match = re.search(r'title:\s*["\']([^"\']+)["\']', project_content)
                subtitle_match = re.search(r'subtitle:\s*["\']([^"\']+)["\']', project_content)
                desc_match = re.search(r'description:\s*["\']([^"\']+)["\']', project_content)
                folder_match = re.search(r'folder:\s*["\']([^"\']+)["\']', project_content)

                self.projects_data[project_id] = {
                    'title': title_match.group(1) if title_match else '',
                    'subtitle': subtitle_match.group(1) if subtitle_match else '',
                    'description': desc_match.group(1) if desc_match else '',
                    'folder': folder_match.group(1) if folder_match else project_id
                }

        except Exception as e:
            print(f"Error loading projects from script.js: {e}")
            self.projects_data = {}

    def save_projects_data(self):
        """Save projects data to JSON file"""
        with open(self.projects_data_file, 'w') as f:
            json.dump(self.projects_data, f, indent=2)

    def on_project_selected(self, event):
        """Handle project selection and populate form fields with existing data"""
        selection = self.project_select.get()
        if not selection:
            return

        project_id = selection.split(':')[0]
        if project_id in self.projects_data:
            project = self.projects_data[project_id]

            # Clear and populate title field
            self.edit_project_title.delete(0, tk.END)
            self.edit_project_title.insert(0, project.get('title', ''))

            # Clear and populate subtitle field
            self.edit_project_subtitle.delete(0, tk.END)
            self.edit_project_subtitle.insert(0, project.get('subtitle', ''))

            # Clear and populate description field
            self.edit_project_description.delete('1.0', tk.END)
            self.edit_project_description.insert('1.0', project.get('description', ''))

            # Store the current project ID for updates
            self.current_project_id = project_id

    def on_cv_section_selected(self, event):
        """Handle CV section selection"""
        # Placeholder - would load CV data
        pass

    def on_update_selected(self, event):
        """Handle update selection"""
        # Placeholder - would load update data
        pass

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

        self.edit_work_folder_label.config(text=f"images/available/{work.get('folder', '')}")
        self.edit_available_image_paths = []
        self.refresh_existing_available_images(work.get('images', []))

    # Placeholder methods for CRUD operations
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

        # Generate project ID
        project_id = f"project{len(self.projects_data) + 16}"  # Start from 16 since 1-15 exist
        project_folder = self.projects_base_dir / project_id
        project_folder.mkdir(exist_ok=True)

        # Copy images to project folder
        image_filenames = []
        if self.new_image_paths:
            for i, img_path in enumerate(self.new_image_paths):
                if os.path.exists(img_path):
                    # Get file extension
                    source = Path(img_path)
                    extension = source.suffix.lower()

                    # Create filename: project_id-1.jpg, project_id-2.jpg, etc.
                    new_filename = f"{project_id}-{i+1}{extension}"
                    dst_path = project_folder / new_filename

                    try:
                        # Copy image directly to project folder
                        shutil.copy2(img_path, dst_path)
                        image_filenames.append(new_filename)
                        print(f"Copied {img_path} to {dst_path}")
                    except Exception as e:
                        print(f"Failed to copy image {img_path}: {e}")
                        messagebox.showwarning("Warning", f"Failed to copy image {source.name}: {e}")

        print(f"Created project folder: {project_folder}")
        print(f"Copied {len(image_filenames)} images: {image_filenames}")

        # Save project data
        self.projects_data[project_id] = {
            'title': title,
            'subtitle': subtitle,
            'description': description,
            'folder': project_id,
            'images': image_filenames
        }

        self.save_projects_data()

        # Update HTML files (placeholder)
        # Would need to update script.js projectData object and index.html work grid

        messagebox.showinfo("Success",
                            f"Project '{title}' created successfully!\n\n"
                            f"Project ID: {project_id}\n"
                            f"Images copied: {len(image_filenames)}\n"
                            f"Folder created: images/{project_id}/")

        # Clear form
        self.new_project_title.delete(0, tk.END)
        self.new_project_subtitle.delete(0, tk.END)
        self.new_project_description.delete('1.0', tk.END)
        self.new_image_paths = []
        self.new_image_list.delete(0, tk.END)

        # Refresh dropdown
        project_names = [f"{pid}: {data['title']}" for pid, data in self.projects_data.items()]
        self.project_select['values'] = project_names

    def update_project(self):
        """Update existing project with new data"""
        if not hasattr(self, 'current_project_id') or not self.current_project_id:
            messagebox.showerror("Error", "Please select a project to update")
            return

        # Get updated values from form
        title = self.edit_project_title.get().strip()
        subtitle = self.edit_project_subtitle.get().strip()
        description = self.edit_project_description.get('1.0', 'end-1c').strip()

        if not title or not description:
            messagebox.showerror("Error", "Please fill in title and description")
            return

        try:
            # Update project data
            self.projects_data[self.current_project_id].update({
                'title': title,
                'subtitle': subtitle,
                'description': description
            })

            # Handle new images if any were selected
            if hasattr(self, 'edit_image_paths') and self.edit_image_paths:
                project_folder = self.projects_base_dir / self.current_project_id
                project_folder.mkdir(exist_ok=True)

                # Copy new images
                image_filenames = []
                for i, img_path in enumerate(self.edit_image_paths):
                    filename = self.copy_image(img_path, f"{self.current_project_id}-{i+1}")
                    if filename:
                        # Move to project folder
                        src = self.projects_base_dir / filename
                        dst = project_folder / filename
                        if src.exists():
                            shutil.move(src, dst)
                        image_filenames.append(filename)

                if image_filenames:
                    self.projects_data[self.current_project_id]['images'] = image_filenames

                # Clear selected images
                self.edit_image_paths = []

            # Save to JSON
            self.save_projects_data()

            # Update dropdown to reflect changes
            project_names = [f"{pid}: {data['title']}" for pid, data in self.projects_data.items()]
            self.project_select['values'] = project_names
            # Keep current selection
            self.project_select.set(f"{self.current_project_id}: {title}")

            messagebox.showinfo("Success", f"Project '{title}' updated successfully!")

            # TODO: Update script.js and HTML files with new data

        except Exception as e:
            messagebox.showerror("Error", f"Failed to update project: {e}")

    def delete_project(self):
        """Delete project with confirmation"""
        if not hasattr(self, 'current_project_id') or not self.current_project_id:
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
            f"This action cannot be undone and will remove all project data and images.",
            icon='warning'
        )

        if result:
            try:
                # Remove project data
                del self.projects_data[self.current_project_id]
                self.save_projects_data()

                # Clear the form
                self.edit_project_title.delete(0, tk.END)
                self.edit_project_subtitle.delete(0, tk.END)
                self.edit_project_description.delete('1.0', tk.END)

                # Update dropdown
                project_names = [f"{pid}: {data['title']}" for pid, data in self.projects_data.items()]
                self.project_select['values'] = project_names
                self.project_select.set('')

                # Reset current project
                self.current_project_id = None

                messagebox.showinfo("Success", f"Project '{project['title']}' has been deleted.")

                # TODO: Also remove from HTML files and delete project folder/images

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete project: {e}")

    def update_bio(self):
        """Update biography"""
        messagebox.showinfo("Info", "Update bio functionality would be implemented here")

    def update_cv_section(self):
        """Update CV section"""
        messagebox.showinfo("Info", "Update CV section functionality would be implemented here")

    def create_update(self):
        """Create new update"""
        messagebox.showinfo("Info", "Create update functionality would be implemented here")

    def update_update(self):
        """Update existing update"""
        messagebox.showinfo("Info", "Update update functionality would be implemented here")

    def delete_update(self):
        """Delete update"""
        messagebox.showinfo("Info", "Delete update functionality would be implemented here")

    def update_contact(self):
        """Update contact information"""
        messagebox.showinfo("Info", "Update contact functionality would be implemented here")

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

        folder_name = self.make_available_folder_name(title)
        folder_path = self.available_base_dir / folder_name

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

            self.available_data[work_id] = {
                'id': work_id,
                'title': title,
                'price': price,
                'size': size,
                'description': description,
                'status': status,
                'folder': folder_name,
                'images': images
            }

            self.save_available_data()
            self.generate_available_data_js()
            self.regenerate_sitemap()
            self.refresh_available_dropdown()

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

        old_folder_name = work.get('folder', self.make_available_folder_name(work.get('title', title)))
        new_folder_name = self.make_available_folder_name(title)
        old_folder_path = self.available_base_dir / old_folder_name
        new_folder_path = self.available_base_dir / new_folder_name

        try:
            if old_folder_name != new_folder_name and old_folder_path.exists() and not new_folder_path.exists():
                old_folder_path.rename(new_folder_path)
            elif old_folder_name == new_folder_name:
                new_folder_path = old_folder_path

            if self.edit_available_image_paths:
                images = self.copy_available_images_to_folder(self.edit_available_image_paths, new_folder_path)
            else:
                images = self.get_available_image_names(new_folder_path)

            work.update({
                'title': title,
                'price': price,
                'size': size,
                'description': description,
                'status': status,
                'folder': new_folder_name,
                'images': images
            })

            self.save_available_data()
            self.generate_available_data_js()
            self.regenerate_sitemap()
            self.refresh_available_dropdown()

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
            folder_path = self.available_base_dir / work.get('folder', '')
            if folder_path.exists():
                shutil.rmtree(folder_path)

            del self.available_data[self.current_available_id]
            self.save_available_data()
            self.generate_available_data_js()
            self.regenerate_sitemap()
            self.refresh_available_dropdown()

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
