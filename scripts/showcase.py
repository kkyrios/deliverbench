"""Render the public P02 example; no task-package files enter the site build."""
from html import escape as esc


def render_showcase(data):
    tasks = {task['id']: task for task in data['tasks']}
    nodes = {**tasks, 'LENDER': data['feedback']}
    edges = data['edges']

    def links(node_id, direction):
        ids = [e['from' if direction == 'in' else 'to'] for e in edges
               if e['to' if direction == 'in' else 'from'] == node_id]
        return ''.join(
            '<span class="dependency-final">Final package</span>' if i == 'FINAL' else
            f'<a href="#p02-{i}" data-project-select="{i}" title="{esc(nodes[i]["label"], quote=True)}">'
            f'{esc(i if i != "LENDER" else "Lender questions")}</a>' for i in ids)

    def task_html(t):
        return f'''<article class="project-task" id="p02-{t['id']}" data-project-node="{t['id']}" style="--node-y:{t['y']}px">
          <button type="button" class="project-task-button" data-project-select="{t['id']}" aria-pressed="false" aria-controls="project-detail" disabled>
            <span class="task-number">{t['id']}<span class="checkpoint-dot" aria-hidden="true"></span></span><span class="task-name">{esc(t['label'])}</span>
          </button>
          <div class="task-mobile-detail"><p><strong>Uses earlier work</strong>{esc(t['uses'])}</p><p><strong>Produces</strong>{esc(t['produces'])}</p></div>
          <div class="task-dependencies"><span>From</span><div>{links(t['id'], 'in') or '<span class="dependency-source">Source materials</span>'}</div><span>To</span><div>{links(t['id'], 'out')}</div></div>
        </article>'''

    phases = []
    for p in data['phases']:
        phases.append(f'''<section class="project-phase" aria-labelledby="phase-{p['id']}" style="--phase-x:{(16 + (p['id']-1)*290)/1120*100:.6f}%">
          <header><span class="phase-index">0{p['id']}</span><h4 id="phase-{p['id']}">{esc(p['title'])}</h4><p class="phase-input">{esc(p['inputs'])}</p></header>
          <div class="phase-tasks">{'FEEDBACK_NODE_PLACEHOLDER' if p['id']==4 else ''}{''.join(task_html(t) for t in data['tasks'] if t['phase']==p['id'])}</div>
        </section>''')

    # Long connections travel through the margins, rather than across task labels.
    paths = []
    long_index = 0
    for e in edges:
        a = nodes[e['from']]
        if e['to'] == 'FINAL':
            x = a['x'] + 105
            path = f'M {x} {a["y"]+96} V 656'
        else:
            b = nodes[e['to']]
            ay = a['y'] + (35 if e['from'] == 'LENDER' else 48)
            by = b['y'] + (35 if e['to'] == 'LENDER' else 48)
            if a['x'] == b['x'] and b['y']-a['y'] <= 210:
                path = f'M {a["x"]+105} {a["y"]+(70 if e["from"]=="LENDER" else 96)} V {b["y"]-4}'
            elif e['kind'] == 'feedback':
                lane = 8 + (['T05','T07','T10'].index(e['from'])) * 10
                sx, tx = a['x']+222, b['x']-18
                path = f'M {a["x"]+210} {ay} H {sx} V {lane} H {tx} V {by} H {b["x"]-4}'
            elif a['x'] == b['x']:
                x = a['x']+232
                path = f'M {a["x"]+210} {ay} H {x} V {by} H {b["x"]+214}'
            elif b['x']-a['x'] > 300 or e['kind'] == 'context':
                lane = 602 + (long_index % 6) * 7
                offset = (long_index % 3) * 7
                long_index += 1
                sx,tx = a['x']+224+offset,b['x']-24-offset
                path = f'M {a["x"]+210} {ay} H {sx} V {lane} H {tx} V {by} H {b["x"]-4}'
            else:
                sx,tx=a['x']+210,b['x']-4
                path=f'M {sx} {ay} C {sx+36} {ay}, {tx-36} {by}, {tx} {by}'
        paths.append(f'<path d="{path}" class="project-edge edge-{e["kind"]}" data-from="{e["from"]}" data-to="{e["to"]}" marker-end="url(#arrow-{e["kind"]})"/>')
    markers = ''.join(f'<marker id="arrow-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>'
                      for kind,color in [('artifact','#2d598a'),('context','#8b9caf'),('feedback','#a28447')])
    feedback = data['feedback']
    feedback_html = f'''<aside class="project-feedback" id="p02-LENDER" data-project-node="LENDER">
      <button type="button" data-project-select="LENDER" aria-pressed="false" aria-controls="project-detail" disabled><span>Business feedback</span>{esc(feedback['label'])}</button>
      <div class="feedback-description">Based on the agent’s T05, T07 and T10 submissions; addressed in T11.</div>
    </aside>'''
    outputs = ''.join(f'<li data-output-source="{d["from"]}"><span aria-hidden="true">▤</span>{esc(d["label"])}</li>' for d in data['deliverables'])
    checkpoints = ''.join(f'<a href="#p02-{t["id"]}" data-project-select="{t["id"]}" aria-label="Explore {t["id"]}: {esc(t["label"], quote=True)}">{t["id"]}</a>' for t in data['tasks'])
    return f'''<article class="project-showcase" aria-labelledby="project-example-title">
      <div class="project-intro"><div><p class="eyebrow">Inside a professional project</p><h2 id="project-example-title"><span>P02</span> Syndicated refinancing</h2></div><span class="project-version">Project example · v{data['version']}</span></div>
      <p class="project-description">{esc(data['description'])}</p>
      <ul class="project-facts" aria-label="Project facts"><li><strong>13</strong> scored subtasks</li><li><strong>One</strong> persistent workspace</li><li><strong>6</strong> final deliverables</li></ul>
      <div class="project-workspace">
        <div class="workspace-heading"><div><h3>The agent’s own work, carried forward</h3><p>New materials arrive in stages. Earlier artifacts stay available for reuse and revision.</p></div><button id="project-reset" type="button" hidden>Show all connections <span aria-hidden="true">↺</span></button></div>
        <div class="project-legend" aria-label="Connection types"><span><i class="legend-artifact"></i>Artifact handoff</span><span><i class="legend-context"></i>Conditions &amp; context</span><span><i class="legend-feedback"></i>Business feedback</span></div>
        <p class="project-interaction-hint" hidden>Select a task to explore its inputs, outputs and connections.</p>
        <div class="project-map" aria-label="P02 task dependencies">
          <svg class="project-wires" viewBox="0 0 1120 660" preserveAspectRatio="none" aria-hidden="true"><defs>{markers}</defs>{''.join(paths)}</svg>
          {''.join(phases).replace('FEEDBACK_NODE_PLACEHOLDER', feedback_html)}
        </div>
        <div class="project-package" id="p02-FINAL" data-project-node="FINAL"><div><span class="package-tag">Final handoff</span><h3>Six files. One delivery package.</h3><p>Current arrangements, supporting analysis and outstanding conditions.</p></div><ul>{outputs}</ul></div>
      </div>
      <p class="project-map-note">Arrows show how earlier work informs later deliverables, not parallel execution. Earlier conclusions can be checked and corrected.</p>
      <div class="project-detail" id="project-detail" tabindex="-1" hidden>
        <div class="project-detail-heading"><h3 id="project-detail-title">Explore the dependencies</h3><p id="project-detail-hint">Select a task to trace the work it uses and the deliverables it informs.</p></div>
        <div class="project-detail-columns"><div><h4>Uses earlier work</h4><p id="project-detail-uses">Diligence, financing terms and models become inputs to later tasks.</p><div id="project-detail-incoming" class="detail-links"></div></div><div><h4>Produces</h4><p id="project-detail-produces">Each submission becomes part of the agent’s persistent project workspace.</p></div><div><h4>Feeds into</h4><p id="project-detail-feeds">Later reviews, lender responses and the final delivery package.</p><div id="project-detail-outgoing" class="detail-links"></div></div></div>
        <p class="sr-only" id="project-selection-status" role="status"></p>
      </div>
      <div class="project-assessments"><section class="checkpoint-assessment" aria-labelledby="checkpoint-title"><span class="assessment-label">At each submission</span><h3 id="checkpoint-title">Checkpoint evaluation</h3><p>Each subtask submission is preserved and scored at its checkpoint.</p><div class="checkpoint-list" aria-label="Thirteen scored checkpoints">{checkpoints}</div></section><section class="final-assessment" aria-labelledby="package-assessment-title"><span class="assessment-label">At final handoff</span><h3 id="package-assessment-title">Final delivery evaluation</h3><p>The final submitted package is evaluated independently for artifact quality, cross-file consistency, and package acceptance.</p><div class="assessment-views"><span>Artifact quality</span><span>Cross-file consistency</span><span>Package acceptance</span></div></section></div>
      <p class="project-evaluation-note">Later corrections can improve the final delivery; earlier checkpoint scores remain unchanged. Signing preparation does not mean that financing has been approved or completed.</p>
    </article>'''
