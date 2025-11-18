{
  "bands": [
    {
      "min_score": 1,
      "max_score": 27,
      "roles": []             // self-managed → no roles
    },
    {
      "min_score": 28,
      "max_score": 39,
      "roles": ["Project Lead"]
    },
    {
      "min_score": 40,
      "max_score": 51,
      "roles": ["Project Manager"]
    },
    {
      "min_score": 52,
      "max_score": 60,
      "roles": [
        "Programme Manager",
        "Senior Project Manager",
        "Change Manager"
      ]
    }
  ]
}













import json
from pathlib import Path
from typing import Any, Dict, List
# ---------- PM role mapping support ----------

# Adjust these filenames / paths if needed
_JOB_PROFILE_FILE = Path(__file__).with_name("job_profile_mapping.json")
_PM_BANDS_FILE = Path(__file__).with_name("pm_role_bands.json")

def _load_json_safe(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

_job_profiles_data = _load_json_safe(_JOB_PROFILE_FILE)
_pm_bands_data = _load_json_safe(_PM_BANDS_FILE)

_JOB_PROFILES: List[Dict[str, Any]] = _job_profiles_data.get("job_profile_mapping", [])
_PM_BANDS: List[Dict[str, Any]] = _pm_bands_data.get("bands", [])


def get_pm_profiles_for_score(total_score: int) -> List[Dict[str, Any]]:
    """
    Based on total_score, return a list of job-profile dicts that should
    be shown in the PM / Resource Recommendation section.

    - 1–27   → []  (self-managed, no roles)
    - 28–39  → ["Project Lead"]
    - 40–51  → ["Project Manager"]
    - 52–60  → multiple roles (from pm_role_bands.json)
    """
    # Find the matching band
    for band in _PM_BANDS:
        try:
            min_s = int(band.get("min_score", 0))
            max_s = int(band.get("max_score", 0))
        except Exception:
            continue

        if min_s <= total_score <= max_s:
            role_names = band.get("roles") or []
            break
    else:
        # no band matched → default: no profiles
        return []

    if not role_names:
        # self-managed case
        return []

    # For each role name, pick the corresponding job_profile block
    results: List[Dict[str, Any]] = []
    for rn in role_names:
        for prof in _JOB_PROFILES:
            if prof.get("job_profile") == rn:
                results.append(prof)
                break  # stop after first match

    return results















# compute score and scoring summary
    total_score, budget = _compute_total_score(questions)
    try:
        scoring_info = scoring.interpret_score(total_score)
    except Exception:
        logger.exception("scoring.interpret_score failed; using fallback")
        scoring_info = {"complexity": None, "recommendation": None, "rationale": None}

    # NEW: get PM profiles based on score
    try:
        pm_profiles = scoring.get_pm_profiles_for_score(total_score)
    except Exception:
        logger.exception("get_pm_profiles_for_score failed")
        pm_profiles = []



















pm_reco = resp.get("pm_resource_recommendation") or []
project_manager = resp.get("project_manager") or {}  # keep old fallback

# PM / Resource Recommendation
if isinstance(pm_reco, list) and pm_reco:
    # pm_reco is a list of profiles (0, 1 or many)
    pm_html_parts = []
    for prof in pm_reco:
        if not isinstance(prof, dict):
            continue
        profile_name = prof.get("job_profile") or ""
        skills = prof.get("skills") or []
        pm_resp = prof.get("responsibilities") or []
        tasks = prof.get("tasks") or []

        block = ""
        if profile_name:
            block += f"<p><strong>Recommended profile:</strong> {esc(str(profile_name))}</p>"

        if skills:
            block += "<p><strong>Skills:</strong></p><ul>"
            for s in skills:
                block += f"<li>{esc(str(s))}</li>"
            block += "</ul>"

        if pm_resp:
            block += "<p><strong>Responsibilities:</strong></p><ul>"
            for r in pm_resp:
                block += f"<li>{esc(str(r))}</li>"
            block += "</ul>"

        if tasks:
            block += "<p><strong>Tasks:</strong></p><ul>"
            for t in tasks:
                block += f"<li>{esc(str(t))}</li>"
            block += "</ul>"

        if block:
            pm_html_parts.append(block)

    pm_html = "".join(pm_html_parts) if pm_html_parts else "<p><em>Not provided</em></p>"

elif isinstance(project_manager, dict) and project_manager:
    # old behaviour fallback if pm_resource_recommendation is missing
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
    # low-complexity self-managed case (1–27) will land here with empty list → “Not provided”
    pm_html = "<p><em>Not provided</em></p>"
