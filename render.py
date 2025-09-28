import json, hashlib, re
from datetime import datetime, timezone, timedelta
from pathlib import Path

def esc_text(s: str) -> str:
    if s is None: return ""
    return (str(s)
            .replace('\\', r'\\').replace('&', r'\&').replace('%', r'\%')
            .replace('#', r'\#').replace('_', r'\_')
            .replace('{', r'\{').replace('}', r'\}'))

def esc_url(u: str) -> str:
    if not u: return ""
    return u.strip().replace(" ", "%20")  # keep URL chars intact

def join_list_esc(items): return ", ".join(esc_text(x) for x in (items or []))
def bulletize(items, prefix="  \\item "): return "\n".join(f"{prefix}{esc_text(x)}" for x in (items or []))

def nice_label(url: str) -> str:
    if not url: return ""
    label = re.sub(r'^https?://', '', url.strip(), flags=re.I)
    label = re.sub(r'/$', '', label)
    return esc_text(label)

def education_block(edu):
    rows=[]
    for e in (edu or []):
        degree = esc_text(e.get("degree",""))
        inst   = esc_text(e.get("institution",""))
        tail=[]
        if e.get("score"):
            tail.append(f"{esc_text(e['score'])} ({esc_text(e.get('type','Score'))})")
        if e.get("status"):
            tail.append(esc_text(e["status"]))
        details = "  |  ".join(tail)
        rows.append(f"\\EducationEntry{{{degree}}}{{{inst}}}{{{details}}}")
    return "\n".join(rows)

def experience_block(exps):
    out=[]
    for e in (exps or []):
        header = f"\\ExperienceEntry{{{esc_text(e.get('position',''))}}}{{{esc_text(e.get('organization',''))}}}{{{esc_text(e.get('duration',''))}}}"
        bullets=[]
        if e.get("impact"): bullets += [f"\\item {esc_text(x)}" for x in e["impact"]]
        if e.get("responsibilities"): bullets += [f"\\item {esc_text(x)}" for x in e["responsibilities"]]
        block = header + ("\n\\begin{itemize}\n" + "\n".join(bullets) + "\n\\end{itemize}\n" if bullets else "\n")
        out.append(block)
    return "\n\n".join(out)

def projects_block(prjs):
    out=[]
    for p in (prjs or []):
        head = f"\\textbf{{{esc_text(p.get('title',''))}}}"
        desc = esc_text(p.get("description",""))
        tech = join_list_esc(p.get("technologies", []))
        imp  = bulletize(p.get("impact", []))
        section = head + (f" \\\\ {desc}" if desc else "")
        if tech: section += f" \\\\ \\textcolor{{muted}}{{{tech}}}"
        if imp:  section += f"\n\\begin{{itemize}}\n{imp}\n\\end{{itemize}}"
        out.append(section)
    return "\n\n".join(out)

def build_contact_block(pd: dict) -> str:
    parts = []
    email = pd.get("email")
    mobile = pd.get("mobile")
    # Accept several keys for portfolio
    portfolio = pd.get("portfolio") or pd.get("website") or pd.get("url")

    # If portfolio missing, try derive from email domain (ignore common providers)
    if not portfolio and isinstance(email, str) and "@" in email:
        domain = email.split("@",1)[1].lower()
        if domain not in {"gmail.com","outlook.com","yahoo.com","hotmail.com","proton.me","icloud.com"}:
            portfolio = f"https://{domain}"

    if email:
        parts.append(f"\\href{{mailto:{esc_url(email)}}}{{{esc_text(email)}}}")
    if mobile:
        parts.append(f"+91-{esc_text(mobile)}")
    if portfolio:
        parts.append(f"\\href{{{esc_url(portfolio)}}}{{{nice_label(portfolio)}}}")

    sep = " \\textcolor{muted}{\\textbar} "
    return sep.join(parts)

def main():
    base = Path(".")
    data = json.loads((base/"resume.json").read_text(encoding="utf-8"))
    tpl  = (base/"template.tex").read_text(encoding="utf-8")

    ist = timezone(timedelta(hours=5, minutes=30))
    build_time_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M")
    build_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()[:10]

    pd = data.get("personal_details", {})
    tpl = tpl.replace("<<PDF_AUTHOR>>", esc_text(pd.get("name","")))
    tpl = tpl.replace("<<PDF_TITLE>>",  esc_text(f"{pd.get('name','')} — Resume"))
    tpl = tpl.replace("<<PDF_SUBJECT>>","Professional Resume")
    tpl = tpl.replace("<<PDF_KEYWORDS>>","Resume, Engineering, Robotics, Automation, Mechanical, IoT")

    tpl = tpl.replace("<<BUILD_TIME>>", build_time_ist)
    tpl = tpl.replace("<<BUILD_HASH>>", build_hash)

    tpl = tpl.replace("<<NAME>>", esc_text(pd.get("name","")))
    tpl = tpl.replace("<<CONTACT_BLOCK>>", build_contact_block(pd))
    tpl = tpl.replace("<<SUMMARY>>", esc_text(data.get("professional_summary","")))

    sk = data.get("skills", {})
    tpl = tpl.replace("<<SK_ENGINEERING>>", join_list_esc(sk.get("engineering", [])))
    tpl = tpl.replace("<<SK_SOFTWARE>>",   join_list_esc(sk.get("software", [])))
    tpl = tpl.replace("<<SK_EIOT>>",       join_list_esc(sk.get("electronics_iot", [])))
    tpl = tpl.replace("<<SK_CAD>>",        join_list_esc(sk.get("cad", [])))
    tpl = tpl.replace("<<SK_ANALYSIS>>",   join_list_esc(sk.get("analysis", [])))
    tpl = tpl.replace("<<SK_SOFT>>",       join_list_esc(sk.get("soft_skills", [])))

    tpl = tpl.replace("<<EXPERIENCE_BLOCK>>", experience_block(data.get("experience", [])))
    tpl = tpl.replace("<<PROJECTS_BLOCK>>",   projects_block(data.get("projects", [])))
    tpl = tpl.replace("<<ACHIEVEMENTS_BLOCK>>", bulletize(data.get("achievements", [])))
    tpl = tpl.replace("<<EDUCATION_BLOCK>>",  education_block(data.get("education", [])))

    lang = data.get("languages", {})
    tpl = tpl.replace("<<LANG_SPOKEN>>", join_list_esc(lang.get("spoken", [])))
    tpl = tpl.replace("<<LANG_PROG>>",   join_list_esc(lang.get("programming", [])))
    tpl = tpl.replace("<<ROLES_BLOCK>>", join_list_esc(data.get("preferred_roles", [])))

    (base/"Pranay_Kiran_Resume.tex").write_text(tpl, encoding="utf-8")
    print("Generated: Pranay_Kiran_Resume.tex")

if __name__ == "__main__":
    main()
