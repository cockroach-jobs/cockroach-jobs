#!/usr/bin/env python3
"""
Cockroach Jobs Portal - Automated Data Synchronizer
Fetches fresh government job notices, results, and admit cards
using standard Python (no extra pip dependencies needed).
"""

import urllib.request
import json
import re
import html
import os
import sys
from datetime import datetime

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ENDPOINTS = [
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/latest-job-updates?per_page=15",
        "category": "job",
        "default_action": "Apply Online"
    },
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/admit-card-updates?per_page=15",
        "category": "admit_card",
        "default_action": "Download Admit Card"
    },
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/result-updates?per_page=15",
        "category": "result",
        "default_action": "Download Result / Score Card"
    },
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/answer-key-updates?per_page=10",
        "category": "answer_key",
        "default_action": "Download Answer Key"
    },
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/syllabus-updates?per_page=5",
        "category": "syllabus",
        "default_action": "Download Syllabus PDF"
    },
    {
        "url": "https://www.sarkariresult.com/wp-json/wp/v2/admission-updates?per_page=5",
        "category": "admission",
        "default_action": "Apply Online Admission"
    }
]

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            if res.status == 200:
                data = res.read().decode("utf-8")
                return json.loads(data)
    except Exception as e:
        print(f"[-] Error fetching {url}: {e}")
    return []

def clean_text(raw):
    if not raw:
        return ""
    text = html.unescape(raw)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_department(title):
    t = title.upper()
    if "SSC" in t:
        return "Staff Selection Commission (SSC)", "SSC"
    if "RRB" in t or "RAILWAY" in t or "RRC" in t:
        return "Railway Recruitment Board (RRB)", "Railway"
    if "UPSSSC" in t:
        return "UPSSSC (Uttar Pradesh)", "UPSSSC"
    if "UPPSC" in t:
        return "UPPSC (Uttar Pradesh)", "UPPSC"
    if "UPSC" in t:
        return "Union Public Service Commission (UPSC)", "UPSC"
    if "BPSC" in t:
        return "Bihar Public Service Commission (BPSC)", "Bihar"
    if "CSBC" in t or "BIHAR POLICE" in t:
        return "Bihar Police Recruitment Board", "Bihar"
    if "UP POLICE" in t or "UPPRPB" in t:
        return "UP Police Recruitment Board (UPPRPB)", "UP Police"
    if "BANK" in t or "IBPS" in t or "SBI" in t or "RBI" in t:
        return "Banking Recruitment", "Bank"
    if "ARMY" in t or "AIR FORCE" in t or "NAVY" in t or "BSF" in t or "CRPF" in t or "SSB" in t or "COAST GUARD" in t:
        return "Defence / Police Force", "Force"
    if "NTA" in t or "CUET" in t or "NEET" in t or "JEE" in t:
        return "National Testing Agency (NTA)", "NTA"
    if "CTET" in t or "TET" in t or "TEACHER" in t or "TRE" in t or "TGT" in t or "PGT" in t:
        return "Teaching Eligibility & Recruitment", "Teaching"
    if "DSSSB" in t:
        return "DSSSB (Delhi Govt)", "Delhi"
    if "RPSC" in t or "RSSB" in t:
        return "Rajasthan Public Service Commission", "Rajasthan"
    return "Government of India", "Govt Job"

def detect_state(title):
    t = title.upper()
    if "UP " in t or "UPSSSC" in t or "UPPSC" in t or "UTTAR PRADESH" in t:
        return "Uttar Pradesh"
    if "BIHAR" in t or "BPSC" in t or "CSBC" in t:
        return "Bihar"
    if "RAJASTHAN" in t or "RPSC" in t or "RSSB" in t:
        return "Rajasthan"
    if "DELHI" in t or "DSSSB" in t:
        return "Delhi"
    if "MP " in t or "MPESB" in t or "MADHYA PRADESH" in t:
        return "Madhya Pradesh"
    if "HSSC" in t or "HARYANA" in t:
        return "Haryana"
    return "All India"

def format_date(iso_date):
    if not iso_date:
        return datetime.now().strftime("%d/%m/%Y")
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return datetime.now().strftime("%d/%m/%Y")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    json_path = os.path.join(base_dir, "jobs_data.json")

    existing_jobs = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                existing_jobs = json.load(f)
        except Exception as e:
            print(f"[!] Warning reading existing jobs: {e}")

    existing_map = {j["id"]: j for j in existing_jobs}
    existing_titles = {clean_text(j["title"]).lower() for j in existing_jobs}

    new_jobs_count = 0
    fresh_items = []

    for ep in ENDPOINTS:
        url = ep["url"]
        category = ep["category"]
        action = ep["default_action"]
        print(f"[*] Fetching: {category} from {url}")

        items = fetch_json(url)
        print(f"    -> Received {len(items)} items")

        for item in items:
            raw_title = item.get("title", {}).get("rendered", "")
            title = clean_text(raw_title)
            if not title or len(title) < 5:
                continue

            slug = item.get("slug") or f"{category}-{item.get('id', 'item')}"
            item_id = slug

            # Check if this job already exists
            title_key = title.lower()
            if item_id in existing_map or title_key in existing_titles:
                continue

            department, tag = detect_department(title)
            state = detect_state(title)
            post_date = format_date(item.get("date"))

            # Direct link extracted from WP post
            official_link = item.get("link", "https://www.sarkariresult.com")

            entry = {
                "id": item_id,
                "title": title,
                "title_hi": title,
                "department": department,
                "category": category,
                "tag": tag,
                "state": state,
                "is_hot": (new_jobs_count < 3),
                "post_date": post_date,
                "short_info": f"{department} has issued an official announcement regarding {title}. Candidates can check eligibility criteria, important dates, and links below.",
                "important_dates": {
                    "notification_released": post_date,
                    "last_date": "Check Official Notification",
                    "exam_date": "As per Schedule"
                },
                "application_fee": {
                    "details": "Refer to official notification PDF",
                    "payment_mode": "Online"
                },
                "age_limit": {
                    "notes": "Age relaxation applicable as per board rules."
                },
                "vacancy_details": [
                    {
                        "post_name": title,
                        "total": "As Per Notification",
                        "eligibility": "Refer to official announcement rules."
                    }
                ],
                "links": {
                    "primary_action": action,
                    "primary_url": official_link,
                    "notification_url": official_link,
                    "official_website": official_link
                }
            }

            fresh_items.append(entry)
            existing_titles.add(title_key)
            existing_map[item_id] = entry
            new_jobs_count += 1

    print(f"\n[+] Total newly discovered items: {new_jobs_count}")

    if new_jobs_count > 0:
        # Prepend new items to the top
        combined_jobs = fresh_items + existing_jobs

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(combined_jobs, f, ensure_ascii=False, indent=2)

        print(f"[OK] Successfully updated {json_path} with total {len(combined_jobs)} jobs!")
    else:
        print("[=] All items are already up to date. No changes needed.")

if __name__ == "__main__":
    main()
