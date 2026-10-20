#!/usr/bin/env python3
"""Build the static site from the reviewed reporting snapshot. Standard library only."""
from pathlib import Path
from html import escape
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/results.json').read_text())
SYSTEMS = DATA['systems']
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
SITE = json.loads((ROOT / 'site.json').read_text())
DIST = ROOT / 'dist'
# dist/ is generated output, never an input. Remove stale assets on every build.
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir(exist_ok=True)
logos = {model: f'{model}.png' for model in ['claude', 'gpt', 'kimi', 'glm', 'gemini']}
logos.update({'deepseek': 'deepseek-color.svg', 'qwen': 'qwen-color.svg'})

def metric_cell(row, key, label, suffix=''):
    return f'''<td class="metric-cell metric-{key}">
      <span class="mobile-metric-label">{label}</span>
      <div class="metric-visual"><span class="metric-track" aria-hidden="true"><span class="metric-fill" style="--value:{row[key]:.6f}%"></span></span>
      <span class="metric-value">{row[key]:.2f}{suffix}</span></div>
    </td>'''

leaderboard=[]
process=[]
for index,row in enumerate(SYSTEMS):
    leaderboard.append(f'''<tr data-system="{row['id']}" data-final="{row['final']}" data-pass="{row['pass_rate']}">
      <td class="rank">{index+1:02d}</td>
      <th scope="row" class="model-cell"><div class="system-cell"><span class="model-logo"><img src="assets/models/{logos[row['id']]}" alt="" width="34" height="34"></span><span class="system-name">{escape(row['name'])}<span class="system-harness">{escape(row['harness'])}</span></span></div></th>
      {metric_cell(row, 'final', 'Final delivery')}
      {metric_cell(row, 'pass_rate', 'Subtask pass rate', '%')}
    </tr>''')
    process.append(f'<tr><td>{escape(row["name"])}</td><td class="number">{row["process"]:.2f}</td><td class="number">{row["final"]:.2f}</td></tr>')
matrix=[]
for project in DATA['final_matrix']:
    cells=''.join(f'<td class="{"gate" if project[row["id"]]==0 else ""}">{project[row["id"]]:.2f}</td>' for row in SYSTEMS)
    matrix.append(f'<tr><td>{project["project"]}</td>{cells}</tr>')
projects=[]
for p in PROJECTS:
    projects.append(f'<article class="project-row"><span class="project-id">{p["id"]}</span><div><h3 class="project-title">{escape(p["title"])}</h3><p class="project-meta">{p["domain"]} · {p["subtasks"]} subtasks</p></div><p>{escape(p["description"])}</p></article>')
replacements = {'LEADERBOARD':''.join(leaderboard),'PROCESS_TABLE':''.join(process),'MATRIX_HEADERS':''.join(f'<th scope="col" class="number">{row["id"].capitalize() if row["id"] != "gpt" else "GPT"}</th>' for row in SYSTEMS),'MATRIX':''.join(matrix),'PROJECTS':''.join(projects)}
html=(ROOT/'src/index.template.html').read_text()
replacements['SITE_URL'] = escape(SITE['url'].rstrip('/') + '/', quote=True)
for key,value in replacements.items(): html=html.replace('{{'+key+'}}',value)
assert '{{' not in html, 'Unresolved template placeholder'
(DIST/'index.html').write_text(html)
for file in ['styles.css','app.js']: shutil.copyfile(ROOT/'src'/file,DIST/file)
shutil.copytree(ROOT/'assets',DIST/'assets',dirs_exist_ok=True)
# Only display data, never task packages, rubric details, or private source files.
shutil.copytree(ROOT/'data',DIST/'data',dirs_exist_ok=True)
(DIST/'.nojekyll').touch()
print(f'Built {len(SYSTEMS)} systems, {len(PROJECTS)} projects, {sum(p["subtasks"] for p in PROJECTS)} subtasks → dist/')
