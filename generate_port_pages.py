import os
import re
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
    clean = re.sub(r'\s*-\s*.*$', '', clean).strip()
    clean = re.sub(r'\s+', ' ', clean).strip()
    if 'port' not in clean.lower():
        clean += ' Port'
    return clean


def extract_and_centralize_css(bissau_html):
    """
    Extracts the inline CSS from bissau-ship-chandler-guinea.html, applies
    the footer theme color fixes (yellow logo text & yellow whatsapp text),
    and saves it to assets/css/port-pages.css.
    Replaces the <style>...</style> block with <link rel="stylesheet" href="../assets/css/port-pages.css">.
    """
    style_start = '<style>'
    style_end = '</style>'

    if style_start in bissau_html and style_end in bissau_html:
        p1 = bissau_html.find(style_start)
        p2 = bissau_html.find(style_end) + len(style_end)

        css_content = bissau_html[p1 + len(style_start) : bissau_html.find(style_end)].strip()

        # Ensure footer rules allow yellow logo text and WhatsApp text
        footer_replacement = """    .site-footer p,
    .site-footer a,
    .site-footer li,
    .site-footer h4,
    .site-footer div {
      color: #FFFFFF;
    }

    .site-footer .footer-brand .logo-text strong {
      color: #FFFFFF !important;
    }

    .site-footer .footer-brand .logo-text span {
      color: var(--primary) !important;
    }

    .site-footer .hero-whatsapp-tag {
      color: #25D366 !important;
    }

    .site-footer .hero-whatsapp-num,
    .site-footer .hero-whatsapp-arrow {
      color: var(--primary) !important;
    }"""

        # Replace overly broad white text rule if present
        css_content = re.sub(
            r'/\*\s*Force white text on all footer elements\s*\*/\s*\.site-footer\s+p,\s*\.site-footer\s+a,\s*\.site-footer\s+li,\s*\.site-footer\s+span,\s*\.site-footer\s+h4,\s*\.site-footer\s+strong,\s*\.site-footer\s+div\s*\{[^}]*\}',
            footer_replacement.strip(),
            css_content
        )

        os.makedirs(os.path.dirname(CSS_FILE), exist_ok=True)
        with open(CSS_FILE, 'w', encoding='utf-8') as f:
            f.write(css_content + '\n')

        print(f"[CSS] Extracted & centralized {len(css_content)} bytes of styles into {CSS_FILE}")

        # Replace inline <style> block with link tag
        link_tag = '  <!-- Centralized Port Pages CSS -->\n  <link rel="stylesheet" href="../assets/css/port-pages.css">'
        bissau_html = bissau_html[:p1] + link_tag + bissau_html[p2:]
    else:
        print("[CSS] Master template already links to external CSS.")

    return bissau_html


def render_article_html(desc_text):
    """
    Parses the Markdown description from Excel into semantic HTML
    matching the exact structure, pill-styled lists, drop-cap, and indentation of Bissau page.
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


def get_template_parts():
    """
    Extracts the master HTML shell from bissau-ship-chandler-guinea.html,
    centralizing the CSS into port-pages.css in the process.
    """
    bissau_path = os.path.join(PORTS_DIR, "bissau-ship-chandler-guinea.html")
    with open(bissau_path, 'r', encoding='utf-8') as f:
        master_html = f.read()

    master_html = extract_and_centralize_css(master_html)

    # Ensure footer WhatsApp number & arrow have the proper primary yellow style
    master_html = master_html.replace(
        '<span class="hero-whatsapp-num">(+248) 2 743 244</span>',
        '<span class="hero-whatsapp-num" style="color: var(--primary);">(+248) 2 743 244</span>'
    )
    master_html = master_html.replace(
        '<span class="hero-whatsapp-arrow" aria-hidden="true">&rarr;</span>',
        '<span class="hero-whatsapp-arrow" style="color: var(--primary);" aria-hidden="true">&rarr;</span>'
    )

    art_start_marker = '<article class="article-content reveal">\n'
    p1 = master_html.find(art_start_marker)
    if p1 == -1:
        # Try without newline
        p1 = master_html.find('<article class="article-content reveal">')
        if p1 != -1:
            p1 += len('<article class="article-content reveal">')
            if master_html[p1 : p1 + 1] == '\n':
                p1 += 1
    else:
        p1 += len(art_start_marker)

    cta_marker = '<!-- Article CTA -->'
    p2 = master_html.find(cta_marker)
    if p2 == -1:
        raise ValueError("Could not find '<!-- Article CTA -->' marker in bissau-ship-chandler-guinea.html")

    art_end_marker = '</article>'
    p3 = master_html.find(art_end_marker, p2)
    if p3 == -1:
        raise ValueError("Could not find '</article>' marker in bissau-ship-chandler-guinea.html")
    p3 += len(art_end_marker)

    head_part = master_html[:p1]
    tail_part = master_html[p3:]

    return head_part, tail_part


def generate_page_html(head_part, tail_part, page_name, h1, meta_title, meta_desc, full_desc, slug):
    """
    Generates complete HTML for a port page matching the exact Bissau structure and Tema theme.
    """
    orig_name = "Bissau Ship Chandler - Guinea"
    orig_title = "Bissau Ship Chandler - Guinea | Ship Supply, Provisions & Marine Stores"
    orig_desc = "Bissau Ship Chandler - Guinea provides professional ship supply, provisions, bonded stores, deck and engine stores, safety equipment, spare parts and marine procurement services."

    h = head_part

    # Replace Title
    h = h.replace(f"<title>{orig_title}</title>", f"<title>{meta_title}</title>")

    # Add canonical tag if not present
    canonical_tag = f'  <link rel="canonical" href="https://shipchandlertema.com/ports/{slug}">\n'
    og_url_tag = f'  <meta property="og:url" content="https://shipchandlertema.com/ports/{slug}">\n'

    if '<link rel="canonical"' not in h:
        h = h.replace('  <!-- Open Graph Meta Tags -->', f'{canonical_tag}\n  <!-- Open Graph Meta Tags -->')

    # Replace Meta Description and OG Description
    h = h.replace(f'content="{orig_desc}"', f'content="{meta_desc}"')

    # Replace OG Title
    h = h.replace(f'<meta property="og:title" content="{orig_title}">', f'<meta property="og:title" content="{meta_title}">\n{og_url_tag.rstrip()}')

    # Replace Hero image alt
    h = h.replace(f'alt="{orig_name}"', f'alt="{h1}"')

    # Replace Breadcrumb
    h = h.replace(f'<li>{orig_name}</li>', f'<li>{page_name}</li>')

    # Replace H1
    h = h.replace(f'<h1 class="hero-title">{orig_name}</h1>', f'<h1 class="hero-title">{h1}</h1>')

    # Replace Hero Description
    h = re.sub(
        r'<p class="hero-desc">[\s\S]*?</p>',
        f'<p class="hero-desc">{meta_desc}</p>',
        h,
        count=1
    )

    # Render article content from Excel description
    article_content = render_article_html(full_desc)

    clean_port = get_clean_port_name(page_name)
    article_cta = f"""
            <!-- Article CTA -->
            <div class="article-cta">
              <h3>Need Supply at {clean_port}?</h3>
              <p>Send us your complete vessel requisition and our team will respond with a competitive quotation.</p>
              <a href="../request-quote.html" class="btn btn-primary">Request a Quote <i
                  class="fas fa-arrow-right"></i></a>
            </div>
          </article>"""

    return h + article_content + article_cta + tail_part


def main():
    print(f"Reading Excel data from: {EXCEL_PATH}")
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    sheet = wb['SEO Pages']

    head_part, tail_part = get_template_parts()

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
            head_part=head_part,
            tail_part=tail_part,
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

    print("\n" + "="*60)
    print(f"SUCCESS: Processed {generated_count} rows across {len(set(f[2] for f in generated_files))} unique port page files.")
    print(f"Centralized CSS written to: {CSS_FILE}")
    print("="*60)


if __name__ == "__main__":
    main()
