// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle navigation active states
    const navLinks = document.querySelectorAll('nav a');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    navLinks.forEach(link => {
        link.classList.remove('active');
        const linkHref = link.getAttribute('href');

        if (linkHref === currentPage ||
            (currentPage === '' && linkHref === 'index.html') ||
            (currentPage === 'index.html' && linkHref === 'index.html')) {
            link.classList.add('active');
        }
    });

    // Handle work item clicks
    const workItems = document.querySelectorAll('.work-item');

    workItems.forEach(item => {
        item.addEventListener('click', function() {
            const projectId = this.getAttribute('data-project');
            if (projectId) {
                // Navigate to individual project page
                window.location.href = `project.html?id=${projectId}`;
            }
        });
    });

    // Handle project page loading
    if (window.location.pathname.includes('project.html')) {
        loadProjectContent();
    }

    // Load grid background images
    loadGridBackgroundImages();
});

// Project content loader
function loadProjectContent() {
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('id');

    if (!projectId) {
        window.location.href = 'index.html';
        return;
    }

    // Project data - Update these with real project information
    const projectData = {
        project1: {
            title: "ReConstructed ReFuse: Air, Sea and Landscapes",
            subtitle: "2024/25, Mosaic & Kiln-worked Glass Installation, Public Art Commission",
            description: "ReConstructed ReFuse: Air, Sea & Landscapes was created for the Municipality of Anchorage Public Art Program in 2024/25. This immersive installation consists of eight large mosaics, a suspended herring net and three mobiles, created almost entirely of waste glass, mainly kiln fired recycled bottles and old windows.\n\nThe first four mosaics, overhead as you enter the building, depict seascapes filled with to-size king and sockeye salmon, herring and jellyfish, all created from window glass reformed in a kiln. Walking up the entry stairwell, there is a net filled with glass herring on the left reflecting in the sun. At the landing, the mosaics continue and move up the stairwell, into a creek and landscape scene with spawning salmon, birds, and other signs of wildlife.\n\nThe pebble tesserae in the creek scene are made of crushed bottle glass; the leaves, wildlife and other objects, of fused bottle and sheet glass, mixed with reclaimed tile tesserae. With the exception of a few art glass details, the mosaic tesserae is entirely reclaimed, reused and waste glass transformed in the kiln. The final piece of this installation are the mobiles hanging overhead in the entrance. Flying glass herring and small murrelet-type birds made of embellished and fused sheet glass float above with shimmering wings of reused window screen.",
            folder: "project1"
        },
        project2: {
            title: "Pilchuck Glass School Studies",
            subtitle: "2022-2023, Glass Casting & Architectural Application, Various Dimensions",
            description: "In 2022 I attended Pilchuck Glass Studio studying glass casting with architectural application taught by Hank Murta Adams. It changed my glass trajectory. I continued the second session, Monumental in 2023, which truly was — being so lucky as to study with both Hank and Isabel de Obaldia. These are examples of some of the works I created during my time there.",
            folder: "project2"
        },
        project3: {
            title: "Chandeliers",
            subtitle: "2021-2023, Kiln Fused Glass & Found Objects, Various Dimensions",
            description: "Created as commissioned pieces, these chandeliers combine kiln fused glass, kiln cast glass, found metal and lighting elements. The P & R Chandelier spans three floors, supported by an anchor chain, with each level containing a lighting element. The top floor features cast glass paint brushes suspended from a reclaimed shrimp pot, with rebar ties and kiln fused glass pendants in netting patterns.\n\nThe Alaska Robotics Chandelier was created for Alaska Robotics Gallery, featuring glass pendants using multiple kilned glass techniques and reclaimed found objects. Comic book inspired glass panels are embellished with drawings by Pat Race and kiln fused with copper inclusions. The center contains glass pencils constructed using non-traditional pate-de-verre technique, all suspended from a reused shrimp pot frame.",
            folder: "project3"
        },
        project4: {
            title: "Salmon Stocks",
            subtitle: "2021, Kiln Formed Glass Panels, Public Art Commission",
            description: "Salmon Stocks is a series of kiln formed solid art glass panels and free swimming fish representing Alaska King Salmon returns since 1972. Created for the Alaska Permanent Fund Corporation in Juneau, this 1% for Art project features full size salmon overlaid on an intricately styled water and graph background with all five of Alaska's species represented: Chinook, Sockeye, Pink, Silver & Chum in both their spawning and bright phases.",
            folder: "project4"
        },
        project5: {
            title: "Herring Catch",
            subtitle: "2021, Glass Installation, Public Art Commission",
            description: "Herring Catch is a 1% for Art project installed at Juneau International Airport. This installation features hundreds of fused glass herring suspended in a net, creating an immersive overhead display that captures the essence of Alaska's fishing heritage and marine environment.",
            folder: "project5"
        },
        project6: {
            title: "Hidden Art / Hidden Message",
            subtitle: "2020, Mosaic Scavenger Hunt, CARES ArtWorks Grant",
            description: "These public art works —funded by CBJ's Covid-19 CARES grant ArtWorks program— are my response to a request for pandemic artwork. I wanted to create art which was accessible to all and contained an element of fun so created a scavenger hunt with a series of artworks. When you locate them all and put them in order they spell an uplifting sentence.\n\nEach individual mosaic utilizes kilned art glass, repurposed scrap tile, glass and found object tesserae and are mounted on concrete board.\n\nThe tool series is installed throughout the Last Chance Mining Museum in Juneau, Alaska.\n\nThe flora & fauna series has been permanently installed in Capitol Park downtown Juneau, Alaska.",
            folder: "project6"
        },
        project7: {
            title: "Trending Towards Tapestry / a Changing Epoch",
            subtitle: "2022, IGCA Exhibit, Mixed Media",
            description: "Trending Towards Tapestry / A Changing Epoch is an exhibit of my explorations in glass, mosaic and plastics. With my all-encompassing philosophy of creative reuse and working with processes having a high degree of experimentation, my art is reflective of the intense beauty found in the natural world and my surroundings of Southeast Alaska, while acknowledging and illuminating the societal problems of waste, industrial and plastic pollution and climate change.\n\nThis past year I have been trying to incorporate plastics into my glass work. As my artistic mentality revolves around the reworking of waste materials, I realized I needed to acknowledge the abundance of plastics in our environment. After many trials, I developed a way to spin twine from single-use plastic bags, creating a visually appealing material, and started using it in my work, creating nets and \"weaving\" with the twine.\n\nI find beauty and inspiration in natural patterns. I explore these patterns using glass as my medium. Glass, as a material, is illuminating and reflecting, transparent and opaque, utilitarian and fanciful.",
            folder: "project7"
        },
        project8: {
            title: "Trending Towards Tapestry / Herring",
            subtitle: "2022, APU Galleries Exhibit, Glass & Plastic Installation",
            description: "My art is reflective of the intense beauty found in the natural world of my surroundings in Southeast Alaska, while acknowledging and reflecting on the societal problems of waste, industrial and plastic pollution. I want to shed light on the issues of throw away society, wastefulness and destructive industrialization, by creating works of art which illuminate these issues and cause one to view these problems in a new light.\n\nThis exhibit – Trending Towards Tapestry / with Herring is created of single use plastic bags hand spun into plastic twine and woven into nets in which glass herring are caught. Each individual herring is made from multiple layers of cut and embellished scrap window glass which is kiln fired into its final form. The herring laden nets are strung between mosaic strips of reclaimed tile, mirror and beach rust and are suspended from reclaimed fishing line.\n\nThe flying glass herring and hooligan are outfitted with plastic wings made from clamshells from grocery store greens and are mounted in front of my \"H2O quilt\" paintings created in both oil on board and kilned art glass mounted on board.",
            folder: "project8"
        },
        project9: {
            title: "Trending Towards Tapestry / Recent Works",
            subtitle: "2022, Haines Brewery Exhibit, Experimental Glass",
            description: "Trending Towards Tapestry is the overarching theme I have been working under the past year. A theme helps give me focus amongst my various artistic trajectories and tries to stitch the pieces together.\n\nGlass Water Blocks – w. Herring & Hooligan: I've been developing some interesting and experimental techniques utilizing metal powders between stacked and kiln fired reclaimed waste sheet glass. The patterns created from the heat, chemical reactions and flow of the glass, become what I've been calling \"glass water blocks.\" In a second firing I have been embellishing these H2O blocks with glass hooligan and herring, each fish cut, printed, layered and embellished with copper wire inclusions.\n\nH2O quilts – Boca Water Swatches: After working as a studio assistant at Casa de los Artistas for plein air artists, I realized I can paint my own thing, \"the essence of water\" — embellished with the small pieces of plastic which came to me at the shore of la playa.",
            folder: "project9"
        },
        project10: {
            title: "Glacier Studies",
            subtitle: "2024, Kiln-worked Glass Studies, Various Dimensions",
            description: "Glacier Studies is an ongoing exploration of glacial landscapes and ice formations through kiln-worked glass. This series captures the translucent blues, crystalline structures, and flowing forms found in Alaska's glaciers, using various glass techniques to recreate the luminous quality of ancient ice.",
            folder: "project10"
        },
        project11: {
            title: "ReConstructed ReFuse IV – Sheldon Museum exhibit",
            subtitle: "2024, Mixed Media Installation, Sheldon Museum",
            description: "ReConstructed ReFuse IV is an installation exhibited at the Sheldon Museum that continues the artist's exploration of waste materials and environmental consciousness. This iteration of the ReConstructed ReFuse series showcases innovative approaches to transforming discarded materials into compelling visual narratives about consumption and sustainability.",
            folder: "project11"
        },
        project12: {
            title: "ReConstructed ReFuse – Canvas exhibit",
            subtitle: "2024, Mixed Media Installation, Canvas Gallery",
            description: "ReConstructed ReFuse at Canvas Gallery presents a focused exhibition exploring themes of waste, reuse, and transformation. This body of work emphasizes the artist's commitment to environmental awareness through the creative repurposing of discarded materials, challenging viewers to reconsider the value and potential of what society discards.",
            folder: "project12"
        },
        project13: {
            title: "Tools",
            subtitle: "2024, Mixed Media Sculpture Series, Various Dimensions",
            description: "The Tools series celebrates the beauty and character of working implements through glass and mixed media. Each piece transforms everyday tools into sculptural forms, honoring the relationship between maker and implement, craft and labor. These works explore themes of utility, craftsmanship, and the dignity of physical work.",
            folder: "project13"
        },
        project14: {
            title: "Public Art",
            subtitle: "2020-2024, Various Public Art Commissions, Multiple Locations",
            description: "This collection showcases various public art commissions throughout Alaska, including installations at Anchorage, the Permanent Fund Corporation, Juneau International Airport, CARES ArtWorks projects, the Augustus Brown Pool, and the Juneau-Douglas City Museum. Each project responds to its unique site and community, bringing art glass and mosaic work into public spaces where they can be experienced by diverse audiences.",
            folder: "project14"
        },
        project15: {
            title: "Mosaics",
            subtitle: "2020-2024, Mosaic Works, Various Dimensions & Locations",
            description: "The Mosaics collection represents a diverse body of work utilizing traditional and innovative mosaic techniques. These pieces incorporate kiln-formed glass, reclaimed tiles, found objects, and recycled materials to create intricate compositions. Each mosaic reflects the artist's commitment to sustainability and creative reuse while exploring patterns found in nature and the built environment.",
            folder: "project15"
        }
    };

    const project = projectData[projectId];

    if (!project) {
        window.location.href = 'index.html';
        return;
    }

    // Update page content
    document.getElementById('project-title').textContent = project.title;
    document.getElementById('project-subtitle').textContent = project.subtitle;

    // Format description with proper paragraph breaks
    const descriptionElement = document.getElementById('project-description');
    const paragraphs = project.description.split('\n\n');
    descriptionElement.innerHTML = paragraphs.map(p => `<p>${p}</p>`).join('');

    // Load project images dynamically from folder
    loadProjectImages(project.folder, project.title);
}

// Function to automatically load images from project folder
function loadProjectImages(folderName, projectTitle) {
    const mainImageContainer = document.getElementById('project-main-image');
    const gallery = document.getElementById('project-gallery');

    mainImageContainer.innerHTML = '';
    gallery.innerHTML = '';

    // Common image file extensions to try
    const imageExtensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];

    // Main image names (for hero image)
    const mainImageNames = ['main', 'primary', 'hero'];

    // Additional image names (for gallery)
    const galleryImageNames = [
        'detail-1',
        'detail-2',
        'detail-3',
        'detail-4',
        'detail-5',
        'process-1',
        'process-2',
        'installation',
        'overview',
        'close-up',
        'macro',
        'environment',
        'context'
    ];

    let mainImageLoaded = false;
    let galleryImageCount = 0;
    const maxGalleryImages = 8;

    // Load main hero image
    mainImageNames.forEach(imageName => {
        if (mainImageLoaded) return;

        imageExtensions.forEach(ext => {
            if (mainImageLoaded) return;

            const imagePath = `images/${folderName}/${imageName}.${ext}`;

            const testImg = new Image();
            testImg.onload = function() {
                if (!mainImageLoaded) {
                    // Create main image
                    const img = document.createElement('img');
                    img.src = imagePath;
                    img.alt = `${projectTitle} - Main Image`;

                    // Add loading animation
                    img.style.opacity = '0';
                    img.onload = function() {
                        this.style.transition = 'opacity 0.5s ease';
                        this.style.opacity = '1';
                    };

                    mainImageContainer.appendChild(img);
                    mainImageLoaded = true;
                }
            };

            testImg.src = imagePath;
        });
    });

    // Load gallery images
    galleryImageNames.forEach(imageName => {
        if (galleryImageCount >= maxGalleryImages) return;

        imageExtensions.forEach(ext => {
            if (galleryImageCount >= maxGalleryImages) return;

            const imagePath = `images/${folderName}/${imageName}.${ext}`;

            const testImg = new Image();
            testImg.onload = function() {
                if (galleryImageCount < maxGalleryImages) {
                    // Create gallery image
                    const img = document.createElement('img');
                    img.src = imagePath;
                    img.alt = `${projectTitle} - ${imageName}`;
                    img.className = 'project-image';

                    // Add loading animation
                    img.style.opacity = '0';
                    img.onload = function() {
                        this.style.transition = 'opacity 0.3s ease';
                        this.style.opacity = '1';
                    };

                    gallery.appendChild(img);
                    galleryImageCount++;
                }
            };

            testImg.src = imagePath;
        });
    });

    // Show placeholders if no images found after a delay
    setTimeout(() => {
        if (!mainImageLoaded) {
            const placeholder = document.createElement('div');
            placeholder.className = 'main-image-placeholder';
            placeholder.innerHTML = `
                <p>Main project image will appear here</p>
                <p>Add: images/${folderName}/main.png</p>
            `;
            mainImageContainer.appendChild(placeholder);
        }

        if (gallery.children.length === 0) {
            const placeholder = document.createElement('div');
            placeholder.className = 'image-placeholder';
            placeholder.innerHTML = `
                <p>Additional project images will be added soon.</p>
                <p>Expected location: images/${folderName}/</p>
                <p>Supported formats: JPG, PNG, WebP, GIF</p>
            `;
            gallery.appendChild(placeholder);
        }
    }, 1000);
}

// Smooth scrolling for internal links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Add loading animation for work items
function animateWorkItems() {
    const workItems = document.querySelectorAll('.work-item');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    });

    workItems.forEach(item => {
        observer.observe(item);
    });
}

// Function to load background images for work grid items
function loadGridBackgroundImages() {
    const workItems = document.querySelectorAll('.work-item');
    const imagePaths = [
        'main.png', 'main.jpg', 'main.JPG', 'main.jpeg',
        'primary.png', 'primary.jpg', 'primary.jpeg',
        'hero.png', 'hero.jpg', 'hero.jpeg'
    ];

    workItems.forEach(item => {
        const projectId = item.getAttribute('data-project');
        if (!projectId) return;

        const projectFolder = projectId;
        const imageContainer = item.querySelector('.work-item-image');
        if (!imageContainer) return;

        let imageLoaded = false;
        let pathIndex = 0;

        function tryNextImage() {
            if (imageLoaded || pathIndex >= imagePaths.length) {
                if (!imageLoaded) {
                    // Show placeholder
                    imageContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
                    imageContainer.style.border = '2px dashed rgba(0, 0, 0, 0.3)';
                    imageContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: rgba(0, 0, 0, 0.5); font-size: 0.9rem;">Image Coming Soon</div>';
                }
                return;
            }

            const imagePath = `images/${projectFolder}/${imagePaths[pathIndex]}`;
            const testImg = new Image();

            testImg.onload = function() {
                if (!imageLoaded) {
                    imageContainer.style.backgroundImage = `url('${imagePath}')`;
                    imageContainer.style.backgroundSize = 'cover';
                    imageContainer.style.backgroundPosition = 'center';
                    imageContainer.style.backgroundRepeat = 'no-repeat';
                    imageLoaded = true;
                }
            };

            testImg.onerror = function() {
                pathIndex++;
                tryNextImage();
            };

            testImg.src = imagePath;
        }

        tryNextImage();
    });
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', animateWorkItems);