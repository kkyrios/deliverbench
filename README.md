# DeliverBench project homepage

A static research showcase for DeliverBench: benchmark overview, results, delivery cases, construction, evaluation, and project coverage.

**Website:** https://kkyrios.github.io/deliverbench/

**Affiliations:** Humanlaya Data · [Theseus Lab](https://theseus-labs-rsi.github.io/)

## Local preview

Python 3.10+ builds the site with the standard library. Node.js is only needed for the JavaScript syntax check.

```sh
python3 scripts/build.py
python3 scripts/verify.py
node --check dist/app.js
python3 -m http.server 8766 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8766/. The build recreates `dist/`; edit the source files instead.

## Updating content

- `src/index.template.html`: page copy, evidence summaries, figure captions, and reporting details.
- `src/styles.css` and `src/app.js`: navy/gray layout and progressively enhanced interactions. The single leaderboard combines model identity, logos, both metric bars, and exact values. Sorting also changes which metric is visually emphasized.
- `data/results.json`: the reviewed 14 October 2026 reporting snapshot, including the 7-system leaderboard and 77 final-delivery scores. Charts and tables share this data.
- `data/projects.json`: public descriptions of the 11 projects.
- `assets/`: approved presentation figures, a site icon, share preview, and self-hosted fonts. `assets/models/` contains the supplied model logos. `assets/cases/` contains four crops exported from the supplied case-study slide, with the slide's content and styling preserved.
- `site.json`: the canonical public URL and share-image base.

The numerical checks recompute leaderboard means from the project matrix and checkpoint pass rates from the 150-subtask denominator. They also check local links and the publication boundary. Browser checks are still needed after visual or interaction changes.

## Deployment and future migration

GitHub Actions builds, verifies, and deploys `dist/` to GitHub Pages on pushes to `main`. Enable **Settings → Pages → Source: GitHub Actions** for the repository.

To move to an organization repository, update `site.json`, this README's website link, and the repository's homepage setting; enable Pages in the destination. Page assets use relative paths, so they work under a project subpath or a root domain. No backend, secrets, or account system is required.

## Publication scope and attribution

This repository contains the showcase website and display data. It does not publish the benchmark task packages, complete paper, private source documents, or native execution traces. Displayed scores use the reporting specification described on the site; checkpoint scores and final-package scores have different scopes.

The page is an original implementation informed by the organization of [StartupBench](https://startupbench.github.io/) and [ProfessionalBench](https://professionalbench.github.io/). No code or brand assets were copied from those sites. DeliverBench figures and research content remain their authors' materials; no broader dataset or figure reuse license is granted here.

DM Sans is self-hosted under the [SIL Open Font License](assets/fonts/OFL.txt).
