"""
Port Pages Generator
Generates responsive, SEO-optimized port landing pages with the new Cyan/Blue Premium theme,
centralized CSS (assets/css/port-pages.css), matching navbar & footer from index.html (without drinks & snacks),
schema markup, sticky TOC sidebar, and styled article content from Excel data.
"""

import os
import re
import html
import json
import openpyxl

# Configuration Paths
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PORTS_DIR = os.path.join(REPO_ROOT, "ports")
CSS_FILE = os.path.join(REPO_ROOT, "assets", "css", "port-pages.css")
EXCEL_PATH = r"D:\FalconXoft Ship Chandler\Website Data\Ship_Chandler_SEO_49_Pages_FULL.xlsx"

# Section heading IDs matching Table of Contents and Bissau layout
H2_IDS = [
    'professional-services',
    'provisions',
    'bonded',
    'deck',
    'engine',
    'cabin',
    'safety',
    'electrical',
    'chemicals',
    'welding',
    'spare-parts',
    'publications',
    'tools',
    'technical-support',
    'urgent',
    'vessels',
    'rfq',
    'why-choose',
    None,
    None,
    None,
    None,
]


def get_clean_port_name(page_name):
    """
    Derives clean port name for the CTA heading:
    e.g. 'Bissau Ship Chandler - Guinea' -> 'Bissau Port'
         'Ship Chandler Apapa' -> 'Apapa Port'
         'Ship Chandler Dar Es Salaam' -> 'Dar Es Salaam Port'
    """
    clean = page_name
    clean = re.sub(r'\bShip\s*Chandlers?\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bShip\s*Supply\s*Chandler\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\bShipchandler\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\s*-\s*.*$', '', clean).strip()
    clean = re.sub(r'\s+', ' ', clean).strip()
    if 'port' not in clean.lower():
        clean += ' Port'
    return clean


def format_hero_title(h1, page_name):
    """
    Formats the H1 title with a styled <span> highlight to match Bissau's two-tone theme.
    """
    if ' - ' in h1:
        parts = h1.split(' - ', 1)
        return f"{parts[0]} <span>- {parts[1]}</span>"
    elif ' -' in h1:
        parts = h1.split(' -', 1)
        return f"{parts[0]} <span>-{parts[1]}</span>"

    m = re.match(r'^(Ship\s*Chandlers?|Shipchandler)\s+(.*)$', h1, flags=re.IGNORECASE)
    if m:
        return f"{m.group(1)} <span>{m.group(2)}</span>"

    m2 = re.match(r'^(.*?)\s+(Ship\s*Chandlers?|Ship\s*Supply\s*Chandler)$', h1, flags=re.IGNORECASE)
    if m2:
        return f"<span>{m2.group(1)}</span> {m2.group(2)}"

    return h1


def extract_and_centralize_css():
    """
    Extracts the CSS from bissau-ship-chandler-guinea.html if inline style block is present,
    and writes it to assets/css/port-pages.css.
    """
    bissau_path = os.path.join(PORTS_DIR, "bissau-ship-chandler-guinea.html")
    if not os.path.exists(bissau_path):
        print(f"[CSS] Bissau template not found at {bissau_path}, skipping extraction.")
        return

    with open(bissau_path, "r", encoding="utf-8") as f:
        bissau_html = f.read()

    style_start = "<style>"
    style_end = "</style>"

    if style_start in bissau_html and style_end in bissau_html:
        p1 = bissau_html.find(style_start)
        p2 = bissau_html.find(style_end)

        css_content = bissau_html[p1 + len(style_start):p2].strip()

        os.makedirs(os.path.dirname(CSS_FILE), exist_ok=True)
        with open(CSS_FILE, "w", encoding="utf-8") as f:
            f.write("/* ==========================================================================\n")
            f.write("   CENTRALIZED PORT PAGES STYLESHEET\n")
            f.write("   Theme: Light Premium - Cyan/Blue Nautical\n")
            f.write("   ========================================================================== */\n\n")
            f.write(css_content + "\n")

        print(f"[CSS] Centralized {len(css_content)} bytes of styles into {CSS_FILE}")
    else:
        print("[CSS] Master template already links to centralized CSS.")


def render_article_html(desc_text):
    """
    Parses the Markdown description from Excel into semantic HTML
    matching the exact structure, IDs, pill-styled lists, and spacing of the Bissau page.
    """
    blocks = [b.strip() for b in desc_text.split('\n\n') if b.strip()]
    lines = []
    h2_index = 0

    for b in blocks:
        if b.startswith('# '):
            # Skip top-level H1 (rendered in Hero section)
            continue
        elif b.startswith('## '):
            heading_text = b[3:].strip()
            # Clean up potential dash formatting
            heading_text = heading_text.replace('\u2013', '–')
            hid = H2_IDS[h2_index] if h2_index < len(H2_IDS) else None
            h2_index += 1
            if lines:
                lines.append('')
            if hid:
                lines.append(f'            <h2 id="{hid}">{heading_text}</h2>')
            else:
                lines.append(f'            <h2>{heading_text}</h2>')
        elif b.startswith('- '):
            lines.append('            <ul>')
            for item in b.split('\n'):
                item = item.strip()
                if not item:
                    continue
                val = re.sub(r'^\s*-\s*', '', item)
                lines.append(f'              <li>{val}</li>')
            lines.append('            </ul>')
        else:
            # Paragraph or bold summary
            if b.startswith('**') and b.endswith('**'):
                bold_content = b[2:-2].strip()
                lines.append(f'            <p><strong>{bold_content}</strong></p>')
            else:
                clean_p = ' '.join(b.split())
                lines.append(f'            <p>{clean_p}</p>')

    return '\n'.join(lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>__META_TITLE__</title>
  <meta name="description"
    content="__META_DESC__">
  <meta name="keywords"
    content="__KEYWORDS__">
  <meta name="author" content="SHIP CHANDLER MISURATA PORT CO., LTD">

  <link rel="canonical" href="__CANONICAL_URL__">

  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="__META_TITLE__">
  <meta property="og:url" content="__CANONICAL_URL__">
  <meta property="og:description"
    content="__META_DESC__">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ship Chandler Misurata">
  <meta property="og:image" content="https://shipchandlermisurata.com/assets/imgs/bg-hero.jpg">

  <!-- Twitter Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="__META_TITLE__">
  <meta name="twitter:description" content="__META_DESC__">
  <meta name="twitter:image" content="https://shipchandlermisurata.com/assets/imgs/bg-hero.jpg">

  <!-- Structured Data (JSON-LD) -->
  <script type="application/ld+json">
__SCHEMA_JSON__
  </script>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
    rel="stylesheet">

  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="../favicon.png">
  <link rel="shortcut icon" href="../favicon.ico">
  <link rel="apple-touch-icon" href="../assets/imgs/logo.png">

  <!-- Centralized Port Pages CSS -->
  <link rel="stylesheet" href="../assets/css/port-pages.css">
</head>

<body>

  <!-- HEADER / NAVBAR -->
  <header class="site-header" id="site-header">
    <div class="container header-inner">
      <a class="logo" href="../index.html">
        <img src="../assets/imgs/logo.png" alt="Ship Chandler Misurata Logo" width="50" height="50">
        <span class="logo-text">
          <strong>ShipChandler</strong>
          <span>Misurata</span>
        </span>
      </a>

      <button class="nav-toggle" type="button" aria-label="Toggle navigation">
        <span></span><span></span><span></span>
      </button>

      <nav class="primary-nav" id="primary-nav">
        <ul class="nav-list">
          <li class="nav-item"><a class="nav-link" href="../index.html">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="../about.html">About</a></li>

          <!-- Services Dropdown -->
          <li class="nav-item has-dropdown">
            <a class="nav-link" href="../services.html">Services <span class="nav-arrow"><svg
                  viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg></span></a>
            <div class="dropdown-menu">
              <a href="../services.html#provisions">Food Provisions Supply</a>
              <a href="../services.html#bonded">Bonded Stores</a>
              <a href="../services.html#deck">Deck Stores</a>
              <a href="../services.html#engine">Engine Stores</a>
              <a href="../services.html#cabin">Cabin & Galley</a>
              <a href="../services.html#safety">Safety & PPE</a>
              <a href="../services.html#electrical">Electrical Stores</a>
              <a href="../services.html#chemicals">Marine Chemicals</a>
              <a href="../services.html#welding">Welding Equipment</a>
              <a href="../services.html#spare-parts">Spare Parts</a>
              <a href="../services.html#publications">Nautical Charts</a>
              <a href="../services.html#tools">Tools & Hardware</a>
              <a href="../services.html#urgent">Urgent Supply</a>
            </div>
          </li>

          <!-- Ports Mega Menu -->
          <li class="nav-item has-mega">
            <a class="nav-link" href="javascript:void(0)">Ports <span class="nav-arrow"><svg
                  viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor"
                  stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg></span></a>
            <div class="mega-menu">
              <div class="mega-header">
                <div class="mega-header-title">Global Port Network</div>
                <div class="mega-search">
                  <i class="fas fa-search" style="color:var(--text-gray);"></i>
                  <input type="text" id="mega-port-search" placeholder="Search 49 ports...">
                </div>
              </div>
              <div class="mega-grid" id="mega-port-list">
                <!-- Populated via JS -->
              </div>
            </div>
          </li>

          <li class="nav-item"><a class="nav-link" href="../contact.html">Contact</a></li>
        </ul>
        <a class="btn btn-primary" style="padding: 12px 28px; font-size: 0.95rem;" href="../request-quote.html">Get
          Quote</a>
      </nav>
    </div>
  </header>

  <main>
    <!-- PORT HERO -->
    <section class="port-hero">
      <img class="port-hero-bg" src="../assets/imgs/bg-hero.jpg" alt="__HERO_ALT__">
      <div class="port-hero-overlay"></div>

      <div class="port-hero-container">
        <div class="port-hero-content">
          <ul class="port-breadcrumb">
            <li><a href="../index.html">Home</a></li>
            <li><span>/</span></li>
            <li><a href="../index.html#ports">Ports</a></li>
            <li><span>/</span></li>
            <li>__PAGE_NAME__</li>
          </ul>
          <span class="eyebrow" style="color: var(--primary-light);">Port Supply Profile</span>
          <h1 class="port-hero-title">__HERO_TITLE__</h1>
          <p class="port-hero-desc">__META_DESC__</p>
        </div>

        <div class="port-hero-badge">
          <div class="port-hero-card">
            <i class="fas fa-ship"></i>
            <div>
              <strong>Vessel Supply</strong>
              <span>Port, terminals & anchorage</span>
            </div>
          </div>
          <div class="port-hero-card">
            <i class="fas fa-clock"></i>
            <div>
              <strong>24/7 Operations</strong>
              <span>On-time dockside delivery</span>
            </div>
          </div>
          <div class="port-hero-card">
            <i class="fas fa-certificate"></i>
            <div>
              <strong>IMPA & ISSA Quality</strong>
              <span>Certified marine supplies</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PORT ARTICLE SECTION WITH STICKY SIDEBAR -->
    <section class="port-article-section">
      <div class="container">
        <div class="port-article-layout">

          <!-- Sticky Sidebar 'On This Page' -->
          <aside class="port-toc-sidebar">
            <h3>On This Page</h3>
            <nav class="port-toc-list">
              <a href="#professional-services">Professional Ship Supply</a>
              <a href="#provisions">Ship Provisions Supply</a>
              <a href="#bonded">Bonded Stores & Crew Welfare</a>
              <a href="#deck">Deck Stores Supply</a>
              <a href="#engine">Engine Stores Supply</a>
              <a href="#cabin">Cabin & Galley Stores</a>
              <a href="#safety">Safety Equipment & PPE</a>
              <a href="#electrical">Electrical Stores</a>
              <a href="#chemicals">Marine Chemicals</a>
              <a href="#welding">Welding Equipment</a>
              <a href="#spare-parts">Spare Parts & Technical</a>
              <a href="#publications">Nautical Charts</a>
              <a href="#tools">Tools & Hardware</a>
              <a href="#technical-support">Technical & Repair Support</a>
              <a href="#urgent">Urgent Ship Supply</a>
              <a href="#vessels">Vessels Supported</a>
              <a href="#rfq">How to Send an RFQ</a>
              <a href="#why-choose">Why Choose Us</a>
            </nav>
            <div class="port-toc-cta">
              <a href="../request-quote.html" class="btn btn-primary">Request a Quote <i class="fas fa-arrow-right"></i></a>
            </div>
          </aside>

          <!-- Main Port Article Content -->
          <article class="port-article-content">
__RENDERED_ARTICLE__

            <!-- Article CTA -->
            <div class="port-article-cta">
              <h3>Need Supply at __CLEAN_PORT__?</h3>
              <p>Send us your complete vessel requisition and our team will respond with a competitive quotation.</p>
              <a href="../request-quote.html" class="btn btn-primary">Request a Quote <i
                  class="fas fa-arrow-right"></i></a>
            </div>
          </article>
        </div>
      </div>
    </section>
  </main>

  <!-- FOOTER -->
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="logo" href="../index.html">
            <img src="../assets/imgs/logo.png" alt="Logo" width="50" height="50"
              style="border-radius: 10px; background:#fff; padding:4px;">
            <span class="logo-text">
              <strong>ShipChandler</strong>
              <span style="color: var(--primary);">Misurata</span>
            </span>
          </a>
          <p>SHIP CHANDLER MISURATA PORT CO., LTD is a licensed marine supplier providing food provisions, food stores,
            bond store supply, and emergency vessel supply services across the Port of Misurata, Libya.</p>
        </div>

        <div class="footer-col">
          <h4>Quick Links</h4>
          <ul class="footer-links">
            <li><a href="../index.html">Home</a></li>
            <li><a href="../about.html">About Us</a></li>
            <li><a href="../services.html">Services</a></li>
            <li><a href="../contact.html">Contact</a></li>
            <li><a href="../request-quote.html">Request a Quote</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Services</h4>
          <ul class="footer-links">
            <li><a href="../services.html#provisions">Provisions Supply</a></li>
            <li><a href="../services.html#bonded">Bonded Stores</a></li>
            <li><a href="../services.html#deck">Deck Stores</a></li>
            <li><a href="../services.html#engine">Engine Stores</a></li>
            <li><a href="../services.html#safety">Safety & PPE</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Contact Us</h4>
          <ul class="footer-contact">
            <li><i class="fas fa-map-marker-alt"></i> Misurata Seaport, Qasr Ahmed, Misurata, Libya</li>
            <li><i class="fas fa-envelope"></i> <a href="mailto:sales@shipchandlermisurata.com"
                style="color:inherit;">sales@shipchandlermisurata.com</a></li>
            <li><i class="fas fa-user-tie"></i> Ahmed Al-Misrati</li>
            <li>
              <a class="hero-whatsapp-bar" href="https://wa.me/2482743244" target="_blank" rel="noopener noreferrer"
                aria-label="Direct WhatsApp contact (+248) 2 743 244">
                <span class="hero-whatsapp-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                    <path
                      d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
                  </svg>
                </span>
                <span class="hero-whatsapp-tag">WhatsApp:</span>
                <span class="hero-whatsapp-num" style="color: var(--primary);">(+248) 2 743 244</span>
                <span class="hero-whatsapp-arrow" style="color: var(--primary);" aria-hidden="true">&rarr;</span>
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div class="footer-bottom">
        <div>&copy; 2026 SHIP CHANDLER MISURATA PORT CO., LTD. All rights reserved.</div>
      </div>
    </div>
  </footer>

  <!-- FLOATING WHATSAPP -->
  <a href="https://wa.me/2482743244" class="whatsapp-float" target="_blank" rel="noopener noreferrer"
    aria-label="WhatsApp Contact +248 2 743 244">
    <i class="fab fa-whatsapp"></i>
  </a>

  <script>
    // --- Port List Data for Dropdown (49 Ports) ---
    const ports = [
      "Ship Chandler Dar Es Salaam", "Ship Chandler Apapa", "Ship Chandler Onne Port Nigeria", "San Pedro Ship Supply Chandler",
      "Ship Chandler Abidjan", "Ship Chandler Freetown", "Monrovia Ship Chandler", "Ship Chandler Maputo", "Ship Chandler Matadi",
      "Ship Chandler Beira", "Ship Chandler Angola", "Ship Chandler Lobito", "ShipChandler Lome", "Shipchandler Lome",
      "Ivory Coast Ship Chandler", "Nouadhibou Ship Chandler", "Ship Chandler Luanda", "Ship Chandler Cape Verde",
      "Ship Chandler Gabon", "Ship Chandler Namibia", "Walvis Bay Ship Chandler", "Ship Chandler Gentil Port - Gabon",
      "Ship Chandler Takoradi", "Ship Chandler Congo", "Shipchandler Lagos", "Ship Chandler Port Ambon",
      "Shipchandler Pointe Noire", "Ship Chandler Djibouti", "Ship Chandler Cabinda", "Ship Chandler Tema",
      "Ship Chandler Mindelo", "Ship Chandler Casablanca", "Ship Chandler Safi Port Morocco", "Ship Chandler Kamsar",
      "Ship Chandler Soyo", "Dakar Ship Chandler", "Ship Chandler Senegal", "Ship Chandler Dakar", "Bissau Ship Chandler - Guinea",
      "Conakry Ship Chandler", "Ship Chandler Cotonou", "Douala Ship Chandler", "Liberia Ship Chandler", "Namibia Ship Chandler",
      "Ship Chandler Dakar", "Ship Chandler Mombasa", "Ship Chandlers Saldanha Bay", "Ship Chandler Owendo", "Ship Chandlers Richards Bay"
    ];

    // Populate Mega Menu
    const megaList = document.getElementById('mega-port-list');
    if (megaList) {
      const third = Math.ceil(ports.length / 3);
      const col1 = ports.slice(0, third);
      const col2 = ports.slice(third, third * 2);
      const col3 = ports.slice(third * 2);

      function createPortGroup(title, items) {
        const group = document.createElement('div');
        group.className = 'mega-group';
        group.innerHTML = `<h4>${title}</h4>`;
        items.forEach(port => {
          const a = document.createElement('a');
          a.href = `${port.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.html`;
          a.textContent = port;
          group.appendChild(a);
        });
        return group;
      }

      megaList.appendChild(createPortGroup('African Ports (A-D)', col1));
      megaList.appendChild(createPortGroup('African Ports (E-M)', col2));
      megaList.appendChild(createPortGroup('African Ports (N-Z)', col3));

      // Mega Menu Search
      const searchInput = document.getElementById('mega-port-search');
      if (searchInput) {
        searchInput.addEventListener('input', function (e) {
          const query = e.target.value.toLowerCase();
          const allLinks = megaList.querySelectorAll('a');
          const groups = megaList.querySelectorAll('.mega-group');

          allLinks.forEach(link => {
            const text = link.textContent.toLowerCase();
            link.style.display = text.includes(query) ? 'block' : 'none';
          });

          groups.forEach(group => {
            const hasVisible = Array.from(group.querySelectorAll('a')).some(a => a.style.display !== 'none');
            group.style.display = hasVisible ? 'block' : 'none';
          });
        });
      }
    }

    document.addEventListener('DOMContentLoaded', function () {
      // --- Sticky Header Effect ---
      const header = document.querySelector('.site-header');
      window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
          header.classList.add('scrolled');
        } else {
          header.classList.remove('scrolled');
        }
      });

      // --- Mobile Nav Toggle ---
      const navToggle = document.querySelector('.nav-toggle');
      const primaryNav = document.querySelector('.primary-nav');

      navToggle.addEventListener('click', function () {
        primaryNav.classList.toggle('open');
        this.classList.toggle('open');
        header.classList.toggle('menu-open');
      });

      // --- Mobile Dropdown Toggles ---
      const dropdownItems = document.querySelectorAll('.nav-item.has-dropdown, .nav-item.has-mega');
      dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        link.addEventListener('click', function (e) {
          if (window.innerWidth <= 1024) {
            e.preventDefault();
            item.classList.toggle('open');
          }
        });
      });

      // --- Smooth scroll for sidebar TOC ---
      document.querySelectorAll('.port-toc-list a').forEach(link => {
        link.addEventListener('click', function (e) {
          e.preventDefault();
          const target = document.querySelector(this.getAttribute('href'));
          if (target) {
            const offset = 100;
            const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({ top, behavior: 'smooth' });
          }
        });
      });

      // --- Scroll Reveal Animation ---
      const revealElements = document.querySelectorAll('.reveal');
      const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('active');
            revealObserver.unobserve(entry.target);
          }
        });
      }, {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
      });

      revealElements.forEach(el => revealObserver.observe(el));
    });
  </script>
</body>

</html>"""


def generate_page_html(page_name, h1, meta_title, meta_desc, full_desc, slug):
    """
    Constructs complete HTML for a port page matching the exact Bissau structure,
    centralized CSS, Misurata theme, SEO tags, schema markup, and clean footer (no drinks/snacks).
    """
    clean_port = get_clean_port_name(page_name)
    hero_title_html = format_hero_title(h1, page_name)
    rendered_article = render_article_html(full_desc)

    canonical_url = f"https://shipchandlermisurata.com/ports/{slug}"
    escaped_desc = html.escape(str(meta_desc).strip())
    escaped_title = html.escape(str(meta_title).strip())
    escaped_name = html.escape(str(page_name).strip())
    escaped_h1 = html.escape(str(h1).strip())
    keywords = f"{escaped_name}, ship chandler, ship supply, provisions, marine stores, bonded stores, deck stores, engine stores, vessel supply, marine procurement"

    # Build Schema.org JSON-LD structured data
    schema_data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": meta_title,
        "description": meta_desc,
        "url": canonical_url,
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": "https://shipchandlermisurata.com/"
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Ports",
                    "item": "https://shipchandlermisurata.com/#ports"
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": page_name,
                    "item": canonical_url
                }
            ]
        }
    }
    schema_json = json.dumps(schema_data, indent=4)

    page_html = HTML_TEMPLATE
    page_html = page_html.replace("__META_TITLE__", escaped_title)
    page_html = page_html.replace("__META_DESC__", escaped_desc)
    page_html = page_html.replace("__KEYWORDS__", keywords)
    page_html = page_html.replace("__CANONICAL_URL__", canonical_url)
    page_html = page_html.replace("__SCHEMA_JSON__", schema_json)
    page_html = page_html.replace("__HERO_ALT__", escaped_h1)
    page_html = page_html.replace("__PAGE_NAME__", escaped_name)
    page_html = page_html.replace("__HERO_TITLE__", hero_title_html)
    page_html = page_html.replace("__RENDERED_ARTICLE__", rendered_article)
    page_html = page_html.replace("__CLEAN_PORT__", clean_port)

    return page_html


def main():
    print(f"Reading Excel data from: {EXCEL_PATH}")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    sheet = wb['SEO Pages']

    # Step 1: Ensure CSS is centralized
    extract_and_centralize_css()

    rows = list(sheet.iter_rows(values_only=True))[1:]  # Skip header row
    print(f"Found {len(rows)} port rows in Excel.")

    generated_count = 0
    generated_files = []

    for row in rows:
        num, page_name, h1, meta_title, meta_desc, full_desc = row[:6]
        if not page_name:
            continue

        slug = re.sub(r'[^a-z0-9]+', '-', str(page_name).lower()).strip('-') + '.html'
        out_path = os.path.join(PORTS_DIR, slug)

        html_content = generate_page_html(
            page_name=page_name,
            h1=h1,
            meta_title=meta_title,
            meta_desc=meta_desc,
            full_desc=full_desc,
            slug=slug
        )

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        generated_count += 1
        generated_files.append((num, page_name, slug))
        print(f"[{num:02d}/49] Generated: {slug} ({page_name})")

    unique_files = len(set(f[2] for f in generated_files))
    print("\n" + "=" * 60)
    print(f"SUCCESS: Processed {generated_count} rows across {unique_files} unique port page files.")
    print(f"Centralized CSS written to: {CSS_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
