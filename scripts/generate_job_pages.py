#!/usr/bin/env python3
"""
Pre-renders static HTML pages for all jobs in jobs_data.json into /jobs/<id>.html
Provides 100% SEO-friendly, multi-page indexing on Cloudflare Pages.
"""

import json
import os
import re
import html

def generate_pages():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    json_path = os.path.join(base_dir, "jobs_data.json")
    jobs_dir = os.path.join(base_dir, "jobs")
    template_path = os.path.join(base_dir, "job.html")

    if not os.path.exists(json_path) or not os.path.exists(template_path):
        print("Missing jobs_data.json or job.html")
        return

    os.makedirs(jobs_dir, exist_ok=True)

    with open(json_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Modify relative links for /jobs/ directory
    rel_template = template.replace('href="styles.css"', 'href="../styles.css"')
    rel_template = rel_template.replace('fetch("jobs_data.json', 'fetch("../jobs_data.json')
    rel_template = rel_template.replace('href="/"', 'href="../"')

    count = 0
    for job in jobs:
        job_id = job["id"]
        # Inject the jobId directly into the page script so it loads instantly even without query param
        custom_page = rel_template.replace(
            'const jobId = urlParams.get("id");',
            f'const jobId = urlParams.get("id") || "{job_id}";'
        )
        custom_page = custom_page.replace(
            '<title id="pageTitle">विस्तृत भर्ती जानकारी | Cockroach Jobs Portal</title>',
            f'<title id="pageTitle">{html.escape(job["title"])} - ऑनलाइन फॉर्म, पात्रता एवं अधिसूचना | Cockroach Jobs</title>'
        )

        out_path = os.path.join(jobs_dir, f"{job_id}.html")
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(custom_page)
        count += 1

    print(f"[OK] Generated {count} static job pages in {jobs_dir}")

if __name__ == "__main__":
    generate_pages()
