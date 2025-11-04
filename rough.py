# Project Manager / PM Resource Recommendation
if pm_reco:
    if isinstance(pm_reco, dict):
        count = pm_reco.get("count")
        responsibilities = pm_reco.get("responsibilities", [])
        recommendation = pm_reco.get("recommendation")

        pm_html = ""
        if count is not None:
            pm_html += f"<p><strong>Count:</strong> {esc(str(count))}</p>"
        if responsibilities:
            pm_html += "<p><strong>Responsibilities:</strong></p><ul>"
            for r in responsibilities:
                pm_html += f"<li>{esc(str(r))}</li>"
            pm_html += "</ul>"
        if recommendation:
            pm_html += f"<p><strong>Recommendation:</strong> {esc(str(recommendation))}</p>"
        if not pm_html:
            pm_html = "<p><em>Not provided</em></p>"
    else:
        # fallback to simple string if not dict
        pm_html = kv("PM / Resource Recommendation", pm_reco)
else:
    if isinstance(project_manager, dict) and project_manager:
        pm_html = ""
        pm_count = project_manager.get("count")
        if pm_count is not None:
            pm_html += f"<p><strong>Project Manager(s):</strong> {esc(str(pm_count))}</p>"
        responsibilities = project_manager.get("responsibilities") or []
        if responsibilities:
            pm_html += "<p><strong>Responsibilities:</strong></p><ul>"
            for d in responsibilities:
                pm_html += f"<li>{esc(str(d))}</li>"
            pm_html += "</ul>"
    else:
        pm_html = "<p><em>Not provided</em></p>"
