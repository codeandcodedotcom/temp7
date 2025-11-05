# format phase title properly (e.g., "deployment_and_uat" → "Deployment and UAT")
phase_name = str(phase_key).replace("_", " ")
phase_name = phase_name.capitalize()  # only capitalize first letter
# fix "Uat" → "UAT" and keep "and" lowercase
phase_name = (
    phase_name.replace(" And ", " and ")
               .replace(" Uat", " UAT")
               .replace(" Qa", " QA")
)
timeline_html += f"<h4>{esc(phase_name)}</h4>"
