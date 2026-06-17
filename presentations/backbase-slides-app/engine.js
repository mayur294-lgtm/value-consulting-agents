/* Backbase Slide Template Engine */

const BB_SHARED_ASSETS = window.BB_SHARED_ASSETS || '.';

/* ====================================================================
   BACKBASE SLIDE TEMPLATE ENGINE
   Complete: 17 Layout Families, All Variants
   ==================================================================== */

// ── SVG Constants ──

const BB_LOGO_DARK = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 142 24" fill="none" class="bb-logo"><g clip-path="url(#a)"><path fill="#041326" d="M3.457 7.552h3.457V.689H0v3.413h3.457v3.45Z"/><path fill="#041326" d="M14.193 11.909v-.545c3.384-.472 4.257-2.687 4.257-4.901 0-2.724-1.856-5.665-6.477-5.774H9.207v3.45h2.766c2.438.036 2.947 1.597 2.911 2.868-.073 2.796-1.347 2.869-3.494 2.905H3.457v13.797h8.26c5.569 0 7.425-3.159 7.425-6.427 0-2.832-.983-4.865-4.95-5.373Zm-2.366 8.315H6.951v-6.972h4.84c2.911 0 3.857.545 3.857 3.522.037 2.505-.91 3.413-3.82 3.45Zm10.007-2.142c0-2.94 1.929-5.918 6.077-5.918 2.366 0 3.712.69 4.695 2.033V9.804h-8.807v-3.05H35.99V20.26h2.038v3.376h-5.422V21.93c-1.02 1.343-2.33 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.201-2.868-3.712-2.868s-3.712 1.198-3.712 2.868 1.2 2.869 3.712 2.869c2.511 0 3.712-1.162 3.712-2.869Zm6.951-2.869c0-5.302 2.62-8.787 7.605-8.787 4.44 0 7.06 2.723 7.06 6.753h-3.384c-.145-2.106-.837-3.703-3.494-3.703-3.166 0-4.367 1.343-4.367 5.736 0 4.394 1.201 5.737 4.367 5.737 2.657 0 3.349-1.634 3.494-3.703h3.384c0 4.03-2.62 6.753-7.06 6.753-4.985 0-7.605-3.485-7.605-8.786Zm21.251 1.562v6.898h-3.384V0h3.384v13.725h2.657l4.73-6.972h4.113l-5.823 8.497 5.787 8.423h-4.113l-4.73-6.898h-2.62Zm29.879-1.562c0 4.975-1.929 8.787-7.424 8.787-2.365 0-4.04-.908-5.058-2.36v2.033H74.82V0h3.385v8.787c1.019-1.453 2.693-2.36 5.058-2.36 5.495 0 7.424 3.812 7.424 8.786Zm-3.384 0c0-4.066-1.238-5.736-4.55-5.736-3.311 0-4.548 1.67-4.548 5.736 0 4.067 1.237 5.737 4.549 5.737 3.311 0 4.549-1.67 4.549-5.737Zm5.568 2.869c0-2.94 1.929-5.918 6.078-5.918 2.365 0 3.675.69 4.694 2.033V9.804h-8.807v-3.05h12.191V20.26h2.038v3.376h-5.422V21.93c-1.019 1.343-2.329 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.237-2.868-3.675-2.868-2.439 0-3.676 1.198-3.676 2.868s1.237 2.869 3.675 2.869c2.439 0 3.676-1.162 3.676-2.869Zm7.97 3.738v-3.412c3.094 1.924 4.695 2.541 7.169 2.541 2.184 0 2.985-.944 2.985-1.997 0-1.198-.874-1.815-4.004-2.505-4.84-1.053-6.15-2.65-6.15-5.301 0-2.796 2.402-4.72 6.041-4.72 2.257 0 4.513.617 6.15 1.743v3.05c-2.474-1.235-4.658-1.743-6.514-1.743-1.746 0-2.292.726-2.292 1.597 0 .944.436 1.598 3.311 2.36 5.022 1.344 6.842 2.397 6.842 5.52 0 2.868-2.402 5.082-6.369 5.082-2.62-.036-4.694-.544-7.169-2.214Zm15.758-6.607c0-5.302 2.111-8.787 7.315-8.787 5.204 0 7.315 3.159 7.315 8.46v1.851h-11.173c.219 2.36 1.201 4.212 5.132 4.212 1.346 0 2.692 0 4.876-.617v2.977c-2.657.69-3.603.69-4.876.69-7.643 0-8.589-5.446-8.589-8.786Zm11.245-1.525c-.073-2.942-1.201-4.212-3.93-4.212-2.73 0-3.749 1.488-3.93 4.211h7.86Z"/></g></svg>`;

const BB_LOGO_WHITE = BB_LOGO_DARK.replace(/#041326/g, '#FFFFFF');

function motifSvg(color) {
  return `<svg width="24" height="24" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><path d="M0 50 L0 100 L100 100 L100 0 L50 0 L50 50 Z" fill="${color}"/></svg>`;
}

// ── Grid Lines ──
const GRID_CONFIGS = {
  cover:              { v:[4.13, 54.1, 95.86],  h:[21.54, 64.86, 92.65] },
  'chapter-numbered': { v:[4.13, 27, 95.86],    h:[11.5, 64.86, 92.65]  },
  'chapter-standard': { v:[4.13, 95.86],         h:[11.5, 64.86, 92.65]  },
  content:            { v:[2.9, 97.1],             h:[5.15, 94.85]         },
  thankyou:           { v:[2.9, 97.1],             h:[26.11, 73.8]         },
  toc:                { v:[2.9, 40, 97.1],         h:[5.15, 94.85]         },
  columns:            { v:[2.9, 97.1],             h:[5.15, 27.53, 32.42, 94.85] },
  'overview-about':   { v:[2.9, 59.45, 97.1],     h:[5.15, 74.85, 94.85]  },
  product:            { v:[2.9, 50, 97.1],         h:[5.15, 94.85]         },
  'cover-photo':      { v:[4.13, 54.1, 95.86],     h:[21.54, 92.65]},
  'cover-photo-navy': { v:[4.13, 54.1, 95.86],    h:[21.54, 64.86, 92.65]},
  statement:          { v:[2.9, 97.1],             h:[5.15, 94.85]         },
  testimonial:        { v:[2.9, 33, 97.1],         h:[5.15, 12, 80, 94.85] },
  team:               { v:[2.9, 97.1],             h:[5.15, 25, 94.85]     },
  agenda:             { v:[2.9, 97.1],             h:[5.15, 30, 94.85]     },
  roadmap:            { v:[2.9, 97.1],             h:[5.15, 25, 94.85]     }
};

function gridLines(variant, vBottom) {
  const c = GRID_CONFIGS[variant];
  if (!c) return '';
  let h = '<div class="grid-lines">';
  const vStyle = vBottom != null ? ';bottom:'+vBottom+'%' : '';
  c.v.forEach(x => { h += `<div class="gl-v" style="left:${x}%${vStyle}"></div>`; });
  c.h.forEach(y => { h += `<div class="gl-h" style="top:${y}%"></div>`; });
  return h + '</div>';
}

const BB_FOOTER_LOGO = `<svg xmlns="http://www.w3.org/2000/svg" width="100%" fill="none" viewBox="0 0 142 24" class="bb-logo"><g clip-path="url(#a)"><path fill="currentColor" d="M3.457 7.552h3.457V.689H0v3.413h3.457v3.45Z"/><path fill="currentColor" d="M14.193 11.909v-.545c3.384-.472 4.257-2.687 4.257-4.901 0-2.724-1.856-5.665-6.477-5.774H9.207v3.45h2.766c2.438.036 2.947 1.597 2.911 2.868-.073 2.796-1.347 2.869-3.494 2.905H3.457v13.797h8.26c5.569 0 7.425-3.159 7.425-6.427 0-2.832-.983-4.865-4.95-5.373Zm-2.366 8.315H6.951v-6.972h4.84c2.911 0 3.857.545 3.857 3.522.037 2.505-.91 3.413-3.82 3.45Zm10.007-2.142c0-2.94 1.929-5.918 6.077-5.918 2.366 0 3.712.69 4.695 2.033V9.804h-8.807v-3.05H35.99V20.26h2.038v3.376h-5.422V21.93c-1.02 1.343-2.33 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.201-2.868-3.712-2.868s-3.712 1.198-3.712 2.868 1.2 2.869 3.712 2.869c2.511 0 3.712-1.162 3.712-2.869Zm6.951-2.869c0-5.302 2.62-8.787 7.605-8.787 4.44 0 7.06 2.723 7.06 6.753h-3.384c-.145-2.106-.837-3.703-3.494-3.703-3.166 0-4.367 1.343-4.367 5.736 0 4.394 1.201 5.737 4.367 5.737 2.657 0 3.349-1.634 3.494-3.703h3.384c0 4.03-2.62 6.753-7.06 6.753-4.985 0-7.605-3.485-7.605-8.786Zm21.251 1.562v6.898h-3.384V0h3.384v13.725h2.657l4.73-6.972h4.113l-5.823 8.497 5.787 8.423h-4.113l-4.73-6.898h-2.62Zm29.879-1.562c0 4.975-1.929 8.787-7.424 8.787-2.365 0-4.04-.908-5.058-2.36v2.033H74.82V0h3.385v8.787c1.019-1.453 2.693-2.36 5.058-2.36 5.495 0 7.424 3.812 7.424 8.786Zm-3.384 0c0-4.066-1.238-5.736-4.55-5.736-3.311 0-4.548 1.67-4.548 5.736 0 4.067 1.237 5.737 4.549 5.737 3.311 0 4.549-1.67 4.549-5.737Zm5.568 2.869c0-2.94 1.929-5.918 6.078-5.918 2.365 0 3.675.69 4.694 2.033V9.804h-8.807v-3.05h12.191V20.26h2.038v3.376h-5.422V21.93c-1.019 1.343-2.329 2.033-4.695 2.033-4.148.037-6.077-2.94-6.077-5.882Zm10.772 0c0-1.706-1.237-2.868-3.675-2.868-2.439 0-3.676 1.198-3.676 2.868s1.237 2.869 3.675 2.869c2.439 0 3.676-1.162 3.676-2.869Zm7.97 3.738v-3.412c3.094 1.924 4.695 2.541 7.169 2.541 2.184 0 2.985-.944 2.985-1.997 0-1.198-.874-1.815-4.004-2.505-4.84-1.053-6.15-2.65-6.15-5.301 0-2.796 2.402-4.72 6.041-4.72 2.257 0 4.513.617 6.15 1.743v3.05c-2.474-1.235-4.658-1.743-6.514-1.743-1.746 0-2.292.726-2.292 1.597 0 .944.436 1.598 3.311 2.36 5.022 1.344 6.842 2.397 6.842 5.52 0 2.868-2.402 5.082-6.369 5.082-2.62-.036-4.694-.544-7.169-2.214Zm15.758-6.607c0-5.302 2.111-8.787 7.315-8.787 5.204 0 7.315 3.159 7.315 8.46v1.851h-11.173c.219 2.36 1.201 4.212 5.132 4.212 1.346 0 2.692 0 4.876-.617v2.977c-2.657.69-3.603.69-4.876.69-7.643 0-8.589-5.446-8.589-8.786Zm11.245-1.525c-.073-2.942-1.201-4.212-3.93-4.212-2.73 0-3.749 1.488-3.93 4.211h7.86Z"/></g></svg>`;

function footerChrome(theme, num) {
  return `<div class="slide-footer"><div class="slide-footer-logo">${BB_FOOTER_LOGO}</div></div><span class="slide-footer-num">${num}</span>`;
}

// ── Template Renderers ──

function renderCoverColorBlock(d, i) {
  const title = (d.title || '').replace(/\n/g, '<br>');
  return `<div class="slide layout-cover-color-block" data-theme="navy" data-idx="${i}">
    ${gridLines('cover')}
    <div class="cover-logo">${BB_LOGO_WHITE}</div>
    <div class="slide-motif">${motifSvg('#fff')}</div>
    ${d.partner ? '<div class="partner-logo">Partner Logo</div>' : ''}
    ${d.label ? `<div class="cover-label">${d.label}</div>` : ''}
    <div class="cover-title">${title}</div>
    ${d.date ? `<div class="cover-date">${d.date}</div>` : ''}
  </div>`;
}

function renderChapterNumbered(d, i) {
  const theme = d.theme || 'navy';
  const mc = theme === 'blue' ? '#fff' : '#3367FF';
  const title = (d.title || '').replace(/\n/g, '<br>');
  return `<div class="slide layout-chapter-numbered" data-theme="${theme}" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:4.13%"></div><div class="gl-v" style="left:27%;top:21.54%;bottom:35.14%"></div><div class="gl-v" style="left:95.86%"></div><div class="gl-h" style="top:21.54%;right:4.14%"></div><div class="gl-h" style="top:64.86%;left:4.13%;right:4.14%"></div></div>
    <div class="slide-motif">${motifSvg(mc)}</div>
    <div class="chapter-number">${d.number || '01'}</div>
    ${d.label ? `<div class="chapter-label t-label">${d.label}</div>` : ''}
    <div class="chapter-title">${title}</div>
    ${d.subtitle ? `<div class="chapter-subtitle">${d.subtitle}</div>` : ''}
  </div>`;
}

function renderChapterStandard(d, i) {
  const theme = d.theme || 'navy';
  const mc = theme === 'blue' ? '#fff' : '#3367FF';
  const title = (d.title || '').replace(/\n/g, '<br>');
  return `<div class="slide layout-chapter-standard" data-theme="${theme}" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:4.13%"></div><div class="gl-v" style="left:95.86%"></div><div class="gl-h" style="top:21.54%;right:4.14%"></div><div class="gl-h" style="top:64.86%;left:4.13%;right:4.14%"></div></div>
    <div class="slide-motif">${motifSvg(mc)}</div>
    ${d.label ? `<div class="chapter-label t-label">${d.label}</div>` : ''}
    <div class="chapter-title">${title}</div>
    ${d.subtitle ? `<div class="chapter-subtitle">${d.subtitle}</div>` : ''}
  </div>`;
}

function renderContentStandard(d, i) {
  const theme = d.theme === 'dark' ? 'navy' : 'white';
  const hasHeader = d.label || d.title;
  let bc = 'content-body t-body';
  if (!hasHeader) bc += ' body-only';
  else if (!d.subtitle) bc += ' no-subtitle';
  return `<div class="slide layout-content-standard" data-theme="${theme}" data-idx="${i}">
    ${gridLines('content', 5.15)}
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="content-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="content-title t-title">${d.title}</div>` : ''}
    ${d.subtitle ? `<div class="content-subtitle t-subtitle">${d.subtitle}</div>` : ''}
    ${d.body ? `<div class="${bc}">${d.body}</div>` : ''}
    ${footerChrome(theme, i + 1)}
  </div>`;
}

function renderThankYou(d, i) {
  return `<div class="slide layout-thank-you" data-theme="navy" data-idx="${i}">
    <div class="cover-bg"><img src="${BB_SHARED_ASSETS}/images/bg.jpg" alt=""></div>
    ${gridLines('thankyou')}
    <div class="cover-logo">${BB_LOGO_WHITE}</div>
    <div class="slide-motif">${motifSvg('#fff')}</div>
    <div class="thankyou-text">Thank you</div>
  </div>`;
}

function renderImage(i) {
  const n = String(i + 1).padStart(2, '0');
  return `<div class="slide" data-idx="${i}"><img class="slide-bg" src="${BB_SHARED_ASSETS}/media/slide-${n}.jpg" alt="Slide ${i+1}" loading="${i<3?'eager':'lazy'}"></div>`;
}

function renderToc(d, i) {
  const items = d.items || [];
  const n = items.length;
  const numbered = d.numbered !== false;
  const rows = items.map((item, idx) => {
    const num = numbered ? `<span class="toc-num">${String(idx+1).padStart(2,'0')}</span>` : '';
    return `<div class="toc-row">${num}<span class="toc-entry">${item}</span></div>`;
  }).join('');
  // Calculate dynamic horizontal line aligned to a row border closest to ~41%
  const rowH = 89.7 / n;
  let bestRow = 1, bestDist = Infinity;
  for (let k = 1; k < n; k++) {
    const dist = Math.abs(5.15 + k * rowH - 41.39);
    if (dist < bestDist) { bestDist = dist; bestRow = k; }
  }
  let hLinePos = 34.8;
  if (n > 3) {
    let bestRow = 1, bestDist = Infinity;
    for (let k = 1; k < n; k++) {
      const dist = Math.abs(5.15 + k * rowH - 34.8);
      if (dist < bestDist) { bestDist = dist; bestRow = k; }
    }
    hLinePos = +(5.15 + bestRow * rowH).toFixed(2);
  }
  const grid = `<div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:40%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:${hLinePos}%;left:2.9%;right:60%"></div><div class="gl-h" style="top:94.85%"></div></div>`;
  return `<div class="slide layout-toc" data-theme="white" data-idx="${i}">
    ${grid}
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="toc-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="toc-title t-title">${d.title}</div>` : ''}
    <div class="toc-rows">${rows}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderContentColumns(d, i) {
  const cols = d.columns || [];
  const colHtml = cols.map(c => {
    const icon = c.icon ? `<div class="col-icon">${c.icon}</div>` : '';
    return `<div class="col-item">${icon}${c.subtitle ? `<div class="col-subtitle">${c.subtitle}</div>` : ''}${c.body ? `<div class="col-body">${c.body}</div>` : ''}</div>`;
  }).join('');
  return `<div class="slide layout-content-columns" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:27.53%;left:2.9%;right:2.9%"></div><div class="gl-h" style="top:32.42%;left:2.9%;right:2.9%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="columns-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="columns-title t-title">${d.title}</div>` : ''}
    <div class="columns-divider"></div>
    <div class="columns-row">${colHtml}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderOverviewAbout(d, i) {
  const stats = (d.stats || []).map(s =>
    `<div class="stat-item"><span class="stat-value">${s.value}</span><span class="stat-label">${s.label}</span></div>`
  ).join('');
  const img = d.image ? `<img src="${d.image}" alt="">` : '<span>Image</span>';
  return `<div class="slide layout-overview-about" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:59.45%;bottom:25.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:74.85%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="about-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="about-title t-title">${d.title}</div>` : ''}
    ${d.subtitle ? `<div class="about-subtitle t-subtitle">${d.subtitle}</div>` : ''}
    <div class="about-image">${img}</div>
    <div class="about-stats">${stats}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderOverviewStats(d, i) {
  const stats = (d.stats || []).map(s =>
    `<div class="stat-item"><span class="stat-value">${s.value}</span><span class="stat-label">${s.label}</span></div>`
  ).join('');
  const img = d.image ? `<img src="${d.image}" alt="">` : '<span>Image</span>';
  return `<div class="slide layout-overview-stats" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:50%;top:5.15%;bottom:25.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:74.85%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="about-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="about-title t-title">${d.title}</div>` : ''}
    ${d.subtitle ? `<div class="about-subtitle">${d.subtitle}</div>` : ''}
    <div class="about-image">${img}</div>
    <div class="about-stats">${stats}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderProduct(d, i) {
  const hasBg = d.imageBg !== false;
  const img = d.image ? `<img src="${d.image}" alt="">` : '<span class="placeholder">Screenshot</span>';
  return `<div class="slide layout-product" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:50%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:50%;left:2.9%;right:50%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="product-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="product-title t-title">${d.title}</div>` : ''}
    ${d.subtitle ? `<div class="product-subtitle t-subtitle">${d.subtitle}</div>` : ''}
    ${d.body ? `<div class="product-body t-body">${d.body}</div>` : ''}
    <div class="product-image${hasBg ? ' has-bg' : ''}">${img}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderCoverPhoto(d, i) {
  const title = (d.title || '').replace(/\n/g, '<br>');
  if (d.image) {
    return `<div class="slide layout-cover-photo" data-idx="${i}">
      <div class="cover-bg"><img src="${d.image}" alt=""></div>
      <div class="cover-overlay"></div>
      <div class="grid-lines"><div class="gl-v" style="left:4.13%;bottom:7.35%"></div><div class="gl-v" style="left:54.1%;bottom:7.35%"></div><div class="gl-v" style="left:95.86%;bottom:7.35%"></div><div class="gl-h" style="top:21.54%;left:4.13%;right:45.9%"></div><div class="gl-h" style="top:92.65%"></div></div>
      <div class="cover-panel"></div>
      <div class="cover-logo">${BB_LOGO_DARK}</div>
      <div class="slide-motif">${motifSvg('#041326')}</div>
      ${d.label ? `<div class="cover-label">${d.label}</div>` : ''}
      <div class="cover-title">${title}</div>
      ${d.date ? `<div class="cover-date">${d.date}</div>` : ''}
    </div>`;
  }
  const partnerEl = d.partner
    ? `<div class="cover-partner"><img src="${d.partner}" alt=""></div>`
    : `<div class="cover-partner placeholder"><svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="#8a8f98" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg><span style="display:block;margin-top:6px;font-size:0.55em;font-weight:400;color:#8a8f98">Client Logo</span></div>`;
  return `<div class="slide layout-cover-photo" data-theme="navy" data-idx="${i}">
    <div class="cover-bg"><img src="${BB_SHARED_ASSETS}/images/bg.jpg" alt=""></div>
    <div class="grid-lines"><div class="gl-v" style="left:4.13%"></div><div class="gl-v" style="left:54.1%"></div><div class="gl-v" style="left:95.86%"></div><div class="gl-h" style="top:21.54%;left:4.13%;right:4.14%"></div><div class="gl-h" style="top:64.86%;left:4.13%;right:45.9%"></div></div>
    ${partnerEl}
    <div class="cover-logo">${BB_LOGO_WHITE}</div>
    <div class="slide-motif">${motifSvg('#fff')}</div>
    ${d.label ? `<div class="cover-label">${d.label}</div>` : ''}
    <div class="cover-title">${title}</div>
    ${d.date ? `<div class="cover-date">${d.date}</div>` : ''}
  </div>`;
}

function renderStatement(d, i) {
  const theme = d.variant === 'dark' ? 'navy' : 'white';
  const accent = d.accent || 'blue';
  const bandClass = d.variant === 'dark' ? 'band-dark' : (accent === 'red' ? 'band-red' : 'band-blue');
  const mc = theme === 'navy' ? '#fff' : '#3367FF';
  return `<div class="slide layout-statement${accent === 'red' ? ' accent-red' : ''}" data-theme="${theme}" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:25.13%"></div><div class="gl-h" style="top:73%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg(mc)}</div>
    ${d.label ? `<div class="statement-label t-label">${d.label}</div>` : ''}
    <div class="statement-band ${bandClass}">
      <div class="statement-text">${d.text || ''}</div>
    </div>
    ${footerChrome(theme, i + 1)}
  </div>`;
}

function renderStatementStat(d, i) {
  const accent = d.accent || 'blue';
  const bandClass = accent === 'red' ? 'band-red' : 'band-blue';
  const numClass = accent === 'red' ? 'num-red' : 'num-blue';
  const statStr = d.stat || '70%';
  const sm = statStr.match(/^([\d,.]+)(.*)$/);
  const statHtml = sm ? `${sm[1]}<span class="stat-unit">${sm[2]}</span>` : statStr;
  return `<div class="slide layout-statement-stat${accent === 'red' ? ' accent-red' : ''}" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:25.13%"></div><div class="gl-h" style="top:73%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="stat-label t-label">${d.label}</div>` : ''}
    <div class="stat-band ${bandClass}">
      <div class="stat-content">
        <div class="stat-number ${numClass}">${statHtml}</div>
        <div class="stat-desc">
          <div class="stat-desc-text">${d.text || ''}</div>
          ${d.source ? `<div class="stat-source">Source: ${d.source}</div>` : ''}
        </div>
      </div>
    </div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderTestimonial(d, i) {
  const img = d.image ? `<img src="${d.image}" alt="">` : `<span class="placeholder-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></span>`;
  return `<div class="slide layout-testimonial" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:33%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:16.52%;left:2.9%;right:2.9%"></div><div class="gl-h" style="top:77.71%;left:33%;right:2.9%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    <div class="testimonial-image">${img}</div>
    <div class="testimonial-label t-label">TESTIMONIAL</div>
    <div class="testimonial-content">
      ${d.logo ? `<div class="testimonial-logo">${d.logo}</div>` : ''}
      <div class="testimonial-quote">"${d.quote || ''}"</div>
      <div class="testimonial-author">
        <div class="testimonial-name">${d.name || ''}</div>
        <div class="testimonial-title">${d.role || ''}</div>
      </div>
    </div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function teamPhotoPlaceholder() {
  return `<span class="placeholder-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg></span>`;
}

function renderTeam(d, i) {
  const members = d.members || [];
  const count = members.length;
  let gridClass = '', gridStyle = '', cellsHtml = '';

  if (count <= 2 || count === 3) {
    // Feature layout: label on left, photo+name pairs on right
    gridClass = 'team-feature';
    const rows = members.length;
    gridStyle = `grid-template-columns:40% 30% 30%;grid-template-rows:repeat(${rows},1fr)`;
    cellsHtml = `<div class="team-label-cell"><span class="t-label">${d.label || ''}</span></div>`;
    members.forEach(m => {
      cellsHtml += `<div class="team-cell"><div class="team-photo">${m.image ? `<img src="${m.image}">` : teamPhotoPlaceholder()}</div></div>
      <div class="team-cell"><div class="team-info"><div class="team-name">${m.name}</div><div class="team-role">${m.role || ''}</div></div></div>`;
    });
  } else if (count === 5) {
    gridClass = 'team-5';
    gridStyle = `grid-template-columns:repeat(5,1fr);grid-template-rows:52% 1fr`;
    members.forEach(m => {
      cellsHtml += `<div class="team-cell"><div class="team-photo">${m.image ? `<img src="${m.image}">` : teamPhotoPlaceholder()}</div></div>`;
    });
    members.forEach(m => {
      cellsHtml += `<div class="team-cell"><div class="team-info"><div class="team-name">${m.name}</div><div class="team-role">${m.role || ''}</div></div></div>`;
    });
  } else {
    // Standard grid — adapt rows to member count for best fit
    const maxRows = count <= 8 ? 2 : count <= 12 ? 3 : 4;
    const cols = Math.ceil(count / maxRows);
    const rows = Math.ceil(count / cols);
    gridStyle = `grid-template-columns:repeat(${cols},1fr);grid-template-rows:repeat(${rows},1fr)`;
    members.forEach(m => {
      cellsHtml += `<div class="team-cell"><div class="team-photo">${m.image ? `<img src="${m.image}">` : teamPhotoPlaceholder()}</div><div class="team-info"><div class="team-name">${m.name}</div><div class="team-role">${m.role || ''}</div></div></div>`;
    });
  }

  const showLabel = count > 3;
  return `<div class="slide layout-team" data-theme="white" data-idx="${i}">
    <div class="grid-lines"><div class="gl-v" style="left:2.9%;bottom:5.15%"></div><div class="gl-v" style="left:97.1%;bottom:5.15%"></div><div class="gl-h" style="top:5.15%"></div><div class="gl-h" style="top:27.53%;left:2.9%;right:2.9%"></div><div class="gl-h" style="top:32.42%;left:2.9%;right:2.9%"></div><div class="gl-h" style="top:94.85%"></div></div>
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${showLabel && d.label ? `<div class="team-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="team-title t-title">${d.title}</div>` : ''}
    <div class="team-grid ${gridClass}" style="${gridStyle}">${cellsHtml}</div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

function renderAgendaTable(d, i) {
  const headers = d.headers || ['Session', 'Time', 'Location', 'Speaker'];
  const rows = (d.rows || []).map(r => {
    const hl = r.highlight ? ' highlight' : '';
    return `<div class="agenda-row${hl}">${r.cells.map(c => `<span>${c}</span>`).join('')}</div>`;
  }).join('');
  return `<div class="slide layout-agenda-table" data-theme="navy" data-idx="${i}">
    ${gridLines('agenda', 5.15)}
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="agenda-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="agenda-title t-title">${d.title}</div>` : ''}
    <div class="agenda-table">
      <div class="agenda-header">${headers.map(h => `<span>${h}</span>`).join('')}</div>
      ${rows}
    </div>
    ${footerChrome('navy', i + 1)}
  </div>`;
}

function renderRoadmap(d, i) {
  const months = d.months || ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const monthsHtml = months.map(m => `<span class="roadmap-month">${m}</span>`).join('');
  const totalM = months.length;
  const rowsHtml = (d.rows || []).map(r => {
    const bars = (r.bars || []).map(b => {
      const left = ((b.start || 0) / totalM * 100).toFixed(1);
      const width = ((b.duration || 1) / totalM * 100).toFixed(1);
      return `<div class="roadmap-bar bar-${b.color || 'blue'}" style="left:${left}%;width:${width}%">${b.label || ''}</div>`;
    }).join('');
    return `<div class="roadmap-row"><span class="roadmap-row-label">${r.label || ''}</span><div class="roadmap-row-track">${bars}</div></div>`;
  }).join('');
  return `<div class="slide layout-roadmap" data-theme="white" data-idx="${i}">
    ${gridLines('roadmap', 5.15)}
    <div class="slide-motif">${motifSvg('#3367FF')}</div>
    ${d.label ? `<div class="roadmap-label t-label">${d.label}</div>` : ''}
    ${d.title ? `<div class="roadmap-title t-title">${d.title}</div>` : ''}
    <div class="roadmap-chart">
      <div class="roadmap-months">${monthsHtml}</div>
      <div class="roadmap-dividers">${months.map(() => '<div class="roadmap-divider"></div>').join('')}</div>
      <div class="roadmap-rows">${rowsHtml}</div>
    </div>
    ${footerChrome('white', i + 1)}
  </div>`;
}

// ── Slide Data (complete demo deck — all template families) ──

const TOTAL = SLIDES.length;

// ── Build Slides ──
function buildSlides() {
  const frame = document.getElementById('slideFrame');
  let html = '';
  SLIDES.forEach((s, i) => {
    switch (s.layout) {
      case 'cover-color-block':  html += renderCoverColorBlock(s, i); break;
      case 'cover-photo':        html += renderCoverPhoto(s, i); break;
      case 'chapter-numbered':   html += renderChapterNumbered(s, i); break;
      case 'chapter-standard':   html += renderChapterStandard(s, i); break;
      case 'toc':                html += renderToc(s, i); break;
      case 'content-standard':   html += renderContentStandard(s, i); break;
      case 'content-columns':    html += renderContentColumns(s, i); break;
      case 'overview-about':     html += renderOverviewAbout(s, i); break;
      case 'overview-stats':    html += renderOverviewStats(s, i); break;
      case 'product':            html += renderProduct(s, i); break;
      case 'statement':          html += renderStatement(s, i); break;
      case 'statement-stat':     html += renderStatementStat(s, i); break;
      case 'testimonial':        html += renderTestimonial(s, i); break;
      case 'team':               html += renderTeam(s, i); break;
      case 'agenda-table':       html += renderAgendaTable(s, i); break;
      case 'roadmap':            html += renderRoadmap(s, i); break;
      case 'thank-you':          html += renderThankYou(s, i); break;
      case 'image': default:     html += renderImage(i); break;
    }
  });
  frame.innerHTML = html;
}

// ── Navigation State ──
const state = { current: 0, overview: false, presenter: false, timerStart: null, timerInterval: null };

function goTo(n) {
  if (n < 0 || n >= TOTAL) return;
  document.querySelectorAll('#slideFrame > .slide').forEach((s, i) => s.classList.toggle('active', i === n));
  state.current = n;
  updateChrome();
  window.location.hash = `slide=${n + 1}`;
  preload(n);
  if (state.presenter) updatePresenter();
}
function next() { goTo(Math.min(state.current + 1, TOTAL - 1)); }
function prev() { goTo(Math.max(state.current - 1, 0)); }

function updateChrome() {
  document.getElementById('progressBar').style.width = `${((state.current + 1) / TOTAL) * 100}%`;
  document.getElementById('slideCounter').textContent = `${state.current + 1} / ${TOTAL}`;
}

function preload(n) {
  [n-1, n+1, n+2].forEach(i => {
    if (i >= 0 && i < TOTAL && SLIDES[i].layout === 'image') {
      const img = new Image();
      img.src = `media/slide-${String(i+1).padStart(2,'0')}.jpg`;
    }
  });
}

// ── Overview ──
function buildOverview() {
  const grid = document.getElementById('overviewGrid');
  const slides = document.querySelectorAll('#slideFrame > .slide');
  grid.innerHTML = '';
  for (let i = 0; i < TOTAL; i++) {
    const thumb = document.createElement('div');
    thumb.className = `overview-thumb${i === state.current ? ' current' : ''}`;
    thumb.dataset.idx = i;

    const render = document.createElement('div');
    render.className = 'thumb-render';
    render.appendChild(slides[i].cloneNode(true));
    thumb.appendChild(render);

    const num = document.createElement('span');
    num.className = 'thumb-num';
    num.textContent = i + 1;
    thumb.appendChild(num);

    const label = document.createElement('span');
    label.className = 'thumb-label';
    const s = SLIDES[i];
    const variant = s.theme || s.variant || s.accent || (s.numbered === false ? 'plain' : '') || '';
    label.textContent = s.layout + (variant ? ' · ' + variant : '');
    thumb.appendChild(label);

    thumb.addEventListener('click', () => { goTo(i); toggleOverview(); });
    grid.appendChild(thumb);
  }
  requestAnimationFrame(() => {
    grid.querySelectorAll('.overview-thumb').forEach(t => {
      const r = t.querySelector('.thumb-render');
      if (r) r.style.transform = `scale(${t.offsetWidth / 1920})`;
    });
  });
}

function toggleOverview() {
  state.overview = !state.overview;
  document.getElementById('overviewOverlay').classList.toggle('open', state.overview);
  if (state.overview) buildOverview();
}

// ── Presenter ──
function updatePresenter() {
  const slides = document.querySelectorAll('#slideFrame > .slide');

  // Current slide
  const cur = document.getElementById('presenterCurrent');
  cur.querySelector('.thumb-render')?.remove();
  const curR = document.createElement('div');
  curR.className = 'thumb-render';
  curR.appendChild(slides[state.current].cloneNode(true));
  cur.appendChild(curR);

  // Next slide
  const nxt = document.getElementById('presenterNext');
  nxt.querySelector('.thumb-render')?.remove();
  if (state.current + 1 < TOTAL) {
    const nxtR = document.createElement('div');
    nxtR.className = 'thumb-render';
    nxtR.appendChild(slides[state.current + 1].cloneNode(true));
    nxt.appendChild(nxtR);
  }
  if (!nxt.querySelector('.presenter-next-label')) {
    const lbl = document.createElement('div');
    lbl.className = 'presenter-next-label';
    lbl.textContent = 'Next';
    nxt.insertBefore(lbl, nxt.firstChild);
  }

  requestAnimationFrame(() => {
    [cur, nxt].forEach(c => {
      const r = c.querySelector('.thumb-render');
      if (r) r.style.transform = `scale(${c.offsetWidth / 1920})`;
    });
  });

  document.getElementById('presenterNotes').value = SPEAKER_NOTES[state.current + 1] || '';
  document.getElementById('presenterSlideInfo').textContent = `${state.current + 1} / ${TOTAL}`;
}

function togglePresenter() {
  state.presenter = !state.presenter;
  document.getElementById('presenterOverlay').classList.toggle('open', state.presenter);
  if (state.presenter) {
    updatePresenter();
    if (!state.timerStart) {
      state.timerStart = Date.now();
      state.timerInterval = setInterval(() => {
        const s = Math.floor((Date.now() - state.timerStart) / 1000);
        const m = Math.floor(s / 60);
        document.getElementById('presenterTimer').textContent =
          `${String(m).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`;
      }, 1000);
    }
  }
}

// ── Goto ──
function showGoto() {
  document.getElementById('gotoDialog').classList.add('open');
  document.getElementById('gotoBackdrop').classList.add('open');
  const input = document.getElementById('gotoInput');
  input.max = TOTAL;
  input.value = '';
  input.focus();
}
function hideGoto() {
  document.getElementById('gotoDialog').classList.remove('open');
  document.getElementById('gotoBackdrop').classList.remove('open');
}

// ── Fullscreen ──
function toggleFullscreen() {
  if (!document.fullscreenElement && !document.webkitFullscreenElement) {
    (document.documentElement.requestFullscreen || document.documentElement.webkitRequestFullscreen).call(document.documentElement);
  } else {
    (document.exitFullscreen || document.webkitExitFullscreen).call(document);
  }
}

// ── Keyboard ──
document.addEventListener('keydown', e => {
  if (document.getElementById('gotoDialog').classList.contains('open')) {
    if (e.key === 'Enter') {
      const v = parseInt(document.getElementById('gotoInput').value);
      if (v >= 1 && v <= TOTAL) goTo(v - 1);
      hideGoto();
    } else if (e.key === 'Escape') { hideGoto(); }
    return;
  }
  switch (e.key) {
    case 'ArrowRight': case ' ': case 'Enter': case 'PageDown': e.preventDefault(); next(); break;
    case 'ArrowLeft': case 'Backspace': case 'PageUp': e.preventDefault(); prev(); break;
    case 'Home': e.preventDefault(); goTo(0); break;
    case 'End': e.preventDefault(); goTo(TOTAL - 1); break;
    case 'f': case 'F': toggleFullscreen(); break;
    case 'o': case 'O': toggleOverview(); break;
    case 'p': case 'P': togglePresenter(); break;
    case 'g': case 'G': showGoto(); break;
    case 'Escape':
      if (state.overview) toggleOverview();
      else if (state.presenter) togglePresenter();
      else if (document.fullscreenElement || document.webkitFullscreenElement) toggleFullscreen();
      break;
  }
});

// ── Mouse click navigation ──
document.getElementById('slideViewport').addEventListener('click', e => {
  if (state.overview || state.presenter) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const x = (e.clientX - rect.left) / rect.width;
  if (x > 0.65) next(); else if (x < 0.35) prev();
});

// ── Touch ──
let touchX = 0;
document.getElementById('slideViewport').addEventListener('touchstart', e => { touchX = e.changedTouches[0].screenX; }, {passive: true});
document.getElementById('slideViewport').addEventListener('touchend', e => {
  const diff = touchX - e.changedTouches[0].screenX;
  if (Math.abs(diff) > 50) { diff > 0 ? next() : prev(); }
}, {passive: true});

// ── Goto backdrop ──
document.getElementById('gotoBackdrop').addEventListener('click', hideGoto);

// ── Hash routing ──
function loadFromHash() {
  const m = window.location.hash.match(/slide=(\d+)/);
  if (m) goTo(parseInt(m[1]) - 1);
}
window.addEventListener('hashchange', loadFromHash);

// ── Init ──
window.addEventListener('load', () => {
  buildSlides();
  loadFromHash();
  if (state.current === 0) goTo(0);
  setTimeout(() => { document.getElementById('fullscreenHint').style.opacity = '0'; }, 4000);
});
