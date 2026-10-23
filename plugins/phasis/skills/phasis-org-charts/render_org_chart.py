#!/usr/bin/env python3
"""render_org_chart.py: rows JSON in, one static SVG out (phasis-org-charts skill).

A department view of a company's current job postings, in the phasis-diagram 1.0.0 style: the company is the one
focal ink card, each source department is a card with its count and teams, dashed = includes an inferred placement,
dotted = department unknown. Every count and every label comes from the rows. Never reporting lines.

The script refuses a row without a source_url (http/https) or a captured_at (ISO 8601 UTC), a documented row without a
department, an inferred row without a department and a basis, an unknown row with a department, and a row with an
email address or a phone number in a served field. If it refuses any row, it draws nothing.
Python standard library only. No network.

Usage: render_org_chart.py ROWS.json [--out org-chart.svg]   (ROWS.json may be - for stdin)
Exit: 0 = drawn; 1 = refused rows or no rows (nothing drawn); 2 = bad input.
"""
import json
import re
import sys
import textwrap
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

STATUSES = ("documented", "inferred", "unknown")
TEXT_FIELDS = ("title", "department", "department_parent", "team", "location", "posted_date")
URL_FIELDS = ("source_url", "placement_source_url")
SERVED = TEXT_FIELDS + URL_FIELDS + ("captured_at", "placement_status", "placement_basis")
PHONE_FIELDS = ("title", "department", "department_parent", "team", "location", "placement_basis")

# phasis-diagram style.md section 1 (the 10 tokens; this card uses 5) and section 2 (system fonts, no web fonts).
INK, PAPER, MUTED, RULE = "#111111", "#ffffff", "#666666", "#dddddd"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,monospace"
W, PAD, COLS, GAP = 960, 24, 4, 16
DASH = {"documented": None, "inferred": "4 3", "unknown": "1 3"}
MAX_TEAMS = 6

ISO_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|\+00:00|\+0000)$")
URL = re.compile(r"^https?://[^\s/@]+\.[^\s/]+(/\S*)?$")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+(@|%40)[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
DATES = re.compile(r"\d{4}-\d{2}-\d{2}(T[\d:.]+(Z|[+-]\d{2}:?\d{2})?)?")
PHONE = re.compile(r"(?<![\w/=-])(\+?\(?\d[\d\s().-]{7,}\d)(?![\w/])")
USAGE = __doc__.split("Usage:")[1].split("Exit:")[0].strip()
SHAPE = {
    "company": "the company name (drawn on the focal card)",
    "domain": "the company domain",
    "sources": [{"url": "feed or page URL", "kind": "feed | page", "captured_at": "ISO 8601 UTC"}],
    "not_found": ["what you looked for and did not find"],
    "rows": [{"title": "", "department": "", "department_parent": "", "team": "", "location": "", "posted_date": "",
              "source_url": "http(s) URL", "captured_at": "ISO 8601 UTC, e.g. 2026-10-23T14:05:00Z",
              "placement_status": "documented | inferred | unknown",
              "placement_source_url": "documented: the URL that states the department",
              "placement_basis": "inferred: one sentence"}],
}


def s(v):
    return v.strip() if isinstance(v, str) else ""


def contact_in(text):
    """Return 'email' or 'phone' when the text holds one. ISO dates and times are not phone numbers."""
    if EMAIL.search(text):
        return "email"
    for m in PHONE.finditer(DATES.sub(" ", text)):
        if len(re.sub(r"\D", "", m.group(1))) >= 9:
            return "phone"
    return None


def check(rows):
    """Return (accepted rows, refusals). These refusal rules are the whole contract of the script."""
    ok, refused = [], []
    for i, r in enumerate(rows):
        why = []
        if not isinstance(r, dict):
            refused.append({"index": i, "title": None, "reasons": ["a row must be a JSON object"]})
            continue
        st = s(r.get("placement_status"))
        dep = s(r.get("department"))
        if not s(r.get("title")):
            why.append("no title")
        if not URL.match(s(r.get("source_url"))):
            why.append("no source_url (http/https)")
        if not ISO_UTC.match(s(r.get("captured_at"))):
            why.append("no captured_at (ISO 8601 UTC, for example 2026-10-23T14:05:00Z)")
        if st not in STATUSES:
            why.append("placement_status must be documented, inferred or unknown")
        if st == "documented" and not dep:
            why.append("documented placement without a department")
        if st == "documented" and s(r.get("placement_source_url")) and not URL.match(s(r.get("placement_source_url"))):
            why.append("placement_source_url is not an http/https URL")
        if st == "inferred" and not dep:
            why.append("inferred placement without a department")
        if st == "inferred" and len(s(r.get("placement_basis"))) < 8:
            why.append("inferred placement without a basis")
        if st == "unknown" and dep:
            why.append("unknown placement with a department: use documented or inferred, or leave the department empty")
        for k in SERVED:
            v = s(r.get(k))
            kind = "email" if EMAIL.search(v) else contact_in(v) if k in PHONE_FIELDS else None
            if kind:
                why.append(f"{k} holds a {kind}: contact details are never served; remove it")
        if why:
            refused.append({"index": i, "title": r.get("title"), "reasons": why})
            continue
        row = {k: s(r.get(k)) for k in SERVED}
        if st == "documented" and not row["placement_source_url"]:
            row["placement_source_url"] = row["source_url"]
        ok.append(row)
    return ok, refused


def group(rows):
    """Departments as the rows state them, largest first. Unknown rows form one separate group."""
    by = {}
    for r in rows:
        if r["placement_status"] != "unknown":
            by.setdefault(r["department"], []).append(r)
    deps = []
    for name, rs in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
        teams = {}
        for r in rs:
            if r["team"]:
                teams[r["team"]] = teams.get(r["team"], 0) + 1
        parents = sorted({r["department_parent"] for r in rs if r["department_parent"]})
        deps.append({"name": name, "n": len(rs), "parents": parents,
                     "documented": sum(1 for r in rs if r["placement_status"] == "documented"),
                     "inferred": sum(1 for r in rs if r["placement_status"] == "inferred"),
                     "teams": sorted(teams.items(), key=lambda kv: (-kv[1], kv[0].lower()))})
    unknown = [r for r in rows if r["placement_status"] == "unknown"]
    return deps, unknown


def t(x, y, text, size=9, fill=MUTED, font=SANS, weight=400, anchor="start", ls=None, opacity=None):
    extra = f' letter-spacing="{ls}"' if ls else ' style="letter-spacing:0"'
    op = f' fill-opacity="{opacity}"' if opacity else ""
    return (f'<text x="{x:g}" y="{y:g}" fill="{fill}"{op} font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{escape(text)}</text>')


def rect(x, y, w, h, stroke=INK, fill=PAPER, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="1"{d}/>'


def wrap(text, chars, lines):
    out = textwrap.wrap(text, chars) or [""]
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: max(1, chars - 1)].rstrip() + "…"
    return out


def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def card_lines(d):
    """The text lines of one department card: (text, size, fill, font, weight)."""
    lines = [(x, 11, INK, SANS, 700) for x in wrap(d["name"], 30, 3)]
    if d["parents"]:
        lines += [(x, 8, MUTED, MONO, 400) for x in wrap("in " + ", ".join(d["parents"]), 38, 2)]
    lines.append((plural(d["n"], "role"), 9, MUTED, MONO, 400))
    status = [f"{d[k]} {k}" for k in ("documented", "inferred") if d.get(k)] or ["unknown"]
    lines.append((" · ".join(status), 8, MUTED, MONO, 400))
    for name, n in d["teams"][:MAX_TEAMS]:
        lines += [(x, 8.5, INK, SANS, 400) for x in wrap(f"{name} ({n})", 36, 2)]
    if len(d["teams"]) > MAX_TEAMS:
        lines.append((f"+{len(d['teams']) - MAX_TEAMS} more teams", 8.5, MUTED, SANS, 400))
    return lines


def render(inp):
    rows, _ = check(inp.get("rows") or [])
    company = s(inp.get("company")) or "Company"
    deps, unknown = group(rows)
    cards = [dict(d, status="inferred" if d["inferred"] else "documented") for d in deps]
    if unknown:
        cards.append({"name": "Department not stated", "n": len(unknown), "parents": [], "documented": 0, "inferred": 0,
                      "teams": [], "status": "unknown", "unknown": True})
    dates = sorted(r["captured_at"] for r in rows)
    as_of = dates[-1][:10]
    hosts = []
    for u in [s(x.get("url")) for x in inp.get("sources") or [] if isinstance(x, dict)] + [r["source_url"] for r in rows]:
        h = urlsplit(u).hostname if URL.match(u) else None
        if h and h not in hosts:
            hosts.append(h)
    counts = {k: sum(1 for r in rows if r["placement_status"] == k) for k in STATUSES}
    title = f"{company} · open roles by department"
    desc = (f"Department view of {plural(len(rows), 'current job posting')} of {company}, as the source classifies them, "
            f"from the source as of {as_of}, not yet checked. {plural(len(deps), 'department')}; documented "
            f"{counts['documented']}, inferred {counts['inferred']}, unknown {counts['unknown']}. "
            f"Departments are source classifications, not reporting lines.")

    cw = (W - 2 * PAD - (COLS - 1) * GAP) / COLS
    body, top = [], 96
    cx = W / 2
    body.append(rect(cx - 150, top, 300, 50, INK, INK))
    for i, line in enumerate(wrap(company, 40, 1)):
        body.append(t(cx, top + 22, line, 12, PAPER, SANS, 700, "middle"))
    body.append(t(cx, top + 39, f"{plural(len(rows), 'open role')} · {plural(len(deps), 'department')}", 9, PAPER, MONO,
                  anchor="middle", opacity="0.75"))
    bus, y = top + 74, top + 98
    grid = []
    for r0 in range(0, len(cards), COLS):
        row_cards = cards[r0:r0 + COLS]
        h = max(16 + sum(13 if ln[1] >= 9 else 12 for ln in card_lines(c)) + 10 for c in row_cards)
        for j, c in enumerate(row_cards):
            grid.append((c, PAD + j * (cw + GAP), y, h))
        y += h + GAP
    xs = sorted({x for _, x, _, _ in grid})
    body.append(f'<path d="M {cx:g} {top + 50} L {cx:g} {bus}" fill="none" stroke="{MUTED}" stroke-width="1"/>')
    if xs:
        body.append(f'<path d="M {min(xs[0] + cw / 2, cx):g} {bus} L {max(xs[-1] + cw / 2, cx):g} {bus}" fill="none" '
                    f'stroke="{MUTED}" stroke-width="1"/>')
    for x in xs:
        last = max(cy for _, gx, cy, _ in grid if gx == x)
        body.append(f'<path d="M {x + cw / 2:g} {bus} L {x + cw / 2:g} {last}" fill="none" stroke="{MUTED}" stroke-width="1"/>')
    for c, x, cy, h in grid:
        unk = c.get("unknown")
        attrs = (f'class="dept" data-department="{escape(c["name"] if not unk else "")}" data-count="{c["n"]}" '
                 f'data-status="{c["status"]}"')
        g = [f"<g {attrs}>", rect(x, cy, cw, h, MUTED if unk else INK, PAPER, DASH[c["status"]])]
        ly = cy + 18
        for text, size, fill, font, weight in card_lines(c):
            g.append(t(x + 12, ly, text, size, fill, font, weight))
            ly += 13 if size >= 9 else 12
        g.append("</g>")
        body.append("".join(g))
    y += 4
    notes = ["Built from current job postings, not an official org chart.",
             "The source's own department and team labels, copied as written. A department is a source classification,",
             "not a reporting line."]
    nf = [x for x in inp.get("not_found") or [] if isinstance(x, str) and x.strip()]
    if nf:
        notes.append(f"Not found: {plural(len(nf), 'item')}, listed with this chart's answer.")
    for line in notes:
        body.append(t(PAD, y + 10, line, 9, MUTED))
        y += 14
    when = dates[0] if dates[0] == dates[-1] else f"{dates[0]} to {dates[-1]}"
    src = f"Source: {', '.join(hosts) or 'not stated'}, captured {when}"
    src_lines = wrap(src, 150, 3)
    h_total = int(y + 26 + 12 * len(src_lines) + 44)
    ly = h_total - 40
    foot = [t(PAD, ly - 10 - 12 * (len(src_lines) - 1 - i), line, 8, MUTED, MONO) for i, line in enumerate(src_lines)]
    foot += [f'<line x1="{PAD}" y1="{ly}" x2="{W - PAD}" y2="{ly}" stroke="{RULE}" stroke-width="1"/>',
             t(PAD, ly + 18, "LEGEND", 8, MUTED, MONO, ls=".18em")]
    legend = [(rect(0, 0, 16, 12, INK, INK), "company"),
              (rect(0, 0, 16, 12), "documented: the source states the department")]
    if counts["inferred"]:
        legend.append((rect(0, 0, 16, 12, INK, PAPER, DASH["inferred"]), "includes inferred placements, with basis"))
    if counts["unknown"]:
        legend.append((rect(0, 0, 16, 12, MUTED, PAPER, DASH["unknown"]), "unknown: no source states the department"))
    lx = 90
    for sw, label in legend:
        foot.append(sw.replace('x="0" y="0"', f'x="{lx}" y="{ly + 9}"'))
        foot.append(t(lx + 22, ly + 18, label, 8.5, MUTED))
        lx += 40 + int(len(label) * 4.6)
    head = [t(PAD, 30, "ORG CHART", 8, MUTED, MONO, ls=".18em"),
            t(PAD, 50, wrap(title, 110, 1)[0], 14, INK, SANS, 700),
            t(PAD, 66, f"From the source, as of {as_of}, not yet checked", 9, MUTED),
            f'<line x1="{PAD}" y1="78" x2="{W - PAD}" y2="78" stroke="{RULE}" stroke-width="1"/>']
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h_total}" role="img" '
           f'aria-labelledby="org-title org-desc" id="svg-org-chart" class="diagram-svg" style="--canvas-width:{W}px">'
           f'<title id="org-title">{escape(title)}</title><desc id="org-desc">{escape(desc)}</desc>'
           f'<style>#svg-org-chart text{{font-variant-numeric:tabular-nums}}</style>'
           f'<g aria-hidden="true" class="diagram-background"><rect width="{W}" height="{h_total}" fill="{PAPER}"/></g>'
           + "".join(head) + "".join(body) + "".join(foot) + "</svg>\n")
    summary = {"rows_drawn": len(rows), "departments": [{"name": d["name"], "count": d["n"]} for d in deps],
               "department_unknown": len(unknown), "counts_by_status": counts, "as_of": as_of, "sources": hosts}
    return svg, summary


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__ + "\nInput JSON shape:\n" + json.dumps(SHAPE, indent=1))
        return 0 if argv else 2
    out = Path("org-chart.svg")
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            print(json.dumps({"error": "--out needs a file name", "usage": USAGE}))
            return 2
        out = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    try:
        inp = json.load(sys.stdin if argv[0] == "-" else open(argv[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(json.dumps({"error": f"cannot read the rows JSON: {e}", "usage": USAGE}))
        return 2
    if not isinstance(inp, dict) or not isinstance(inp.get("rows"), list):
        print(json.dumps({"error": "the input must be a JSON object with a rows list", "usage": USAGE}))
        return 2
    company_contact = contact_in(s(inp.get("company")))
    if company_contact:
        print(json.dumps({"error": f"company holds a {company_contact}: contact details are never served"}))
        return 2
    ok, refused = check(inp["rows"])
    result = {"rows_in": len(inp["rows"]), "rows_accepted": len(ok), "refused": refused}
    if refused:
        result["drawn"] = False
        result["note"] = "Nothing drawn. Fix each refused row or leave it out (and say why), then run again."
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 1
    if not ok:
        result["drawn"] = False
        result["note"] = "No rows: nothing drawn. Say that no current posting was found and list what you checked."
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 1
    svg, summary = render(inp)
    out.write_text(svg, encoding="utf-8")
    result.update(summary, drawn=True, chart_file=str(out.resolve()),
                  label=f"From the source, as of {summary['as_of']}, not yet checked")
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
