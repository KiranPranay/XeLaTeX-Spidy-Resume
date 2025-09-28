import json, hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

def esc(s: str) -> str:
    if s is None:
        return ""
    return (str(s)
            .replace('\\', r'\\')
            .replace('&', r'\&')
            .replace('%', r'\%')
            .replace('#', r'\#')
            .replace('_', r'\_')
            .replace('{', r'\{')
            .replace('}', r'\}'))

def join_list_esc(items):
    return ", ".join(esc(x) for x in (items or []))

def bulletize(items, prefix="  \\item "):
    return "\n".join(f"{prefix}{esc(x)}" for x in (items or []))

def education_lines(edu):
    lines = []
    for e in (edu or []):
        parts = [esc(e.get("degree","")), esc(e.get("institution",""))]
        line = " \\textemdash\\ ".join(p for p in parts if p)
        tail = []
        if e.get("score"):
            t = e.get("type","Score")
            tail.append(f"{esc(e['score'])} ({esc(t)})")
        if e.get("status"):
            tail.append(esc(e["status"]))
        if tail:
            line += " \\\\ \\textcolor{muted}{" + "  |  ".join(tail) + "}"
        lines.append(line)
    return "\n\n".join(lines)

def experience_block(exps):
    out = []
    for e in (exps or []):
        header = f"\\textbf{{{esc(e.get('position',''))}}} \\hfill {esc(e.get('duration',''))} \\\\ \\textit{{{esc(e.get('organization',''))}}}"
        bullets = []
        if e.get("impact"):
            bullets += [f"\\item {esc(x)}" for x in e["impact"]]
        if e.get("responsibilities"):
            bullets += [f"\\item {esc(x)}" for x in e["responsibilities"]]
        block = header + "\n\\begin{itemize}\n" + "\n".join(bullets) + "\n\\end{itemize}\n"
        out.append(block)
    return "\n\n".join(out)

def projects_block(prjs):
    out = []
    for p in (prjs or []):
        head = f"\\textbf{{{esc(p.get('title',''))}}}"
        desc = esc(p.get("description",""))
        tech = join_list_esc(p.get("technologies", []))
        imp = bulletize(p.get("impact", []))
        section = head + (f" \\\\ {desc}" if desc else "")
        if tech:
            section += f" \\\\ \\textcolor{{muted}}{{{tech}}}"
        if imp:
            section += f"\n\\begin{{itemize}}\n{imp}\n\\end{{itemize}}"
        out.append(section)
    return "\n\n".join(out)

def main():
    base = Path(".")
    data = json.loads((base/"resume.json").read_text(encoding="utf-8"))
    tpl = (base/"template.tex").read_text(encoding="utf-8")

    ist = timezone(timedelta(hours=5, minutes=30))
    build_time_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M")
    build_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()[:10]

    pd = data.get("personal_details", {})
    tpl = tpl.replace("<<PDF_AUTHOR>>", esc(pd.get("name","")))
    tpl = tpl.replace("<<PDF_TITLE>>", esc(f"{pd.get('name','')} — Resume"))
    tpl = tpl.replace("<<PDF_SUBJECT>>", "Professional Resume")
    tpl = tpl.replace("<<PDF_KEYWORDS>>", "Resume, Engineering, Robotics, Automation, Mechanical, IoT")

    tpl = tpl.replace("<<BUILD_TIME>>", build_time_ist)
    tpl = tpl.replace("<<BUILD_HASH>>", build_hash)

    tpl = tpl.replace("<<NAME>>", esc(pd.get("name","")))
    tpl = tpl.replace("<<EMAIL>>", esc(pd.get("email","")))
    tpl = tpl.replace("<<MOBILE>>", esc(pd.get("mobile","")))
    tpl = tpl.replace("<<SUMMARY>>", esc(data.get("professional_summary","")))

    sk = data.get("skills", {})
    tpl = tpl.replace("<<SK_ENGINEERING>>", join_list_esc(sk.get("engineering", [])))
    tpl = tpl.replace("<<SK_SOFTWARE>>", join_list_esc(sk.get("software", [])))
    tpl = tpl.replace("<<SK_EIOT>>", join_list_esc(sk.get("electronics_iot", [])))
    tpl = tpl.replace("<<SK_CAD>>", join_list_esc(sk.get("cad", [])))
    tpl = tpl.replace("<<SK_ANALYSIS>>", join_list_esc(sk.get("analysis", [])))
    tpl = tpl.replace("<<SK_SOFT>>", join_list_esc(sk.get("soft_skills", [])))

    tpl = tpl.replace("<<EXPERIENCE_BLOCK>>", experience_block(data.get("experience", [])))
    tpl = tpl.replace("<<PROJECTS_BLOCK>>", projects_block(data.get("projects", [])))
    tpl = tpl.replace("<<ACHIEVEMENTS_BLOCK>>", bulletize(data.get("achievements", [])))
    tpl = tpl.replace("<<EDUCATION_BLOCK>>", education_lines(data.get("education", [])))

    lang = data.get("languages", {})
    tpl = tpl.replace("<<LANG_SPOKEN>>", join_list_esc(lang.get("spoken", [])))
    tpl = tpl.replace("<<LANG_PROG>>", join_list_esc(lang.get("programming", [])))
    tpl = tpl.replace("<<ROLES_BLOCK>>", join_list_esc(data.get("preferred_roles", [])))

    (base/"Pranay_Kiran_Resume.tex").write_text(tpl, encoding="utf-8")
    print("Generated: Pranay_Kiran_Resume.tex")

if __name__ == "__main__":
    main()
