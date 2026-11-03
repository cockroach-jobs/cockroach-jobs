#!/usr/bin/env python3
"""
Cockroach Jobs Portal - Production XML Sitemap Generator
Automatically generates compliant sitemap.xml with home, agency hubs, legal pages,
and all 130+ individual job URLs with exact timestamps for rapid Google indexing.
"""

import json
import os
from datetime import datetime

DOMAIN = "https://cockroachjobsportal.pages.dev"

def generate_sitemap():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    json_path = os.path.join(base_dir, "jobs_data.json")
    catalog_path = os.path.join(base_dir, "exam_catalog.json")
    sitemap_path = os.path.join(base_dir, "sitemap.xml")

    today = datetime.now().strftime("%Y-%m-%d")

    urls = []

    # 1. Homepage (Top Priority)
    urls.append({
        "loc": f"{DOMAIN}/",
        "lastmod": today,
        "changefreq": "always",
        "priority": "1.0"
    })

    # 2. Agency Hubs (High Priority)
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        for agency_id, agency in catalog.get("agencies", {}).items():
            slug = agency.get("slug", "ssc")
            urls.append({
                "loc": f"{DOMAIN}/agency.html?id={slug}",
                "lastmod": today,
                "changefreq": "daily",
                "priority": "0.9"
            })
            # Also static agency path
            urls.append({
                "loc": f"{DOMAIN}/agencies/{slug}.html",
                "lastmod": today,
                "changefreq": "daily",
                "priority": "0.85"
            })

    # 3. All Live Jobs & Notifications
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
        for job in jobs:
            job_id = job.get("id")
            if not job_id:
                continue
            urls.append({
                "loc": f"{DOMAIN}/job.html?id={job_id}",
                "lastmod": today,
                "changefreq": "hourly",
                "priority": "0.8"
            })
            urls.append({
                "loc": f"{DOMAIN}/jobs/{job_id}.html",
                "lastmod": today,
                "changefreq": "hourly",
                "priority": "0.8"
            })

    # 4. Legal Compliance Pages
    for legal in ["privacy-policy", "disclaimer", "contact"]:
        urls.append({
            "loc": f"{DOMAIN}/{legal}",
            "lastmod": today,
            "changefreq": "monthly",
            "priority": "0.4"
        })

    # Build XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for u in urls:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{u["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{u["lastmod"]}</lastmod>')
        xml_lines.append(f'    <changefreq>{u["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{u["priority"]}</priority>')
        xml_lines.append('  </url>')

    xml_lines.append('</urlset>')

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))

    print(f"[OK] Successfully generated sitemap.xml with {len(urls)} URLs at {sitemap_path}")

if __name__ == "__main__":
    generate_sitemap()
