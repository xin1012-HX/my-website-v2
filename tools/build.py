#!/usr/bin/env python3
"""Build the static portfolio pages from centralized project and artwork data."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"


def esc(value: object, quote: bool = True) -> str:
    return html.escape(str(value), quote=quote)


def load_json(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


PROJECTS = load_json("projects.json")
ARTWORKS = load_json("artworks.json")
MANIFEST = load_json("image-manifest.json")


def asset_info(source_name: str) -> dict:
    try:
        return MANIFEST[source_name]
    except KeyError as error:
        raise SystemExit(f"Missing optimized asset for {source_name}") from error


def image(
    source_name: str,
    alt: str,
    *,
    class_name: str = "",
    loading: str = "lazy",
    fetchpriority: str = "auto",
) -> str:
    info = asset_info(source_name)
    attributes = [
        f'src="assets/images/{esc(info["file"])}"',
        f'alt="{esc(alt)}"',
        f'width="{info["width"]}"',
        f'height="{info["height"]}"',
        f'loading="{loading}"',
        'decoding="async"',
    ]
    if class_name:
        attributes.append(f'class="{esc(class_name)}"')
    if fetchpriority != "auto":
        attributes.append(f'fetchpriority="{fetchpriority}"')
    return f"<img {' '.join(attributes)}>"


def optimized_path(source_name: str) -> str:
    return f"assets/images/{esc(asset_info(source_name)['file'])}"


def header(current: str = "") -> str:
    def nav_link(label: str, href: str, key: str) -> str:
        marker = ' aria-current="page"' if current == key else ""
        return f'<a href="{href}"{marker}>{label}</a>'

    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <a class="site-brand" href="index.html" aria-label="Xin He portfolio home">
        {image('logo.png', '', loading='eager')}
        <span class="brand-lockup">
          <span class="brand-name">Xin He</span>
          <span class="brand-discipline">Architecture + Art</span>
        </span>
      </a>
      <button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="site-nav" data-menu-toggle><span></span></button>
      <nav class="site-nav" id="site-nav" aria-label="Primary navigation" data-navigation>
        {nav_link('Work', 'index.html#work', 'work')}
        {nav_link('About', 'index.html#about', 'about')}
        {nav_link('Art', 'art.html', 'art')}
        {nav_link('Contact', '#contact', 'contact')}
      </nav>
    </header>
    """


def footer() -> str:
    return """
    <footer class="site-footer" id="contact">
      <section class="footer-block">
        <h2>Start a conversation.</h2>
        <p>Architecture, spatial research, editorial work, and creative collaboration.</p>
      </section>
      <section class="footer-block">
        <h3>Contact</h3>
        <p><a href="mailto:26xhe@mvcds.org">26xhe@mvcds.org</a></p>
        <p>Toledo, Ohio · Beijing, China</p>
      </section>
      <section class="footer-block">
        <h3>Elsewhere</h3>
        <div class="footer-links">
          <a href="https://www.linkedin.com/in/xin-he-a198a2350/" target="_blank">LinkedIn</a>
          <a href="https://www.instagram.com/xin521iloveu/" target="_blank">Instagram</a>
          <a href="https://www.behance.net/xinhe53" target="_blank">Behance</a>
        </div>
        <p>© <span data-current-year>2026</span> Xin He.</p>
      </section>
    </footer>
    """


def page(
    *,
    title: str,
    description: str,
    content: str,
    current: str = "",
    page_path: str = "",
    base_url: str,
    json_ld: dict | None = None,
) -> str:
    canonical = f"{base_url.rstrip('/')}/{page_path}" if page_path else f"{base_url.rstrip('/')}/"
    structured = ""
    if json_ld:
        structured = (
            '<script type="application/ld+json">'
            + json.dumps(json_ld, ensure_ascii=False).replace("</", "<\\/")
            + "</script>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#050816">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="assets/images/favicon.png" type="image/png">
  <link rel="manifest" href="site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="assets/css/site.css?v=20260724-portrait">
  <link rel="stylesheet" href="assets/css/night.css?v=20260724-portrait">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(base_url.rstrip('/'))}/assets/images/og-night.png">
  <meta name="twitter:card" content="summary_large_image">
  {structured}
  <script defer src="assets/js/site.js?v=20260724-wordfit"></script>
</head>
<body>
  <div class="site-shell">
    {header(current)}
    <main id="main">
      {content}
    </main>
    {footer()}
  </div>
</body>
</html>
"""


def featured_card(project: dict) -> str:
    return f"""
    <a class="project-card" href="{esc(project['legacy_file'])}" data-reveal>
      <div class="project-card-media">{image(project['cover'], project['deck'])}</div>
      <div class="project-card-copy">
        <span class="project-number">{esc(project['index'])}</span>
        <div>
          <h3>{esc(project['title'])}</h3>
          <div class="project-card-meta">{esc(project['year'])} · {esc(project['category'])}</div>
        </div>
      </div>
    </a>
    """


def drawing_row(project: dict) -> str:
    return f"""
    <a class="drawing-row" href="{esc(project['legacy_file'])}">
      <span class="drawing-code">{esc(project['index'])}</span>
      <span class="drawing-title">{esc(project['title'])}</span>
      <span class="drawing-meta">{esc(project['year'])}</span>
      <span class="drawing-meta">{esc(project['category'])}</span>
      <span class="drawing-meta">View ↗</span>
      {image(project['cover'], '', class_name='drawing-preview')}
    </a>
    """


def build_index(base_url: str) -> None:
    hero = PROJECTS[0]
    featured = "".join(featured_card(project) for project in PROJECTS[:3])
    archive = "".join(drawing_row(project) for project in PROJECTS)
    teaser_indexes = (0, 8, 14)
    art_teasers = "".join(
        f"""
        <a class="art-tile" href="art.html#art-{index + 1}" data-reveal>
          {image(ARTWORKS[index]['src'], ARTWORKS[index]['alt'])}
          <span>{esc(ARTWORKS[index]['title'])}</span>
        </a>
        """
        for index in teaser_indexes
    )
    content = f"""
    <section class="hero" id="top">
      <div class="hero-copy">
        <div>
          <p class="eyebrow">Selected work · 2024—2026</p>
          <h1>Space as <em>care,</em> evidence & imagination.</h1>
        </div>
        <div class="hero-summary">
          <p>Xin (Louis) He works across social architecture, environmental systems, structural studies, and speculative worlds.</p>
          <a class="text-link" href="#work">Explore selected work</a>
        </div>
      </div>
      <a class="hero-visual" href="{esc(hero['legacy_file'])}" aria-label="View {esc(hero['title'])}">
        {image(hero['cover'], hero['deck'], loading='eager', fetchpriority='high')}
        <span class="hero-caption"><span>{esc(hero['title'])}</span><span>{esc(hero['category'])} · {esc(hero['year'])}</span></span>
      </a>
    </section>

    <section id="work">
      <div class="section-heading" data-reveal>
        <div>
          <p class="section-kicker">01 · Selected architecture</p>
          <h2>Three ways to make place.</h2>
        </div>
        <p>Care for vulnerable communities, connective civic infrastructure, and computational form each become a different method of architectural inquiry.</p>
      </div>
      <div class="featured-grid">{featured}</div>
    </section>

    <section id="archive">
      <div class="section-heading" data-reveal>
        <div>
          <p class="section-kicker">02 · Drawing register</p>
          <h2>Complete project index.</h2>
        </div>
        <p>Eight works spanning social space, morphology, tectonics, parametric design, editorial systems, and virtual environments.</p>
      </div>
      <div class="drawing-index">
        <div class="drawing-index-head"><span>Sheet</span><span>Project</span><span>Year</span><span>Discipline</span><span>Status</span></div>
        {archive}
      </div>
    </section>

    <section class="about-grid" id="about">
      <div class="about-portrait">{image('profile.jpg', 'Portrait of Xin Louis He')}</div>
      <div class="about-copy" data-reveal>
        <p class="section-kicker">03 · About the designer</p>
        <h2 class="about-title">Rigorous ideas, human consequences.</h2>
        <p>Xin (Louis) He is an incoming B.S. Architecture student at the University of Illinois Urbana-Champaign. His practice connects organic morphology, technological experimentation, public welfare, and visual storytelling.</p>
        <p>From conversations with shelter residents to parametric structures and virtual environments, each project asks how design decisions can become more legible, empathetic, and precise.</p>
        <div class="about-actions">
          <a class="button" href="assets/media/Xin_Louis_He_CV.pdf">View CV</a>
          <a class="button secondary" href="mailto:26xhe@mvcds.org">Email Xin</a>
        </div>
      </div>
    </section>

    <section class="art-teaser" id="art-preview">
      <div class="section-heading" data-reveal>
        <div>
          <p class="section-kicker">04 · Fine art</p>
          <h2>Atlas of Forced Evolution.</h2>
        </div>
        <div>
          <p>Fifteen sculptural studies examine how convenience, extraction, and infrastructure force vulnerable species to adapt.</p>
          <p><a class="text-link" href="art.html">Enter the full art atlas</a></p>
        </div>
      </div>
      <div class="art-strip">{art_teasers}</div>
    </section>
    """
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Xin (Louis) He",
        "url": f"{base_url.rstrip('/')}/",
        "jobTitle": "Architecture student and designer",
        "sameAs": [
            "https://www.linkedin.com/in/xin-he-a198a2350/",
            "https://www.behance.net/xinhe53",
        ],
    }
    (ROOT / "index.html").write_text(
        page(
            title="Xin He · Architecture + Art",
            description="Selected architecture, spatial research, environmental art, and virtual environments by Xin Louis He.",
            content=content,
            current="work",
            base_url=base_url,
            json_ld=person,
        ),
        encoding="utf-8",
    )


def gallery_figure(item: dict, number: int) -> str:
    wide = " wide" if item.get("wide") else ""
    full = optimized_path(item["src"])
    return f"""
    <figure class="gallery-figure{wide}" data-reveal>
      <button class="gallery-button" type="button" data-lightbox-src="{full}" data-lightbox-caption="{esc(item['caption'])}" aria-label="Enlarge {esc(item['caption'])}">
        {image(item['src'], item['alt'])}
      </button>
      <figcaption><span>{number:02d}</span><span>{esc(item['caption'])}</span></figcaption>
    </figure>
    """


def build_project(project: dict, next_project: dict, base_url: str) -> None:
    facts = (
        ("Year", project["year"]),
        ("Location / Field", project["location"]),
        ("Role", project["role"]),
        ("Recognition / Method", project["recognition"]),
    )
    fact_markup = "".join(
        f'<div class="project-fact"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'
        for label, value in facts
    )
    story_markup = "".join(f"<p>{esc(paragraph)}</p>" for paragraph in project["story"])
    gallery_items = [item for item in project["images"] if item["src"] != project["cover"]]
    gallery_markup = "".join(gallery_figure(item, index + 1) for index, item in enumerate(gallery_items))
    if project.get("video"):
        video = project["video"]
        gallery_markup += f"""
        <figure class="project-video" data-reveal>
          <video controls preload="metadata" poster="{optimized_path(project['cover'])}">
            <source src="assets/media/{esc(video['src'])}" type="video/mp4">
            Your browser does not support embedded video.
          </video>
          <figcaption>{esc(video['caption'])}</figcaption>
        </figure>
        """
    content = f"""
    <header class="project-hero">
      <div class="project-hero-copy">
        <div>
          <p class="eyebrow">{esc(project['index'])} · {esc(project['category'])}</p>
          <h1>{esc(project['title'])}</h1>
          <p class="project-deck">{esc(project['deck'])}</p>
        </div>
        <a class="text-link" href="index.html#archive">Back to drawing register</a>
      </div>
      <div class="project-hero-media">{image(project['cover'], project['deck'], loading='eager', fetchpriority='high')}</div>
    </header>
    <dl class="project-facts">{fact_markup}</dl>
    <section class="project-story">
      <h2>{esc(project['story_title'])}</h2>
      <div class="story-copy" data-reveal>{story_markup}</div>
    </section>
    <section class="project-gallery" aria-label="Project drawings and images">{gallery_markup}</section>
    <a class="next-project" href="{esc(next_project['legacy_file'])}">
      <span>Next project</span>
      <strong>{esc(next_project['title'])}</strong>
      <span>{esc(next_project['index'])} →</span>
    </a>
    """
    creative_work = {
        "@context": "https://schema.org",
        "@type": "CreativeWork",
        "name": project["title"],
        "creator": {"@type": "Person", "name": "Xin (Louis) He"},
        "dateCreated": project["year"],
        "description": project["deck"],
    }
    (ROOT / project["legacy_file"]).write_text(
        page(
            title=f"{project['title']} · Xin He",
            description=project["deck"],
            content=content,
            current="work",
            page_path=project["legacy_file"],
            base_url=base_url,
            json_ld=creative_work,
        ),
        encoding="utf-8",
    )


def build_art(base_url: str) -> None:
    cards = []
    for index, artwork in enumerate(ARTWORKS, start=1):
        full = optimized_path(artwork["src"])
        cards.append(
            f"""
            <article class="artwork-card" id="art-{index}" data-reveal>
              <button class="gallery-button" type="button" data-lightbox-src="{full}" data-lightbox-caption="{esc(artwork['title'])}" aria-label="Enlarge {esc(artwork['title'])}">
                {image(artwork['src'], artwork['alt'])}
              </button>
              <h2>{index:02d} · {esc(artwork['title'])}</h2>
              <p class="artwork-meta">{esc(artwork['dimensions'])}<br>{esc(artwork['materials'])}</p>
              <p class="artwork-description">{esc(artwork['description'])}</p>
            </article>
            """
        )
    content = f"""
    <header class="art-hero">
      <div>
        <p class="eyebrow">AP 3-D Art & Design · 15 works</p>
        <h1>Atlas of Forced Evolution.</h1>
      </div>
      <div class="art-hero-copy">
        <p><strong>What if animals had to evolve to survive human impact?</strong></p>
        <p>This sculptural matrix examines material progress and ecological damage. Each work pairs a vulnerable species with the infrastructure, consumption, entertainment, or waste that pressures its survival.</p>
        <a class="text-link" href="index.html#art-preview">Return to portfolio</a>
      </div>
    </header>
    <section class="art-grid" aria-label="Sculptural artwork catalogue">{''.join(cards)}</section>
    """
    (ROOT / "art.html").write_text(
        page(
            title="Atlas of Forced Evolution · Xin He",
            description="Fifteen sculptural studies by Xin He examining material progress, ecological damage, and vulnerable species.",
            content=content,
            current="art",
            page_path="art.html",
            base_url=base_url,
        ),
        encoding="utf-8",
    )


def build_404(base_url: str) -> None:
    content = """
    <section class="not-found">
      <div>
        <strong aria-hidden="true">404</strong>
        <h1>This drawing is not in the set.</h1>
        <p>The page may have moved, but the complete project register is still available.</p>
        <a class="button" href="index.html#archive">Return to project index</a>
      </div>
    </section>
    """
    (ROOT / "404.html").write_text(
        page(
            title="Page not found · Xin He",
            description="Return to the Xin He architecture and art portfolio.",
            content=content,
            page_path="404.html",
            base_url=base_url,
        ),
        encoding="utf-8",
    )


def build_discovery_files(base_url: str) -> None:
    base = base_url.rstrip("/")
    paths = ["", "art.html", *(project["legacy_file"] for project in PROJECTS)]
    urls = "\n".join(f"  <url><loc>{esc(base + '/' + path)}</loc></url>" for path in paths)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="https://xin1012-hx.github.io/my-website-v2",
        help="Public base URL used for canonical and social metadata",
    )
    args = parser.parse_args()
    build_index(args.base_url)
    for index, project in enumerate(PROJECTS):
        build_project(project, PROJECTS[(index + 1) % len(PROJECTS)], args.base_url)
    build_art(args.base_url)
    build_404(args.base_url)
    build_discovery_files(args.base_url)
    print(f"Built {len(PROJECTS) + 3} HTML pages.")


if __name__ == "__main__":
    main()
