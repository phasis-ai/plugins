#!/usr/bin/env python3
"""Write the archived-copy quote block of an answer from an evolution.py result file. Standard library only, no network.

The block is the only place in an answer where archived copy appears in quotation marks. Every quote in it comes from
the result file and starts at the start of its field value (a value over 104 characters is already cut at a word
boundary with an ellipsis). A double quote inside the copy is written as an apostrophe. Every quote carries its capture
date and its capture link. The script checks the block with check_quotes.py before it writes it. Paste the block into the
answer unchanged.

Sections (choose what the question needs):
  --runs     value runs, each value with its first and last capture   (default: title,h1,meta_description)
  --changes  change rows between consecutive captures                 (default: title,h1,meta_description,hero,prices)
  --fields   the copy of each capture                                 (default: none; for example buttons or h1,hero)
  --match    keep only values that contain one of these words, for --fields (for example trial,free)
Field names: title, h1 (headline), meta_description, hero (value line), h2 (section headings), nav, buttons, prices.
Give an empty value (--changes "") to leave a section out.

Usage: python3 -I quote_block.py evolution-<domain>.json [--runs ...] [--changes ...] [--fields ...] [--match ...]
Writes quotes.md next to the result file and prints it.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_quotes  # noqa: E402

START, END = check_quotes.START, check_quotes.END
NAMES = {"title": "Page title", "h1": "Headline", "meta_description": "Description", "hero": "Value line",
         "h2": "Section heading", "nav": "Nav label", "buttons": "Button", "prices": "Price"}
RUN_KEY = {"title": "title", "h1": "headline", "meta_description": "meta_description"}


def q(s):
    """A quote in double quotation marks. A double quote inside the copy becomes an apostrophe, so the quote stays whole."""
    return f"\"{check_quotes.inner(s)}\""


def cap(date, url):
    return f"captured {date} ([capture]({url}))"


def block(res, runs=("title", "h1", "meta_description"), changes=("title", "h1", "meta_description", "hero", "prices"),
          fields=(), match=()):
    out = [START, "**Archived copy** (each quote starts at the start of its field; the exact date of a change is unknown)"]
    for f in runs:
        rr = res.get("runs", {}).get(RUN_KEY.get(f, f), [])
        if not rr:
            continue
        out += ["", f"{NAMES[f]}, value by capture:"]
        for r in rr:
            span = cap(r["first_date"], r["first_url"]) + (
                "" if r["first"] == r["last"] else f" to {cap(r['last_date'], r['last_url'])}")
            n = f", {r['captures']} capture" + ("" if r["captures"] == 1 else "s")
            val = q(r["value"]) if r["known"] and r["value"] else ("none" if r["known"] else "unknown (body not readable)")
            out.append(f"- {val}, {span}{n}")
    rows = [r for r in res.get("rows", []) if r["field"] in changes]
    if rows:
        out += ["", "Changes between consecutive captures:"]
        for r in rows:
            what = {"changed": f"{q(r['before'])} to {q(r['after'])}", "added": f"added {q(r['after'])}",
                    "removed": f"removed {q(r['before'])}"}[r["kind"]]
            out.append(f"- {NAMES[r['field']]} {r['kind']} between {r['from_date']} ([capture]({r['from_url']})) and "
                       f"{r['to_date']} ([capture]({r['to_url']})): {what}")
    if fields:
        out += ["", "Copy by capture:"]
        for c in res.get("captures", []):
            cp = c.get("copy")
            if not cp:
                continue
            for f in fields:
                if not cp["readable"] and f not in ("title", "meta_description"):
                    out.append(f"- {cap(c['date'], c['snapshot_url'])}, {NAMES[f]}: unknown (body not readable)")
                    continue
                vals = cp.get(f) or []
                vals = [vals] if isinstance(vals, str) else vals
                vals = [v for v in vals if v and (not match or any(m.lower() in v.lower() for m in match))]
                text = "; ".join(q(v) for v in vals) if vals else "none"
                out.append(f"- {cap(c['date'], c['snapshot_url'])}, {NAMES[f]}: {text}")
    if len(out) == 2:
        out += ["", "- No archived copy to quote."]
    out.append(END)
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("result")
    split = lambda s: tuple(x.strip() for x in s.split(",") if x.strip())
    ap.add_argument("--runs", type=split, default=("title", "h1", "meta_description"))
    ap.add_argument("--changes", type=split, default=("title", "h1", "meta_description", "hero", "prices"))
    ap.add_argument("--fields", type=split, default=())
    ap.add_argument("--match", type=split, default=())
    a = ap.parse_args(argv)
    for f in a.runs + a.changes + a.fields:
        if f not in NAMES or (f in a.runs and f not in RUN_KEY):
            print(json.dumps({"refused": f"unknown field {f!r}", "fields": list(NAMES), "runs": list(RUN_KEY)}))
            return 2
    res = json.loads(Path(a.result).read_text())
    text = block(res, a.runs, a.changes, a.fields, a.match)
    chk = check_quotes.check(text, [res])
    if chk["refused"]:  # cannot happen with a result from evolution.py; never write an unchecked block
        print(json.dumps({"refused": chk["refused"]}, ensure_ascii=False, indent=1))
        return 1
    out = Path(a.result).with_name("quotes.md")
    out.write_text(text)
    print(text + f"\n(written to {out}; {chk['quotes']} quotes, all allowed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
