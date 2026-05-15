const AVAILABLE_SITE_URL = 'https://rachaeljuzeler.com/';

function availableAbsoluteUrl(path) {
    return new URL(path, AVAILABLE_SITE_URL).toString();
}

function getAvailableWorks() {
    return Array.isArray(window.availableWorks) ? window.availableWorks : [];
}

function encodePathSegment(segment) {
    return encodeURIComponent(String(segment || '').trim());
}

function toTitleCase(value) {
    return String(value || '')
        .trim()
        .replace(/\w\S*/g, part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase());
}

function getAvailableFolderCandidates(work) {
    const rawValues = [
        work && work.folder,
        work && work.title,
        work && work.folder ? toTitleCase(work.folder) : '',
        work && work.title ? toTitleCase(work.title) : '',
        work && work.folder ? String(work.folder).toLowerCase() : '',
        work && work.title ? String(work.title).toLowerCase() : '',
        work && work.folder ? String(work.folder).replace(/\s+/g, '-') : '',
        work && work.title ? String(work.title).replace(/\s+/g, '-') : ''
    ];

    return rawValues
        .map(value => String(value || '').trim())
        .filter(Boolean)
        .filter((value, index, values) => values.indexOf(value) === index);
}

function getAvailableImagePath(folderName, imageName) {
    if (!folderName || !imageName) {
        return 'images/rjuzeler.jpg';
    }

    return `images/available/${encodePathSegment(folderName)}/${encodePathSegment(imageName)}`;
}

function getAvailableImageCandidates(work, imageName, index) {
    const folderCandidates = getAvailableFolderCandidates(work);
    const normalizedNames = [];
    const isPrimaryImage = index === 0;

    if (isPrimaryImage) {
        normalizedNames.push('main.jpg', 'main.jpeg', 'main.png', 'main.webp');
    } else if (typeof index === 'number' && index > 0) {
        normalizedNames.push(
            `detail-${index}.jpg`,
            `detail-${index}.jpeg`,
            `detail-${index}.png`,
            `detail-${index}.webp`
        );
    }

    const imageCandidates = [imageName, ...normalizedNames]
        .map(value => String(value || '').trim())
        .filter(Boolean)
        .filter((value, candidateIndex, values) => values.indexOf(value) === candidateIndex);

    const paths = [];

    folderCandidates.forEach(folderName => {
        imageCandidates.forEach(fileName => {
            paths.push(getAvailableImagePath(folderName, fileName));
        });
    });

    return paths.length ? paths : ['images/rjuzeler.jpg'];
}

function setAvailableImageSource(imageElement, work, imageName, index) {
    const candidates = getAvailableImageCandidates(work, imageName, index);
    let candidateIndex = 0;

    function applyCandidate() {
        imageElement.src = candidates[candidateIndex];
    }

    imageElement.onerror = function() {
        candidateIndex += 1;
        if (candidateIndex < candidates.length) {
            applyCandidate();
            return;
        }

        imageElement.onerror = null;
        imageElement.src = 'images/rjuzeler.jpg';
    };

    applyCandidate();
}

function setAvailableMeta(selector, content) {
    const element = document.querySelector(selector);
    if (element && content) {
        element.setAttribute('content', content);
    }
}

function setAvailableCanonical(href) {
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical && href) {
        canonical.setAttribute('href', href);
    }
}

function renderAvailableListing() {
    const list = document.getElementById('available-list');
    const emptyState = document.getElementById('available-empty');
    if (!list) {
        return;
    }

    const works = getAvailableWorks().filter(work => work.status !== 'On Hold');

    if (works.length === 0) {
        emptyState.hidden = false;
        return;
    }

    emptyState.hidden = true;

    works.forEach(work => {
        const card = document.createElement('article');
        card.className = 'available-card';

        const link = document.createElement('a');
        link.className = 'available-card-link';
        link.href = `available-piece.html?id=${work.id}`;
        link.setAttribute('aria-label', `View available work: ${work.title}`);

        const imageWrap = document.createElement('div');
        imageWrap.className = 'available-card-image-wrap';

        const image = document.createElement('img');
        image.className = 'available-card-image';
        image.alt = work.title;
        image.loading = 'lazy';
        setAvailableImageSource(image, work, (work.images || [])[0], 0);
        imageWrap.appendChild(image);

        if (work.status && work.status !== 'Available') {
            const badge = document.createElement('span');
            badge.className = 'available-status-badge';
            badge.textContent = work.status;
            imageWrap.appendChild(badge);
        }

        const textWrap = document.createElement('div');
        textWrap.className = 'available-card-text';

        const title = document.createElement('h2');
        title.className = 'available-card-title';
        title.textContent = work.title;
        textWrap.appendChild(title);

        if (work.price) {
            const price = document.createElement('p');
            price.className = 'available-card-price';
            price.textContent = work.price;
            textWrap.appendChild(price);
        }

        link.appendChild(imageWrap);
        link.appendChild(textWrap);
        card.appendChild(link);
        list.appendChild(card);
    });
}

function renderAvailableDetail() {
    const detail = document.getElementById('available-piece-detail');
    if (!detail) {
        return;
    }

    const params = new URLSearchParams(window.location.search);
    const workId = params.get('id');
    const work = getAvailableWorks().find(item => item.id === workId);
    const missing = document.getElementById('available-piece-missing');

    if (!work) {
        missing.hidden = false;
        return;
    }

    missing.hidden = true;
    detail.hidden = false;

    const mainImage = document.getElementById('available-piece-main-image');
    const title = document.getElementById('available-piece-title');
    const price = document.getElementById('available-piece-price');
    const size = document.getElementById('available-piece-size');
    const description = document.getElementById('available-piece-description');
    const gallery = document.getElementById('available-piece-gallery');
    const status = document.getElementById('available-piece-status');

    title.textContent = work.title;
    mainImage.alt = work.title;
    setAvailableImageSource(mainImage, work, (work.images || [])[0], 0);
    price.textContent = work.price || 'Price available on request.';
    size.textContent = work.size || '';
    size.hidden = !work.size;

    description.innerHTML = '';
    const paragraphs = (work.description || 'More information coming soon.').split(/\n\s*\n/);
    paragraphs.forEach(text => {
        const paragraph = document.createElement('p');
        paragraph.textContent = text.trim();
        description.appendChild(paragraph);
    });

    status.textContent = work.status || 'Available';
    status.hidden = false;
    if (!work.status || work.status === 'Available') {
        status.classList.add('is-available');
    } else {
        status.classList.remove('is-available');
    }

    gallery.innerHTML = '';
    (work.images || []).forEach((imageName, index) => {
        if (index === 0) {
            return;
        }
        const thumb = document.createElement('img');
        thumb.className = 'available-piece-thumb';
        thumb.alt = `${work.title} detail ${index}`;
        thumb.loading = 'lazy';
        setAvailableImageSource(thumb, work, imageName, index);
        gallery.appendChild(thumb);
    });

    updateAvailableDetailSeo(work);
}

function updateAvailableDetailSeo(work) {
    const pageTitle = `${work.title} | Available Work | Rachael Juzeler`;
    const description = work.description ? work.description.split('\n')[0].trim() : `Available work by Rachael Juzeler: ${work.title}.`;
    const primaryImagePath = getAvailableImageCandidates(work, (work.images || [])[0], 0)[0] || 'images/rjuzeler.jpg';
    const imageUrl = availableAbsoluteUrl(primaryImagePath);
    const pageUrl = availableAbsoluteUrl(`available-piece.html?id=${work.id}`);

    document.title = pageTitle;
    setAvailableCanonical(pageUrl);
    setAvailableMeta('meta[name="description"]', description);
    setAvailableMeta('meta[property="og:title"]', pageTitle);
    setAvailableMeta('meta[property="og:description"]', description);
    setAvailableMeta('meta[property="og:url"]', pageUrl);
    setAvailableMeta('meta[property="og:image"]', imageUrl);
    setAvailableMeta('meta[name="twitter:title"]', pageTitle);
    setAvailableMeta('meta[name="twitter:description"]', description);
    setAvailableMeta('meta[name="twitter:image"]', imageUrl);

    const structuredData = document.getElementById('available-structured-data');
    if (structuredData) {
        const data = {
            '@context': 'https://schema.org',
            '@type': 'VisualArtwork',
            name: work.title,
            description,
            image: imageUrl,
            url: pageUrl,
            creator: {
                '@type': 'Person',
                name: 'Rachael Juzeler',
                url: availableAbsoluteUrl('')
            }
        };

        if (work.price) {
            data.offers = {
                '@type': 'Offer',
                availability: work.status === 'SOLD' ? 'https://schema.org/SoldOut' : 'https://schema.org/InStock',
                priceCurrency: 'USD',
                price: work.price
            };
        }

        structuredData.textContent = JSON.stringify(data);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    renderAvailableListing();
    renderAvailableDetail();
});
