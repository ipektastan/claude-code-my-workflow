#!/usr/bin/env python3
"""Convert a Claude Code session log (.jsonl) into a readable Markdown file.

Usage:  python transcript_to_md.py session.jsonl [output.md]
Keeps the original file untouched. Shows who spoke, the text, each tool call
(with its input) and each tool result (shortened if very long).
"""
import json, sys, os

MAX_RESULT = 1500  # characters of each tool result to show

def blocks(content):
    if isinstance(content, str):
        yield ("text", content)
        return
    for b in content or []:
        if not isinstance(b, dict):
            yield ("text", str(b)); continue
        t = b.get("type")
        if t == "text":
            yield ("text", b.get("text", ""))
        elif t == "tool_use":
            yield ("tool_use", json.dumps({"tool": b.get("name"), "input": b.get("input")}, indent=2, ensure_ascii=False))
        elif t == "tool_result":
            c = b.get("content")
            if isinstance(c, list):
                c = "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
            c = str(c)
            if len(c) > MAX_RESULT:
                c = c[:MAX_RESULT] + f"\n... [shortened, {len(c)} characters in total]"
            yield ("tool_result", c)
        # other block types (e.g. internal reasoning) are skipped

def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".md"
    out, n = [f"# Transcript: {os.path.basename(src)}\n"], 0
    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try: rec = json.loads(line)
            except json.JSONDecodeError: continue
            msg = rec.get("message")
            if not isinstance(msg, dict): continue
            role = msg.get("role") or rec.get("type") or "?"
            ts = rec.get("timestamp", "")
            for kind, text in blocks(msg.get("content")):
                if not text.strip(): continue
                n += 1
                if kind == "text":
                    out.append(f"\n## {role.upper()}  {ts}\n\n{text}\n")
                elif kind == "tool_use":
                    out.append(f"\n**TOOL CALL**\n```json\n{text}\n```\n")
                else:
                    out.append(f"\n**TOOL RESULT**\n```\n{text}\n```\n")
    with open(dst, "w", encoding="utf-8") as f:
        f.write("".join(out))
    print(f"Wrote {dst} ({n} entries)")

main()
