#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SITE_ROOT.parents[1]
SOURCE_ROOT = WORKSPACE_ROOT / 'manamaths'
TARGET_ROOT = SITE_ROOT / 'manamaths'
TARGET_PDFS_ROOT = TARGET_ROOT / 'pdfs'

LEVEL_ORDER = ['foundation', 'proficient', 'excellence']
LEVEL_LABELS = {
    'foundation': 'Foundation',
    'proficient': 'Proficient',
    'excellence': 'Excellence',
}
LEVEL_DESCRIPTIONS = {
    'foundation': 'Direct practice and accessible first-step questions.',
    'proficient': 'More variety, more independence, and slightly harder recognition.',
    'excellence': 'Richer reasoning, comparison, and multi-step thinking.',
}


def title_from_slug(slug: str) -> str:
    title = slug
    if title.startswith('lo-yr9-'):
        title = title[len('lo-yr9-'):]
    return title.replace('-', ' ').title()


def collect_objectives() -> list[dict]:
    objectives: list[dict] = []
    for folder in sorted(SOURCE_ROOT.glob('lo-yr9-*')):
        if not folder.is_dir():
            continue

        pdfs = []
        for level in LEVEL_ORDER:
            source_pdf = folder / f'{level}-questions.pdf'
            if source_pdf.exists():
                pdfs.append(
                    {
                        'level': level,
                        'label': LEVEL_LABELS[level],
                        'description': LEVEL_DESCRIPTIONS[level],
                        'source_path': source_pdf,
                        'file_name': source_pdf.name,
                    }
                )

        if pdfs:
            objectives.append(
                {
                    'slug': folder.name,
                    'title': title_from_slug(folder.name),
                    'pdfs': pdfs,
                }
            )
    return objectives


def copy_pdfs(objectives: list[dict]) -> None:
    TARGET_PDFS_ROOT.mkdir(parents=True, exist_ok=True)

    live_slugs = {objective['slug'] for objective in objectives}
    for existing in TARGET_PDFS_ROOT.iterdir():
        if existing.is_dir() and existing.name not in live_slugs:
            shutil.rmtree(existing)

    for objective in objectives:
        objective_target = TARGET_PDFS_ROOT / objective['slug']
        objective_target.mkdir(parents=True, exist_ok=True)
        for pdf in objective['pdfs']:
            shutil.copy2(pdf['source_path'], objective_target / pdf['file_name'])


def render_index(objectives: list[dict]) -> str:
    objective_cards = []
    for objective in objectives:
        pdf_links = []
        for pdf in objective['pdfs']:
            href = f"/manamaths/pdfs/{objective['slug']}/{pdf['file_name']}"
            pdf_links.append(
                f'''<article class="card worksheet-card">
  <div class="worksheet-card-top">
    <p class="tier-label">{html.escape(pdf['label'])}</p>
    <a class="btn btn-secondary worksheet-link" href="{html.escape(href)}" target="_blank" rel="noopener">Open PDF</a>
  </div>
  <p>{html.escape(pdf['description'])}</p>
  <p class="small-note"><a href="{html.escape(href)}" target="_blank" rel="noopener">{html.escape(pdf['file_name'])}</a></p>
</article>'''
            )

        objective_cards.append(
            f'''<section class="section objective-section" id="{html.escape(objective['slug'])}">
  <div class="section-header section-header--narrow">
    <p class="eyebrow">Learning objective</p>
    <h2>{html.escape(objective['title'])}</h2>
    <p>Open the worksheet PDFs for this objective. Each file opens directly from the public site.</p>
  </div>
  <div class="grid grid-3 worksheet-grid">
    {''.join(pdf_links)}
  </div>
</section>'''
        )

    jump_links = ''.join(
        f'<a href="#{html.escape(objective["slug"])}">{html.escape(objective["title"])}</a>'
        for objective in objectives
    )

    objective_count = len(objectives)
    pdf_count = sum(len(objective['pdfs']) for objective in objectives)

    return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mana Maths worksheets | Review Fuel</title>
    <meta
      name="description"
      content="Public worksheet PDFs for Mana Maths, organised by learning objective."
    />
    <link rel="icon" href="/reviewfuelfav.ico" />
    <link rel="stylesheet" href="/styles.css" />
  </head>
  <body>
    <div id="header-slot"></div>
    <div class="wrap leads-page manamaths-page">
      <header>
        <div class="hero-layout hero-layout--split hero-layout--tight leads-hero">
          <div class="hero-stack hero-copy">
            <p class="hero-kicker">Mana Maths</p>
            <h1>Worksheet PDFs by learning objective.</h1>
            <p class="lead">
              Open the latest public worksheet PDFs for Mana Maths. Everything is grouped by learning objective so it is quick to find the right set.
            </p>
            <div class="hero-cta">
              <a class="btn" href="#objectives">Browse worksheets</a>
              <a class="btn btn-secondary" href="https://github.com/williammcintosh/manamaths" target="_blank" rel="noopener">View source repo</a>
            </div>
          </div>

          <div class="card leads-summary-card manamaths-summary-card">
            <div>
              <p class="eyebrow">Current library</p>
              <h2>Public PDF index</h2>
              <p>Each worksheet opens as a direct PDF file from this site.</p>
            </div>
            <div class="leads-summary-grid">
              <div class="summary-stat">
                <span class="summary-number">{objective_count}</span>
                <span class="summary-label">Learning objectives</span>
              </div>
              <div class="summary-stat">
                <span class="summary-number">{pdf_count}</span>
                <span class="summary-label">Worksheet PDFs</span>
              </div>
            </div>
            <div class="inline-links">
              {jump_links}
            </div>
          </div>
        </div>
      </header>

      <section class="section utility-section" id="objectives" aria-labelledby="worksheet-library">
        <div class="section-header section-header--narrow">
          <p class="eyebrow">Worksheet library</p>
          <h2 id="worksheet-library">Find a worksheet fast</h2>
          <p>Foundation, Proficient, and Excellence PDFs are listed under each objective.</p>
        </div>
      </section>

      {''.join(objective_cards)}
    </div>

    <script>
      const headerSlot = document.getElementById('header-slot');
      if (headerSlot) {{
        fetch('/partials/header.html')
          .then((r) => r.text())
          .then((html) => {{
            headerSlot.innerHTML = html;
            const headerEl = headerSlot.querySelector('.site-header');
            const toggle = headerSlot.querySelector('.header-toggle');
            if (headerEl && toggle) {{
              toggle.addEventListener('click', () => {{
                const isOpen = headerEl.classList.toggle('menu-open');
                toggle.setAttribute('aria-expanded', isOpen);
              }});
            }}
          }})
          .catch(() => {{}});
      }}
    </script>
  </body>
</html>
'''


def main() -> int:
    objectives = collect_objectives()
    if not objectives:
        raise SystemExit('No worksheet PDFs found in manamaths repo.')

    copy_pdfs(objectives)
    TARGET_ROOT.mkdir(parents=True, exist_ok=True)
    (TARGET_ROOT / 'index.html').write_text(render_index(objectives), encoding='utf-8')
    print(f'Synced {sum(len(o["pdfs"]) for o in objectives)} PDFs across {len(objectives)} learning objectives.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
