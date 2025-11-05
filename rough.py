# prefer new key "prerequisites" (list), fallback to old "pre_requisites"
p_prereq = phase_val.get("prerequisites") or phase_val.get("pre_requisites")
if p_prereq:
    if isinstance(p_prereq, list):
        timeline_html += "<p><strong>Pre-requisites:</strong></p><ul>"
        for prereq in p_prereq:
            timeline_html += f"<li>{esc(str(prereq))}</li>"
        timeline_html += "</ul>"
    else:
        timeline_html += f"<p><strong>Pre-requisites:</strong> {esc(str(p_prereq))}</p>"
