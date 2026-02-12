# AnimeWatchOrder.com

Static bilingual (EN/FR) anime watch order guide site. Built with pure HTML/CSS and a Python static site generator.

## Stack

- **Static HTML/CSS** — No JavaScript required
- **Python 3** — Build script generates pages from JSON data
- **Netlify** — Free hosting with automatic builds
- **Google Fonts** — Bebas Neue + Outfit

## Project Structure

```
animewatchorder.com/
├── index.html                  # Homepage EN
├── dragon-ball/
│   └── index.html              # Dragon Ball EN
├── fr/
│   ├── index.html              # Homepage FR
│   └── dragon-ball/
│       └── index.html          # Dragon Ball FR
├── assets/
│   └── css/
│       └── style.css           # Design system
├── data/
│   └── dragon-ball.json        # Dragon Ball data (EN + FR)
├── build.py                    # Static site generator
├── sitemap.xml                 # SEO sitemap with hreflang
├── robots.txt                  # Crawler directives
├── netlify.toml                # Netlify config
└── .gitignore
```

## Local Development

### Generate pages

```bash
python3 build.py
```

This reads JSON files from `data/` and generates all HTML pages for both languages.

### Preview locally

```bash
# Using Python's built-in server
python3 -m http.server 8000
# Then open http://localhost:8000
```

## Adding a New Series

1. Create `data/new-series.json` following the structure of `dragon-ball.json`
2. Add the slug to the `SERIES` list in `build.py`
3. Run `python3 build.py`

## Deployment on Netlify

1. Push this repo to GitHub
2. Connect the repo in Netlify
3. Netlify will run `python3 build.py` automatically on each push
4. Set publish directory to `.` (root)

The `netlify.toml` file handles build commands, redirects, and security headers.

## Affiliate Links

Replace `YOURAFFID` placeholders in `data/*.json` with your actual affiliate IDs:
- **Crunchyroll**: Update UTM parameters in streaming URLs
- **Amazon Associates**: Replace `?tag=YOURAFFID` with your Amazon tag

## SEO Features

- Bilingual hreflang tags (EN/FR + x-default)
- Schema.org HowTo + FAQPage structured data
- Semantic HTML with proper heading hierarchy
- XML sitemap with all URLs
- robots.txt

## License

All rights reserved.
