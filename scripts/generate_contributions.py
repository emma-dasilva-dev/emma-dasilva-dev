#!/usr/bin/env python3
"""Build an animated, blue GitHub contribution calendar as a self-contained SVG."""
import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

USERNAME = os.environ.get("GITHUB_USERNAME", "emma-dasilva-dev")
OUTPUT = Path("assets/contributions.svg")
URL = f"https://github-contributions-api.deno.dev/{USERNAME}.json"
COLORS = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#183a63",
    "SECOND_QUARTILE": "#235a98",
    "THIRD_QUARTILE": "#3186d3",
    "FOURTH_QUARTILE": "#60b7ff",
}
CELL, GAP, LEFT, TOP = 11, 3, 22, 69

def main():
    request = Request(URL, headers={"User-Agent": "emma-github-readme-calendar/1.0"})
    with urlopen(request, timeout=30) as response:
        data = json.load(response)
    weeks = data.get("contributions")
    if not isinstance(weeks, list) or not weeks:
        raise ValueError("No valid contribution weeks returned; retaining previous graphic")
    total = data.get("totalContributions", 0)
    if isinstance(total, dict):
        total = sum(v for v in total.values() if isinstance(v, int))
    width = max(700, LEFT * 2 + len(weeks) * (CELL + GAP))
    height = 216
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub contribution calendar for {escape(USERNAME)}" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style><![CDATA[',
        '.label{font:12px ui-monospace,SFMono-Regular,Consolas,monospace;fill:#8b949e}',
        '.heading{font:600 15px ui-sans-serif,system-ui,sans-serif;fill:#e6edf3}',
        '@keyframes appear{0%{opacity:0;transform:scale(.2)}100%{opacity:1;transform:scale(1)}}',
        '.day{transform-box:fill-box;transform-origin:center;animation:appear .5s cubic-bezier(.2,.8,.2,1) both}',
        '@media(prefers-reduced-motion:reduce){.day{animation:none}}',
        ']]></style>',
        f'<rect width="{width}" height="{height}" rx="12" fill="#0d1117"/>',
        f'<text x="{LEFT}" y="29" class="heading">@{escape(USERNAME)}</text>',
        f'<text x="{width-LEFT}" y="29" class="label" text-anchor="end">{escape(str(total))} contributions in the last year</text>',
        '<text x="2" y="108" class="label">M</text>',
        '<text x="2" y="136" class="label">W</text>',
        '<text x="2" y="164" class="label">F</text>',
    ]
    last_month = None
    for wi, week in enumerate(weeks):
        if not isinstance(week, list):
            raise ValueError("Unexpected contribution week format")
        for di, day in enumerate(week):
            date = day.get("date", "")
            try:
                d = dt.date.fromisoformat(date)
            except (TypeError, ValueError):
                continue
            if di == 0 and d.day <= 7 and d.month != last_month:
                parts.append(f'<text x="{LEFT + wi*(CELL+GAP)}" y="53" class="label">{d.strftime("%b")}</text>')
                last_month = d.month
            level = day.get("contributionLevel", "NONE")
            fill = COLORS.get(level, COLORS["NONE"])
            count = int(day.get("contributionCount", 0))
            x, y = LEFT + wi * (CELL + GAP), TOP + di * (CELL + GAP)
            delay = min(wi * .012 + di * .008, 1.1)
            parts.append(f'<rect class="day" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}" style="animation-delay:{delay:.3f}s"><title>{count} contributions on {escape(date)}</title></rect>')
    parts += [
        f'<text x="{LEFT}" y="198" class="label">Less</text>',
    ]
    for i, level in enumerate(COLORS):
        parts.append(f'<rect x="{LEFT + 34 + i*16}" y="187" width="11" height="11" rx="2" fill="{COLORS[level]}"/>')
    parts += [
        f'<text x="{LEFT + 120}" y="198" class="label">More</text>',
        '</svg>',
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Generated {OUTPUT}: {len(weeks)} weeks, {total} contributions")

if __name__ == "__main__":
    main()
