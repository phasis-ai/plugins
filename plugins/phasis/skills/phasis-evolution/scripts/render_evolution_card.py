#!/usr/bin/env python3
"""Draw the site_history card (one static SVG) from an evolution.py result file. Standard library only, no network.

Style: phasis-diagram 1.0.0 (10 tokens, system fonts, one focal mark, legend strip, no fields in timelines).
Dates run across (positions in proportion to time, a tick per capture), sections run down. A diamond marks a section
that changed since the capture before; the top change is the one lavender diamond; a small circle marks a section that
was captured with no change; a dashed column marks a capture whose body copy is not readable. Below: the top 3 changes
with short quotes, the counts, the label and the source line. Every mark, count and quote comes from the result rows.

The script REFUSES a result with a row or a capture that has no capture URL (https://web.archive.org/web/<timestamp>/...)
or no 14-digit timestamp, or a quote longer than 104 characters. Then it draws nothing.

Usage: python3 -I render_evolution_card.py evolution-<domain>.json [--out card.svg]
Prints a JSON summary (drawn, captures, marks, top changes, refused items, the output file).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import escape as e
from pathlib import Path

INK, PAPER, MUTED, RULE, LAV = "#111111", "#ffffff", "#666666", "#dddddd", "#eee7fc"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,monospace"
W = 720
QUOTE_MAX = 104
SECTIONS = [("headline", ("title", "h1")), ("value line", ("meta_description", "hero")), ("nav", ("nav",)),
            ("buttons", ("buttons",)), ("pricing", ("prices",))]
TOP_ORDER = ["h1", "title", "meta_description", "hero", "prices", "buttons"]  # amendment 3, section 1.2
NAMES = {"h1": "Headline", "title": "Page title", "meta_description": "Description", "hero": "Hero line",
         "prices": "Pricing", "buttons": "Button"}
TS = re.compile(r"^\d{14}$")


def t(x, y, s, size=9, fill=MUTED, font=SANS, weight=400, anchor="start", ls=None):
    extra = f' letter-spacing="{ls}"' if ls else ' style="letter-spacing:0"'
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{e(s)}</text>')


def day(ts):
    return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"


def mon(ts):
    return datetime.strptime(ts[:8], "%Y%m%d").strftime("%b %Y")


def snap_ok(url, ts):
    return isinstance(url, str) and url.startswith(f"https://web.archive.org/web/{ts}/")


def check(res):
    """Every capture and row must carry its timestamp and capture URL; every quote at most 104 characters."""
    bad = []
    caps = [c for c in res.get("captures", []) if c.get("copy")]
    for c in caps:
        if not TS.match(str(c.get("timestamp", ""))) or not snap_ok(c.get("snapshot_url"), c.get("timestamp")):
            bad.append({"capture": c.get("timestamp"), "why": "no 14-digit timestamp or capture URL"})
    stamps = {c["timestamp"] for c in caps}
    for i, r in enumerate(res.get("rows", [])):
        for side in ("from", "to"):
            ts = str(r.get(f"{side}_timestamp", ""))
            if not TS.match(ts) or not snap_ok(r.get(f"{side}_url"), ts):
                bad.append({"row": i, "why": f"no {side} timestamp or capture URL"})
            elif ts not in stamps:
                bad.append({"row": i, "why": f"{side} capture {ts} is not in the result's captures"})
        for q in ("before", "after"):
            if len(r.get(q) or "") > QUOTE_MAX:
                bad.append({"row": i, "why": f"{q} quote longer than {QUOTE_MAX} characters"})
    return bad


def spec(res):
    """The card spec (CATALOG-DESIGN 7.2 shape, kind site_history), computed from the result rows only."""
    caps = [c for c in res["captures"] if c.get("copy")]
    rows = res["rows"]
    marks = []
    for i, c in enumerate(caps):
        col = {}
        for sec, fields in SECTIONS:
            has = any(c["copy"].get(f) for f in fields)
            known = c["copy"]["readable"] or sec in ("headline", "value line")
            changed = i > 0 and any(r["to_timestamp"] == c["timestamp"] and r["field"] in fields for r in rows)
            col[sec] = "changed" if changed else ("captured" if has else ("unknown" if not known else "absent"))
        marks.append({"timestamp": c["timestamp"], "readable": c["copy"]["readable"], "sections": col})
    top, used = [], set()
    for want_changed in (True, False):
        for f in TOP_ORDER:
            if f in used or len(top) == 3:
                continue
            cand = [r for r in rows if r["field"] == f and (r["kind"] == "changed") == want_changed]
            if cand:
                top.append(sorted(cand, key=lambda r: (r["similarity"], -int(r["to_timestamp"])))[0])
                used.add(f)
    lst = res.get("list", {})
    return {"kind": "site_history", "version": 1, "title": f"{res['domain']} homepage copy over time",
            "label": res["label"], "source_line": res["source_line"],
            "spec": {"domain": res["domain"], "captures": marks, "sections": [s for s, _ in SECTIONS],
                     "top": [{"n": i + 1, "section": r["section"], "field": r["field"], "kind": r["kind"],
                              "before": r["before"], "after": r["after"], "from": r["from_timestamp"],
                              "to": r["to_timestamp"], "from_url": r["from_url"], "to_url": r["to_url"]}
                             for i, r in enumerate(top)],
                     "counts": {"captures_used": len(caps), "rows": len(rows),
                                "monthly_captures": lst.get("monthly_captures"),
                                "html_captures": lst.get("html_captures"), "distinct_digests": lst.get("distinct_digests"),
                                "html_capture_days": lst.get("html_capture_days"),
                                "same_content": sum(bool(c.get("same_as_previous")) for c in caps),
                                "section_headings_rows": sum(r["section"] == "section headings" for r in rows)}}}


def render(c, slug="evolution-card"):
    s = c["spec"]
    caps, top, cnt = s["captures"], s["top"], s["counts"]
    n = len(caps)
    L, R, T0, rh = 112, W - 40, 104, 26
    ts = [datetime.strptime(x["timestamp"], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc).timestamp() for x in caps]
    span = (ts[-1] - ts[0]) or 1
    if ts[-1] - ts[0] < 2 * 86400:  # captures within 2 days share one column: spreading them would fake a timeline
        xs = [(L + R) / 2] * n
    else:
        xs = [L + (v - ts[0]) / span * (R - L) for v in ts]
    top_at = {(x["to"], x["section"]): x["n"] for x in top}
    b = []
    for j, sec in enumerate(s["sections"]):
        y = T0 + j * rh
        b.append(t(24, y + 3, sec.capitalize(), 10, INK, SANS, 700))
        b.append(f'<line x1="{L}" y1="{y}" x2="{R}" y2="{y}" stroke="{RULE}" stroke-width="0.8"/>')
    yb = T0 + (len(s["sections"]) - 1) * rh
    for x, cap in zip(xs, caps):  # unreadable captures: a dashed column (the body copy is unknown there)
        if not cap["readable"]:
            b.append(f'<line x1="{x:.0f}" y1="{T0 - 12}" x2="{x:.0f}" y2="{yb + 12}" stroke="{MUTED}" stroke-width="1" '
                     f'stroke-dasharray="4 3"/>')
    for x, cap in zip(xs, caps):
        for j, sec in enumerate(s["sections"]):
            y = T0 + j * rh
            st = cap["sections"][sec]
            if st == "captured":
                b.append(f'<circle cx="{x:.0f}" cy="{y}" r="3" fill="{PAPER}" stroke="{MUTED}" stroke-width="0.8"/>')
            elif st == "changed":
                num = top_at.get((cap["timestamp"], sec))
                fill = LAV if num == 1 else PAPER
                d = 6
                b.append(f'<path d="M {x:.0f} {y - d} L {x + d:.0f} {y} L {x:.0f} {y + d} L {x - d:.0f} {y} Z" fill="{fill}" '
                         f'stroke="{INK}" stroke-width="1.2"/>')
                if num:
                    b.append(f'<text x="{x + 9:.0f}" y="{y - 5}" fill="{INK}" font-family="{SANS}" font-size="9" font-weight="700" '
                             f'style="letter-spacing:0;paint-order:stroke;stroke:#ffffff;stroke-width:3">{num}</text>')
    ya = yb + 22  # date axis: a tick per capture, labels kept 56 units apart (first and last always)
    b.append(f'<line x1="{L}" y1="{ya - 8}" x2="{R}" y2="{ya - 8}" stroke="{MUTED}" stroke-width="1"/>')
    shown = []
    order = [0, n - 1] + list(range(1, n - 1)) if n > 1 else [0]
    for i in order:
        if all(abs(xs[i] - xs[k]) >= 56 for k in shown):
            shown.append(i)
    for i, x in enumerate(xs):
        b.append(f'<line x1="{x:.0f}" y1="{ya - 11}" x2="{x:.0f}" y2="{ya - 5}" stroke="{MUTED}" stroke-width="1"/>')
        if i in shown:
            anchor = "start" if len(shown) > 1 and i == 0 else "end" if len(shown) > 1 and i == n - 1 else "middle"
            b.append(t(x, ya + 6, mon(caps[i]["timestamp"]), 8.5, MUTED, anchor=anchor))
    y = ya + 34
    plural = lambda k, w: f"{k} {w}" + ("" if k == 1 else "s")
    if not top:
        b.append(t(24, y, "No change to compare.", 11, INK, SANS, 700))
        why = "The copy is the same in every capture used."
        days = cnt.get("html_capture_days") or []
        if cnt["captures_used"] == 1 or cnt["same_content"] == cnt["captures_used"] - 1:
            why = (f"A change needs 2 captures with different content. The Internet Archive holds "
                   f"{plural(cnt['captures_used'], 'capture')} of this homepage in this range.")
            if cnt.get("html_captures") and len(days) == 1 and cnt.get("distinct_digests") == 1:
                why = (f"A change needs 2 captures with different content. The Internet Archive holds "
                       f"{plural(cnt['html_captures'], 'HTML capture')} of this homepage, all on {days[0]}, "
                       f"with the same content digest.")
        b.append(t(24, y + 16, why, 9, MUTED))
        y += 34
    else:
        b.append(t(24, y, "TOP CHANGES", 8, MUTED, MONO, ls=".18em"))
        y += 18
        for x in top:
            b.append(f'<circle cx="31" cy="{y - 3}" r="7" fill="{INK}"/>')
            b.append(f'<text x="31" y="{y}" fill="{PAPER}" font-family="{SANS}" font-size="9" font-weight="700" '
                     f'text-anchor="middle" style="letter-spacing:0">{x["n"]}</text>')
            head = f'{NAMES[x["field"]]} {x["kind"]} · between {day(x["from"])} and {day(x["to"])}'
            b.append(t(46, y, head, 10, INK, SANS, 700))
            if x["before"]:
                b.append(t(46, y + 14, f'Before: “{x["before"]}”', 9, MUTED))
            if x["after"]:
                b.append(t(46, y + 14 + (14 if x["before"] else 0), f'After: “{x["after"]}”', 9, INK))
            y += 20 + 14 * (bool(x["before"]) + bool(x["after"]))
    y += 4
    unread = sum(not x["readable"] for x in caps)
    used_of = (f' used of {plural(cnt["html_captures"], "HTML capture")} in the range' if cnt.get("html_captures")
               else f' used of {plural(cnt["monthly_captures"], "monthly capture")}' if cnt.get("monthly_captures") else " used")
    note = (f'{plural(cnt["captures_used"], "capture")}{used_of}. '
            f'{plural(cnt["rows"], "change row")} in the result ({cnt["section_headings_rows"]} for section headings).')
    b.append(t(24, y, note, 9, MUTED))
    b.append(t(24, y + 14, "A mark compares a capture with the one before it. A gap between captures is not a change."
               + (" Dashed: copy not readable (a script-built or near-empty page)." if unread else ""), 9, MUTED))
    h = y + 14 + 70
    used = {st for cap in caps for st in cap["sections"].values()}
    legend = [(lambda x, yy: f'<path d="M {x + 8} {yy} L {x + 14} {yy + 6} L {x + 8} {yy + 12} L {x + 2} {yy + 6} Z" fill="{LAV}" '
               f'stroke="{INK}" stroke-width="1.2"/>', "top change · focal"),
              (lambda x, yy: f'<path d="M {x + 8} {yy} L {x + 14} {yy + 6} L {x + 8} {yy + 12} L {x + 2} {yy + 6} Z" fill="{PAPER}" '
               f'stroke="{INK}" stroke-width="1.2"/>', "changed since the capture before"),
              (lambda x, yy: f'<circle cx="{x + 8}" cy="{yy + 6}" r="3" fill="{PAPER}" stroke="{MUTED}" stroke-width="0.8"/>',
               "captured, no change")]
    legend = [lg for lg, keep in zip(legend, [bool(top), "changed" in used, "captured" in used]) if keep]
    if unread:
        legend.append((lambda x, yy: f'<line x1="{x + 8}" y1="{yy}" x2="{x + 8}" y2="{yy + 12}" stroke="{MUTED}" stroke-width="1" '
                       f'stroke-dasharray="4 3"/>', "copy not readable"))
    return frame(slug, c, h, b, legend)


def frame(slug, c, h, body, legend):
    """The phasis-diagram card chrome with the site_history label line (the Archive capture range)."""
    head = [t(24, 30, "SITE HISTORY", 8, MUTED, MONO, ls=".18em"), t(24, 50, c["title"], 14, INK, SANS, 700),
            t(24, 66, c["label"], 9, MUTED), f'<line x1="24" y1="78" x2="{W - 24}" y2="78" stroke="{RULE}" stroke-width="1"/>']
    ly = h - 40
    foot = [t(24, ly - 10, f'Source: {c["source_line"]}', 8, MUTED, MONO),
            f'<line x1="24" y1="{ly}" x2="{W - 24}" y2="{ly}" stroke="{RULE}" stroke-width="1"/>',
            t(24, ly + 18, "LEGEND", 8, MUTED, MONO, ls=".18em")]
    x = 90
    for swatch, label in legend:
        foot.append(swatch(x, ly + 9))
        foot.append(t(x + 22, ly + 18, label, 8.5, MUTED))
        x += 40 + int(len(label) * 4.6)
    sp = c["spec"]
    desc = (f'Timeline of {sp["counts"]["captures_used"]} Internet Archive captures of the {sp["domain"]} homepage, '
            f'with a mark where the headline, value line, nav, buttons or pricing changed, and '
            f'{len(sp["top"])} top changes quoted. {c["label"]}.')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" role="img" aria-labelledby="{slug}-title {slug}-desc" '
            f'id="svg-{slug}" class="diagram-svg" style="--canvas-width:{W}px">'
            f'<title id="{slug}-title">{e(c["title"])}</title><desc id="{slug}-desc">{e(desc)}</desc>'
            f'<style>#svg-{slug} text{{font-variant-numeric:tabular-nums}}</style>'
            f'<g aria-hidden="true" class="diagram-background"><rect width="{W}" height="{h}" fill="{PAPER}"/>'
            f'<g class="field field-editorial"/></g>' + "".join(head) + "".join(body) + "".join(foot) + "</svg>")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("result", help="the evolution-<domain>.json file written by evolution.py")
    ap.add_argument("--out", help="the SVG file to write (default: evolution-<domain>.svg next to the result)")
    a = ap.parse_args(argv)
    res = json.loads(Path(a.result).read_text())
    out = Path(a.out) if a.out else Path(a.result).with_name(f"evolution-{res['domain']}.svg")
    bad = check(res)
    caps = [c for c in res.get("captures", []) if c.get("copy")]
    if bad:
        print(json.dumps({"drawn": False, "refused": bad[:20], "refused_count": len(bad),
                          "why": "fix or leave out each refused item, then run again"}, indent=1))
        return 1
    if not caps:
        print(json.dumps({"drawn": False, "why": "no capture with copy: nothing to draw", "label": res.get("label")}))
        return 0
    c = spec(res)
    out.write_text(render(c) + "\n")
    print(json.dumps({"drawn": True, "file": str(out), "captures": len(caps), "rows": len(res["rows"]),
                      "marks_changed": sum(v == "changed" for m in c["spec"]["captures"] for v in m["sections"].values()),
                      "top": [(x["n"], x["field"], x["kind"], day(x["from"]), day(x["to"])) for x in c["spec"]["top"]],
                      "label": c["label"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
