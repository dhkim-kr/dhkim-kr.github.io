# Dae Hyeon Kim / Research profile

Research profile and project portfolio at [dhkim-kr.github.io](https://dhkim-kr.github.io/).

The site contains Korean and English pages, 13 project details and 33 publication or manuscript details, including 13 domestic conference papers. Research figures and evaluation conditions are based on the September 2026 portfolio, original papers and linked research repositories. Journal articles, international conferences, domestic conferences, manuscripts under review and work in preparation are listed separately.

## Update content

- `content/projects.json`: project metadata, figures, original numerical tables and chart values.
- `content/publications.json`: paper titles, venues, status, authorship roles, DOI and repository links.
- `content/editorial.json`: English project descriptions and bilingual paper summaries.
- `content/table-translations.json`: English labels for source tables and charts.
- `content/figure-sources.json`: source notes for research figures.
- `assets/site.css`: shared white and blue design, including responsive styles.

Generate the committed static HTML with Python 3.10 or later:

```bash
python scripts/build.py
python scripts/check.py
python -m http.server 8765
```

No third-party build dependencies or client-side framework are required. Commit both source changes and generated HTML. GitHub Pages serves the root of the `Master` branch; `.nojekyll` enables direct static serving. Detail routes contain an `index.html` so direct links and reloads work without a router fallback.

## Content and assets

Research figures retain the content of the original portfolio or research repository. Paper figures and datasets retain their respective copyrights and licenses. Links to public research repositories do not imply that every dataset, training checkpoint or clinical evaluation is publicly released. Manuscript status is recorded as of September 8, 2026.
