#!/usr/bin/env python3
"""Check the quotes of an answer before it is sent. Standard library only, no network.

Archived copy appears in quotation marks only inside the quote block that quote_block.py writes (between its start and
end markers). Inside the block, a quote must be a whole field value of a capture, a change row or a value run, or the
start of such a value cut at a word boundary and ended with an ellipsis; a double quote inside a value counts as an
apostrophe. Any quote outside the block is refused: the prose may describe a change, but it never quotes. With --block,
the block in the answer must equal quotes.md.

Usage: python3 -I check_quotes.py answer.md evolution-<domain>.json [more result files] [--block quotes.md]
Prints a JSON summary. Exit 0 when every quote is allowed; exit 1 when something is refused: fix it and run again.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evolution as ev  # noqa: E402

QUOTE = re.compile(r"[\"“]([^\"“”\n]{1,400})[\"”]")
START = "<!-- evolution-quotes:start (paste unchanged) -->"
END = "<!-- evolution-quotes:end -->"


def inner(s):
    """A double quote inside a value becomes an apostrophe (as quote_block.py writes it), so QUOTE reads it whole."""
    return ev.norm(s).replace('"', "'")


def values(res):
    out = {inner(res.get("label", ""))}
    for c in res.get("captures", []):
        for v in (c.get("copy") or {}).values():
            out.update(inner(x) for x in (v if isinstance(v, list) else [v]) if isinstance(x, str))
    for r in res.get("rows", []):
        out.update({inner(r["before"]), inner(r["after"])})
    for rr in res.get("runs", {}).values():
        out.update(inner(x["value"]) for x in rr if x.get("value"))
    return {v for v in out if v}


def split(answer):
    """(the block, the rest of the answer). A block is the text from START to END, markers included."""
    i, j = answer.find(START), answer.find(END)
    if i < 0 or j < i:
        return "", answer
    j += len(END)
    return answer[i:j], answer[:i] + answer[j:]


def check(answer, results, block=None):
    vals = set()
    for res in results:
        vals |= values(res)
    inside, outside = split(answer)
    refused = [{"quote": q, "why": "quote outside the copy block: describe it without quotation marks, or use the block"}
               for q in QUOTE.findall(outside)]
    qs = QUOTE.findall(inside)
    refused += [{"quote": q, "why": "not a whole value or the start of one (cut at a word boundary, with an ellipsis)"}
                for q in qs if not ev.quote_ok(q, vals)]
    if block is not None and ev.norm(inside) != ev.norm(block.strip()):
        refused.append({"quote": None, "why": "the copy block is missing or changed: paste quotes.md unchanged"})
    return {"quotes": len(qs) + len(QUOTE.findall(outside)), "allowed": len(qs) - sum(r["quote"] in qs for r in refused),
            "refused": refused}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    block = None
    if "--block" in argv:
        k = argv.index("--block")
        block = Path(argv[k + 1]).read_text()
        del argv[k:k + 2]
    if len(argv) < 2:
        print(__doc__)
        return 2
    out = check(Path(argv[0]).read_text(), [json.loads(Path(f).read_text()) for f in argv[1:]], block)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if out["refused"] else 0


if __name__ == "__main__":
    sys.exit(main())
