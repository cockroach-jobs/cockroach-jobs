#!/usr/bin/env python3
"""
Pre-renders static Agency Hub pages into /agencies/<slug>.html for Cloudflare Pages SEO.
"""

import json
import os
import html

def generate_agency_pages():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    cat_path = os.path.join(base_dir, "exam_catalog.json")
    template_path = os.path.join(base_dir, "agency.html")
    out_dir = os.path.join(base_dir, "agencies")

    if not os.path.exists(cat_path) or not os.path.exists(template_path):
        print("Missing exam_catalog.json or agency.html")
        return

    os.makedirs(out_dir, exist_ok=True)

    with open(cat_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    rel_template = template.replace('href="styles.css"', 'href="../styles.css"')
    rel_template = rel_template.replace('fetch("exam_catalog.json', 'fetch("../exam_catalog.json')
    rel_template = rel_template.replace('fetch("jobs_data.json', 'fetch("../jobs_data.json')
    rel_template = rel_template.replace('href="/"', 'href="../"')

    count = 0
    for agency_id, agency in catalog.get("agencies", {}).items():
        slug = agency.get("slug", "ssc")
        custom_page = rel_template.replace(
            'const agencySlug = (urlParams.get("id") || "ssc").toLowerCase();',
            f'const agencySlug = (urlParams.get("id") || "{slug}").toLowerCase();'
        )
        custom_page = custom_page.replace(
            '<title id="agencyPageTitle">भर्ती आयोग हब | Cockroach Jobs Portal</title>',
            f'<title id="agencyPageTitle">{html.escape(agency["name_hi"])} - सभी भर्तियां, OTR व कैलेंडर | Cockroach Jobs</title>'
        )

        out_path = os.path.join(out_dir, f"{slug}.html")
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(custom_page)
        count += 1

    print(f"[OK] Generated {count} static agency hub pages in {out_dir}")

if __name__ == "__main__":
    generate_agency_pages()
