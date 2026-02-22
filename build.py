#!/usr/bin/env python3
"""
AnimeWatchOrder.com — Static Site Generator
Reads JSON data files from /data/ and generates bilingual HTML pages (EN + FR).
Usage: python3 build.py
"""

import json
import os
import sys
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SITE_URL = "https://animewatchorder.com"
CURRENT_YEAR = "2026"

# Google Tag Manager snippet
GTM_HEAD = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-TJ84SLJX');</script>
<!-- End Google Tag Manager -->"""

# Google Search Console verification
GOOGLE_SITE_VERIFICATION = '<meta name="google-site-verification" content="NC4herujRe5TMX77VnhqjvWdJa6XAwBd5iAVIGxwXbk" />'

# Series to generate (add new slugs here)
SERIES = ["dragon-ball", "naruto"]


def load_json(slug):
    """Load JSON data for a given series slug."""
    path = DATA_DIR / f"{slug}.json"
    if not path.exists():
        print(f"  [ERROR] Data file not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def badge_class(type_key):
    """Return CSS badge class for a given type."""
    mapping = {
        "canon": "badge--canon",
        "mixed": "badge--mixed",
        "film_canon": "badge--film-canon",
        "non_canon": "badge--non-canon",
        "filler": "badge--filler",
    }
    return mapping.get(type_key, "badge--canon")


def verdict_class(verdict):
    """Return CSS verdict class."""
    mapping = {
        "must_watch": "verdict--must-watch",
        "watchable": "verdict--watchable",
        "skip": "verdict--skip",
    }
    return mapping.get(verdict, "verdict--watchable")


def verdict_label(verdict, ui):
    """Return display label for a verdict."""
    mapping = {
        "must_watch": ui["must_watch"],
        "watchable": ui["watchable"],
        "skip": ui["skip"],
    }
    return mapping.get(verdict, verdict)


def type_label(type_key, ui):
    """Return display label for a type."""
    mapping = {
        "canon": ui["canon"],
        "mixed": ui["mixed"],
        "film_canon": ui["film_canon"],
        "non_canon": ui["non_canon"],
        "filler": ui.get("filler", "Filler"),
    }
    return mapping.get(type_key, type_key)


def build_timeline_rows(data, ui):
    """Generate HTML rows for the main timeline table."""
    rows = []
    for item in data["timeline"]:
        rec_tag = ""
        rec_class = ""
        if item.get("recommended"):
            rec_tag = f' <span class="tag-recommended">{ui["recommended_label"]}</span>'
            rec_class = ' class="row--recommended"'

        watch_url = item.get("watch_url", "#")
        row = f"""        <tr{rec_class}>
          <td class="col-num">{item['num']}</td>
          <td class="col-title">{item['title']}{rec_tag}<small>{item['subtitle']}</small></td>
          <td><span class="badge {badge_class(item['type'])}">{type_label(item['type'], ui)}</span></td>
          <td>{item['episodes']}</td>
          <td>{item['when']}</td>
          <td>{item['path']}</td>
          <td><span class="verdict {verdict_class(item['verdict'])}">{verdict_label(item['verdict'], ui)}</span></td>
          <td><a href="{watch_url}" class="stream-link" rel="nofollow noopener" target="_blank">CR</a></td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)


def build_films_rows(data, ui):
    """Generate HTML rows for the films table."""
    rows = []
    for film in data["films"]:
        canon_class = "film-canon-yes" if film["canon"] else "film-canon-no"
        canon_text = ui["yes"] if film["canon"] else ui["no"]
        v_class = verdict_class(film["verdict"])
        v_label = verdict_label(film["verdict"], ui)

        row = f"""        <tr>
          <td class="film-title">{film['title']}</td>
          <td>{film['year']}</td>
          <td class="{canon_class}">{canon_text}</td>
          <td>{film['placement']}</td>
          <td><span class="verdict {v_class}">{v_label}</span></td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)


def build_fillers_rows(data, ui):
    """Generate HTML rows for the fillers table."""
    rows = []
    for filler in data["fillers"]:
        v_class = verdict_class(filler["verdict"])
        v_label = verdict_label(filler["verdict"], ui)

        row = f"""        <tr>
          <td>{filler['arc']}</td>
          <td>{filler['episodes']}</td>
          <td><span class="verdict {v_class}">{v_label}</span></td>
          <td>{filler['notes']}</td>
        </tr>"""
        rows.append(row)
    return "\n".join(rows)


def build_paths_html(data, ui):
    """Generate HTML for the three watch path cards."""
    cards = []
    for path in data["paths"]:
        rec_badge = ""
        rec_class = ""
        if path.get("recommended"):
            rec_badge = f'<span class="path-card__badge">{ui["recommended_label"]}</span>'
            rec_class = " path-card--recommended"

        card = f"""      <div class="path-card{rec_class}">
        {rec_badge}
        <span class="path-card__icon">{path['icon']}</span>
        <div class="path-card__name">{path['name']}</div>
        <div class="path-card__subtitle">{path['subtitle']}</div>
        <p class="path-card__desc">{path['description']}</p>
        <div class="path-card__meta">
          <span class="path-card__hours">{path['hours']}</span>
          {path['includes']}
        </div>
      </div>"""
        cards.append(card)
    return "\n".join(cards)


def build_faq_html(data):
    """Generate HTML for FAQ section."""
    items = []
    for faq in data["faq"]:
        item = f"""      <div class="faq-item">
        <h3>{faq['question']}</h3>
        <p>{faq['answer']}</p>
      </div>"""
        items.append(item)
    return "\n".join(items)


def build_why_confusing_html(data, ui):
    """Generate HTML for the 'Why Dragon Ball Is Confusing' info box."""
    wc = data["why_confusing"]
    return f"""      <div class="info-box">
        <div class="info-box__label">{ui['why_confusing_label']}</div>
        <div class="info-box__text">{wc['content']}</div>
      </div>"""


def build_compare_html(data, ui):
    """Generate HTML for the DBZ vs Kai comparison grid + verdict."""
    compare = data["dbz_vs_kai"]
    cards = []
    for card in compare["cards"]:
        rec_badge = ""
        if card.get("recommended"):
            rec_badge = f'<span class="winner-tag">{ui["recommended_label"]}</span>'

        stats_html = ""
        for stat in card["stats"]:
            stats_html += f"""          <div class="compare-card__stat">
            <span class="compare-card__label">{stat['label']}</span>
            <span class="compare-card__value">{stat['value']}</span>
          </div>\n"""

        card_html = f"""      <div class="compare-card {card.get('color_class', '')}">
        {rec_badge}
        <div class="compare-card__title">{card['title']}</div>
        <div class="compare-card__subtitle">{card['subtitle']}</div>
{stats_html}      </div>"""
        cards.append(card_html)

    grid = f"""      <div class="compare-grid">
{chr(10).join(cards)}
      </div>"""

    verdict = f"""      <div class="verdict-box">
        <div class="verdict-box__label">{ui.get('compare_verdict_label', 'Our Verdict')}</div>
        <p class="verdict-box__text">{compare['verdict']}</p>
      </div>"""

    return grid + "\n" + verdict


def build_streaming_html(data, ui):
    """Generate HTML for streaming platform cards."""
    cards = []
    for i, s in enumerate(data["streaming"]):
        available_items = "\n".join(
            [f'            <li>{item}</li>' for item in s["available"]]
        )
        cta_class = "streaming-card__cta--primary" if i == 0 else ""

        card = f"""      <div class="streaming-card">
        <span class="streaming-card__icon">{s['icon']}</span>
        <div class="streaming-card__name">{s['platform']}</div>
        <ul class="streaming-card__list">
{available_items}
        </ul>
        <a href="{s['url']}" class="streaming-card__cta {cta_class}" target="_blank" rel="noopener noreferrer nofollow">{s['cta']}</a>
      </div>"""
        cards.append(card)
    return "\n".join(cards)


def build_schema_json(data, slug, lang):
    """Generate Schema.org HowTo JSON-LD."""
    url = f"{SITE_URL}/{slug}/" if lang == "en" else f"{SITE_URL}/fr/{slug}/"
    schema = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"{data['title']} Watch Order Guide" if lang == "en" else f"{data['title']} Guide d'Ordre de Visionnage",
        "description": data["meta_description"],
        "url": url,
        "datePublished": "2026-02-12",
        "dateModified": "2026-02-12",
        "step": [],
    }
    for item in data["timeline"]:
        step = {
            "@type": "HowToStep",
            "name": item["title"],
            "text": item.get("notes", ""),
        }
        schema["step"].append(step)
    return json.dumps(schema, indent=2, ensure_ascii=False)


def build_faq_schema(data):
    """Generate Schema.org FAQPage JSON-LD."""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [],
    }
    for faq in data["faq"]:
        entity = {
            "@type": "Question",
            "name": faq["question"],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq["answer"],
            },
        }
        schema["mainEntity"].append(entity)
    return json.dumps(schema, indent=2, ensure_ascii=False)


def generate_series_page(slug, data, lang):
    """Generate a full series page HTML."""
    ui = data["ui"]
    lang_prefix = "/fr" if lang == "fr" else ""
    other_lang = "fr" if lang == "en" else "en"
    other_prefix = "/fr" if other_lang == "fr" else ""
    home_url = f"{lang_prefix}/"
    lang_switch_url = f"{other_prefix}/{slug}/"

    # Build all sections
    why_confusing_html = build_why_confusing_html(data, ui)
    paths_html = build_paths_html(data, ui)
    compare_html = build_compare_html(data, ui)
    timeline_rows = build_timeline_rows(data, ui)
    faq_html = build_faq_html(data)
    streaming_html = build_streaming_html(data, ui)
    howto_schema = build_schema_json(data, slug, lang)
    faq_schema = build_faq_schema(data)

    canonical = f"{SITE_URL}/{slug}/" if lang == "en" else f"{SITE_URL}/fr/{slug}/"
    en_url = f"{SITE_URL}/{slug}/"
    fr_url = f"{SITE_URL}/fr/{slug}/"

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  {GTM_HEAD}
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data['meta_title']}</title>
  <meta name="description" content="{data['meta_description']}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="fr" href="{fr_url}">
  <link rel="alternate" hreflang="x-default" href="{en_url}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <script type="application/ld+json">
{howto_schema}
  </script>
  <script type="application/ld+json">
{faq_schema}
  </script>
</head>
<body>
  <!-- Navigation -->
  <nav class="nav" aria-label="Main navigation">
    <div class="container nav__inner">
      <a href="{home_url}" class="nav__logo">Anime<span>Watch</span>Order</a>
      <ul class="nav__links">
        <li><a href="{home_url}">{ui['nav_home']}</a></li>
        <li><a href="{lang_switch_url}" class="nav__lang">{ui['lang_switch']}</a></li>
      </ul>
    </div>
  </nav>

  <main class="container">
    <!-- 1. Hero Section -->
    <section class="hero" id="hero">
      <span class="hero__tag">{data['category_tag']}</span>
      <h1>{data['title']} {"Watch Order" if lang == "en" else "Ordre de Visionnage"}</h1>
      <div class="hero__meta">
        <div class="hero__meta-item">
          <span class="hero__meta-value">{data['hero']['series']}</span>
          <span class="hero__meta-label">{"Series" if lang == "en" else "Séries"}</span>
        </div>
        <div class="hero__meta-item">
          <span class="hero__meta-value">{data['hero']['films']}</span>
          <span class="hero__meta-label">Films</span>
        </div>
        <div class="hero__meta-item">
          <span class="hero__meta-value">{data['hero']['hours']}+</span>
          <span class="hero__meta-label">{"Hours" if lang == "en" else "Heures"}</span>
        </div>
        <div class="hero__meta-item">
          <span class="hero__meta-value">{data['hero']['updated']}</span>
          <span class="hero__meta-label">{"Updated" if lang == "en" else "Mis à jour"}</span>
        </div>
      </div>
      <p class="hero__intro">{data['intro']}</p>
    </section>

    <!-- 2. Quick Answer Box -->
    <section class="section" id="quick-answer">
      <div class="quick-answer">
        <div class="quick-answer__label">{ui['quick_answer_label']}</div>
        <p class="quick-answer__text">{data['quick_answer']}</p>
      </div>
    </section>

    <!-- 3. Why Dragon Ball Is Confusing -->
    <section class="section" id="why-confusing">
{why_confusing_html}
    </section>

    <!-- 4. Watch Paths -->
    <section class="section" id="paths">
      <h2>{ui['paths_heading']}</h2>
      <div class="paths-grid">
{paths_html}
      </div>
    </section>

    <!-- 5. DBZ vs Kai Comparison -->
    <section class="section" id="compare">
      <h2>{data['dbz_vs_kai']['heading']}</h2>
      <p class="section__intro">{data['dbz_vs_kai']['intro']}</p>
{compare_html}
    </section>

    <!-- 6. Complete Dragon Ball Timeline -->
    <section class="section" id="timeline">
      <h2>{ui['timeline_heading']}</h2>
      <div class="table-wrapper">
        <table class="timeline-table">
          <thead>
            <tr>
              <th>{ui['col_num']}</th>
              <th>{ui['col_title']}</th>
              <th>{ui['col_type']}</th>
              <th>{ui['col_episodes']}</th>
              <th>{ui['col_when']}</th>
              <th>{ui['col_path']}</th>
              <th>{ui['col_verdict']}</th>
              <th>{ui['col_watch']}</th>
            </tr>
          </thead>
          <tbody>
{timeline_rows}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 7. FAQ Section -->
    <section class="section" id="faq">
      <h2>{ui['faq_heading']}</h2>
{faq_html}
    </section>

    <!-- 8. Streaming Platforms -->
    <section class="section" id="streaming">
      <h2>{ui['streaming_heading']}</h2>
      <div class="streaming-grid">
{streaming_html}
      </div>
    </section>

    <!-- 9. Manga Continuation Box -->
    <section class="section" id="manga">
      <div class="manga-box">
        <span class="manga-box__icon">📚</span>
        <div class="manga-box__title">{data['manga']['title']}</div>
        <p class="manga-box__desc">{data['manga']['description']}</p>
        <a href="{data['manga']['link_url']}" class="manga-box__link" target="_blank" rel="noopener noreferrer nofollow">→ {data['manga']['link_text']}</a>
      </div>
    </section>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p class="footer__text">{ui['footer_text']}</p>
      <p class="footer__affiliate">{ui['footer_affiliate']}</p>
    </div>
  </footer>
</body>
</html>"""
    return html


def generate_homepage(lang, series_list):
    """Generate the homepage HTML for a given language."""
    lang_prefix = "/fr" if lang == "fr" else ""
    other_prefix = "/fr" if lang == "en" else ""
    other_lang_label = "FR" if lang == "en" else "EN"
    other_home = f"{other_prefix}/"
    home_url = f"{lang_prefix}/"

    canonical = SITE_URL + "/" if lang == "en" else f"{SITE_URL}/fr/"
    en_url = f"{SITE_URL}/"
    fr_url = f"{SITE_URL}/fr/"

    if lang == "en":
        title = "AnimeWatchOrder.com — Complete Anime Watch Order Guides"
        description = "Clear, structured watch order guides for the most complex anime franchises. Dragon Ball, Naruto, One Piece, and more."
        h1_text = "Anime Watch Order Guides"
        subtitle = "Clear, structured watch order guides for the most complex anime franchises."
        nav_home = "Home"
        cta_text = "View Guide"
    else:
        title = "AnimeWatchOrder.com — Guides d'Ordre de Visionnage Anime"
        description = "Des guides clairs et structurés pour les franchises anime les plus complexes. Dragon Ball, Naruto, One Piece et plus."
        h1_text = "Guides d'Ordre de Visionnage Anime"
        subtitle = "Des guides clairs et structurés pour les franchises anime les plus complexes."
        nav_home = "Accueil"
        cta_text = "Voir le Guide"

    # Build series cards
    cards_html = ""
    for s in series_list:
        slug = s["slug"]
        d = s["data"][lang]
        link = f"{lang_prefix}/{slug}/"
        emoji = d.get("emoji", "🎬")
        cards_html += f"""      <a href="{link}" class="series-card">
        <span class="series-card__emoji">{emoji}</span>
        <div class="series-card__title">{d['title']}</div>
        <div class="series-card__meta">{d['category_tag']}</div>
        <span class="series-card__cta">{cta_text} →</span>
      </a>
"""

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  {GTM_HEAD}
  {GOOGLE_SITE_VERIFICATION}
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="en" href="{en_url}">
  <link rel="alternate" hreflang="fr" href="{fr_url}">
  <link rel="alternate" hreflang="x-default" href="{en_url}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
  <!-- Navigation -->
  <nav class="nav" aria-label="Main navigation">
    <div class="container nav__inner">
      <a href="{home_url}" class="nav__logo">Anime<span>Watch</span>Order</a>
      <ul class="nav__links">
        <li><a href="{home_url}">{nav_home}</a></li>
        <li><a href="{other_home}" class="nav__lang">{other_lang_label}</a></li>
      </ul>
    </div>
  </nav>

  <main class="container">
    <section class="home-hero">
      <h1>{h1_text}</h1>
      <p class="home-hero__subtitle">{subtitle}</p>
      <div class="series-grid">
{cards_html}
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="container">
      <p class="footer__text">AnimeWatchOrder.com</p>
    </div>
  </footer>
</body>
</html>"""
    return html


def generate_sitemap(series_slugs):
    """Generate sitemap.xml with hreflang annotations."""
    urls = []

    # Homepage
    urls.append({
        "loc_en": f"{SITE_URL}/",
        "loc_fr": f"{SITE_URL}/fr/",
    })

    # Series pages
    for slug in series_slugs:
        urls.append({
            "loc_en": f"{SITE_URL}/{slug}/",
            "loc_fr": f"{SITE_URL}/fr/{slug}/",
        })

    entries = []
    for url in urls:
        entry = f"""  <url>
    <loc>{url['loc_en']}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{url['loc_en']}"/>
    <xhtml:link rel="alternate" hreflang="fr" href="{url['loc_fr']}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{url['loc_en']}"/>
    <lastmod>2026-02-12</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{url['loc_fr']}</loc>
    <xhtml:link rel="alternate" hreflang="en" href="{url['loc_en']}"/>
    <xhtml:link rel="alternate" hreflang="fr" href="{url['loc_fr']}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{url['loc_en']}"/>
    <lastmod>2026-02-12</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>"""
        entries.append(entry)

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(entries)}
</urlset>"""
    return sitemap


def write_file(path, content):
    """Write content to a file, creating directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {path.relative_to(BASE_DIR)}")


def main():
    print("=" * 60)
    print("AnimeWatchOrder.com — Static Site Generator")
    print("=" * 60)

    # Load all series data
    series_list = []
    for slug in SERIES:
        print(f"\n[1/4] Loading data: {slug}")
        raw = load_json(slug)
        series_list.append({"slug": slug, "data": {"en": raw["en"], "fr": raw["fr"]}})

    # Generate series pages
    print("\n[2/4] Generating series pages...")
    for s in series_list:
        slug = s["slug"]
        for lang in ["en", "fr"]:
            data = s["data"][lang]
            html = generate_series_page(slug, data, lang)
            if lang == "en":
                out_path = BASE_DIR / slug / "index.html"
            else:
                out_path = BASE_DIR / "fr" / slug / "index.html"
            write_file(out_path, html)

    # Generate homepages
    print("\n[3/4] Generating homepages...")
    for lang in ["en", "fr"]:
        html = generate_homepage(lang, series_list)
        if lang == "en":
            out_path = BASE_DIR / "index.html"
        else:
            out_path = BASE_DIR / "fr" / "index.html"
        write_file(out_path, html)

    # Generate sitemap
    print("\n[4/4] Generating sitemap...")
    sitemap = generate_sitemap(SERIES)
    write_file(BASE_DIR / "sitemap.xml", sitemap)

    print("\n" + "=" * 60)
    print(f"Build complete! Generated {len(SERIES) * 2} series pages + 2 homepages.")
    print("=" * 60)


if __name__ == "__main__":
    main()
