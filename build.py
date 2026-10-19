#!/usr/bin/env python3
"""Rebuild index.html from products.json + src/template.html (no dependencies)."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(here, "products.json"), encoding="utf-8"))
keep = ["Product","Brand","Category","Link","Price","Why it's trending","Source","Status"]
data = []
for p in P:
    d = {k: p[k] for k in keep}
    img = f"img/{p['id']}.jpg"
    d["img"] = img if os.path.exists(os.path.join(here, img)) else ""
    data.append(d)
t = open(os.path.join(here, "src/template.html"), encoding="utf-8").read()
js = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(t.replace("__DATA__", js))
print(f"Built index.html with {len(data)} products, {sum(1 for d in data if d['img'])} images")
