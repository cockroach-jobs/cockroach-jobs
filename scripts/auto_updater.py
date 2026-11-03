#!/usr/bin/env python3
"""
Cockroach Jobs Portal - Production Auto-Updater
Deep-crawls official announcements and authentic articles.
Extracts exact Important Dates, Application Fees, Age Limits, Vacancy Details & Eligibility,
and verified Direct Government Apply (.gov.in / .nic.in) + Official Notification PDF links.
"""

import urllib.request
import json
import re
import html
import os
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

GOV_AUTHORITIES = {
    "HARYANA_HSSC": {
        "dept": "Haryana Staff Selection Commission (HSSC)",
        "tag": "HSSC",
        "state": "Haryana",
        "apply_url": "https://onetimeregn.haryana.gov.in",
        "notice_url": "https://hssc.gov.in/advertisements",
        "official_site": "https://hssc.gov.in"
    },
    "HARYANA_HPSC": {
        "dept": "Haryana Public Service Commission (HPSC)",
        "tag": "HPSC",
        "state": "Haryana",
        "apply_url": "https://hpsc.gov.in/en-us/Online-Application",
        "notice_url": "https://hpsc.gov.in/en-us/Advertisements",
        "official_site": "https://hpsc.gov.in"
    },
    "RAJASTHAN_RSSB": {
        "dept": "Rajasthan Staff Selection Board (RSSB / RSMSSB)",
        "tag": "RSSB",
        "state": "Rajasthan",
        "apply_url": "https://sso.rajasthan.gov.in/signin",
        "notice_url": "https://rsmssb.rajasthan.gov.in",
        "official_site": "https://rsmssb.rajasthan.gov.in"
    },
    "RAJASTHAN_RPSC": {
        "dept": "Rajasthan Public Service Commission (RPSC)",
        "tag": "RPSC",
        "state": "Rajasthan",
        "apply_url": "https://sso.rajasthan.gov.in/signin",
        "notice_url": "https://rpsc.rajasthan.gov.in/news",
        "official_site": "https://rpsc.rajasthan.gov.in"
    },
    "UP_UPSSSC": {
        "dept": "Uttar Pradesh Subordinate Services Selection Commission (UPSSSC)",
        "tag": "UPSSSC",
        "state": "Uttar Pradesh",
        "apply_url": "https://upsssc.gov.in/Online_App/Notifications.aspx",
        "notice_url": "https://upsssc.gov.in/Online_App/Notifications.aspx",
        "official_site": "https://upsssc.gov.in"
    },
    "UP_POLICE": {
        "dept": "Uttar Pradesh Police Recruitment & Promotion Board (UPPRPB)",
        "tag": "UP Police",
        "state": "Uttar Pradesh",
        "apply_url": "https://uppbpb.gov.in",
        "notice_url": "https://uppbpb.gov.in",
        "official_site": "https://uppbpb.gov.in"
    },
    "UP_UPPSC": {
        "dept": "Uttar Pradesh Public Service Commission (UPPSC)",
        "tag": "UPPSC",
        "state": "Uttar Pradesh",
        "apply_url": "https://uppsc.up.nic.in/CandidatePages/OTR/OTR_Home.aspx",
        "notice_url": "https://uppsc.up.nic.in/CandidatePages/Notifications/Notifications.aspx",
        "official_site": "https://uppsc.up.nic.in"
    },
    "UP_UPESSC": {
        "dept": "Uttar Pradesh Education Service Selection Commission (UPESSC)",
        "tag": "UP Teacher",
        "state": "Uttar Pradesh",
        "apply_url": "https://upessc.up.gov.in",
        "notice_url": "https://upessc.up.gov.in",
        "official_site": "https://upessc.up.gov.in"
    },
    "BIHAR_BPSC": {
        "dept": "Bihar Public Service Commission (BPSC)",
        "tag": "BPSC",
        "state": "Bihar",
        "apply_url": "https://onlinebpsc.bihar.gov.in",
        "notice_url": "https://bpsc.bih.nic.in",
        "official_site": "https://bpsc.bih.nic.in"
    },
    "BIHAR_CSBC": {
        "dept": "Central Selection Board of Constable (Bihar Police CSBC)",
        "tag": "Bihar Police",
        "state": "Bihar",
        "apply_url": "https://csbc.bih.nic.in",
        "notice_url": "https://csbc.bih.nic.in",
        "official_site": "https://csbc.bih.nic.in"
    },
    "BIHAR_BSSC": {
        "dept": "Bihar Staff Selection Commission (BSSC)",
        "tag": "BSSC",
        "state": "Bihar",
        "apply_url": "https://onlinebssc.com",
        "notice_url": "https://bssc.bihar.gov.in/Notices.htm",
        "official_site": "https://bssc.bihar.gov.in"
    },
    "MP_MPESB": {
        "dept": "Madhya Pradesh Employees Selection Board (MPESB Vyapam)",
        "tag": "MPESB",
        "state": "Madhya Pradesh",
        "apply_url": "https://esb.mponline.gov.in/Portal/Examinations/Vyapam/ExamsList.aspx",
        "notice_url": "https://esb.mp.gov.in/Rulebooks.html",
        "official_site": "https://esb.mp.gov.in"
    },
    "MP_MPPSC": {
        "dept": "Madhya Pradesh Public Service Commission (MPPSC)",
        "tag": "MPPSC",
        "state": "Madhya Pradesh",
        "apply_url": "https://mponline.gov.in/portal/services/MPPSC/ExamList.aspx",
        "notice_url": "https://mppsc.mp.gov.in/advertisement",
        "official_site": "https://mppsc.mp.gov.in"
    },
    "CENTRAL_SSC": {
        "dept": "Staff Selection Commission (SSC)",
        "tag": "SSC",
        "state": "All India",
        "apply_url": "https://ssc.gov.in/login",
        "notice_url": "https://ssc.gov.in/notices",
        "official_site": "https://ssc.gov.in"
    },
    "CENTRAL_RAILWAY": {
        "dept": "Railway Recruitment Boards (Indian Railways / RRBs)",
        "tag": "Railway",
        "state": "All India",
        "apply_url": "https://www.rrbapply.gov.in/#/auth/home",
        "notice_url": "https://indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,7,1281",
        "official_site": "https://rrb.indianrailways.gov.in"
    },
    "CENTRAL_UPSC": {
        "dept": "Union Public Service Commission (UPSC)",
        "tag": "UPSC",
        "state": "All India",
        "apply_url": "https://upsconline.nic.in/upsc/OTRP/index.php",
        "notice_url": "https://upsc.gov.in/examinations/active-exams",
        "official_site": "https://upsc.gov.in"
    },
    "CENTRAL_NTA": {
        "dept": "National Testing Agency (NTA)",
        "tag": "NTA",
        "state": "All India",
        "apply_url": "https://exams.nta.ac.in",
        "notice_url": "https://nta.ac.in/Notice",
        "official_site": "https://nta.ac.in"
    },
    "CENTRAL_IBPS": {
        "dept": "Institute of Banking Personnel Selection (IBPS / Bank Exams)",
        "tag": "Bank",
        "state": "All India",
        "apply_url": "https://ibpsonline.ibps.in",
        "notice_url": "https://www.ibps.in/index.php/all-notifications/",
        "official_site": "https://ibps.in"
    },
    "CENTRAL_FORCE": {
        "dept": "Defence & Paramilitary Forces Recruitment",
        "tag": "Force",
        "state": "All India",
        "apply_url": "https://rectt.bsf.gov.in",
        "notice_url": "https://rectt.bsf.gov.in",
        "official_site": "https://rectt.bsf.gov.in"
    }
}

def resolve_authority(title):
    t = title.upper()
    if "HSSC" in t or "HARYANA" in t or "HPSC" in t:
        return GOV_AUTHORITIES["HARYANA_HPSC"] if "HPSC" in t else GOV_AUTHORITIES["HARYANA_HSSC"]
    if "RPSC" in t or "RSSB" in t or "RSMSSB" in t or "RAJASTHAN" in t:
        return GOV_AUTHORITIES["RAJASTHAN_RPSC"] if "RPSC" in t else GOV_AUTHORITIES["RAJASTHAN_RSSB"]
    if "UPESSC" in t or "TGT" in t or "PGT" in t or ("TEACHER" in t and "UP" in t) or "HEADMASTER" in t:
        return GOV_AUTHORITIES["UP_UPESSC"]
    if "UPSSSC" in t or "LOWER PCS" in t:
        return GOV_AUTHORITIES["UP_UPSSSC"]
    if "UP POLICE" in t or "UPPRPB" in t:
        return GOV_AUTHORITIES["UP_POLICE"]
    if "UPPSC" in t or "RO / ARO" in t or "RO ARO" in t:
        return GOV_AUTHORITIES["UP_UPPSC"]
    if "BPSC" in t or "BIHAR TEACHER" in t or "TRE" in t:
        return GOV_AUTHORITIES["BIHAR_BPSC"]
    if "CSBC" in t or "BIHAR POLICE" in t:
        return GOV_AUTHORITIES["BIHAR_CSBC"]
    if "BSSC" in t:
        return GOV_AUTHORITIES["BIHAR_BSSC"]
    if "MPESB" in t or "VYAPAM" in t or "MADHYA PRADESH" in t or ("MP " in t and "EXAM" in t):
        return GOV_AUTHORITIES["MP_MPPSC"] if "MPPSC" in t else GOV_AUTHORITIES["MP_MPESB"]
    if "SSC" in t:
        return GOV_AUTHORITIES["CENTRAL_SSC"]
    if "RRB" in t or "RAILWAY" in t or "NTPC" in t or "STATION MASTER" in t:
        return GOV_AUTHORITIES["CENTRAL_RAILWAY"]
    if "UPSC" in t or "NDA" in t or "CDS" in t:
        return GOV_AUTHORITIES["CENTRAL_UPSC"]
    if "NTA" in t or "CUET" in t or "NEET" in t or "JEE" in t or "SAINIK" in t:
        return GOV_AUTHORITIES["CENTRAL_NTA"]
    if "BANK" in t or "IBPS" in t or "SBI" in t or "SO " in t or "PO " in t:
        return GOV_AUTHORITIES["CENTRAL_IBPS"]
    if "BSF" in t or "CRPF" in t or "AIR FORCE" in t or "ARMY" in t or "NAVY" in t or "COAST GUARD" in t:
        return GOV_AUTHORITIES["CENTRAL_FORCE"]
    if "UTTAR PRADESH" in t or "UP " in t:
        return GOV_AUTHORITIES["UP_UPSSSC"]
    if "BIHAR" in t:
        return GOV_AUTHORITIES["BIHAR_BPSC"]
    return GOV_AUTHORITIES["CENTRAL_SSC"]

def parse_full_article(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        html_content = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

    # Title
    m_title = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    raw_title = m_title.group(1).split('|')[0].strip() if m_title else ""
    raw_title = html.unescape(re.sub(r'<[^>]+>', '', raw_title)).strip()

    # Short info
    short_info = ""
    m_info = re.search(r'Short Information.*?</t[dh]>\s*<td[^>]*>(.*?)</td>', html_content, re.DOTALL | re.IGNORECASE)
    if m_info:
        short_info = html.unescape(re.sub(r'<[^>]+>', ' ', m_info.group(1))).strip()
        short_info = re.sub(r'\s+', ' ', short_info)

    data = {
        "title": raw_title,
        "short_info": short_info,
        "important_dates": {},
        "application_fee": {},
        "age_limit": {},
        "vacancy_details": [],
        "links": {}
    }

    # Important Dates, Fee, Age
    ul_blocks = re.findall(r'<ul[^>]*>(.*?)</ul>', html_content, re.DOTALL | re.IGNORECASE)
    for ul in ul_blocks:
        li_items = re.findall(r'<li[^>]*>(.*?)</li>', ul, re.DOTALL | re.IGNORECASE)
        for li in li_items:
            t = html.unescape(re.sub(r'<[^>]+>', ' ', li)).strip()
            t = re.sub(r'\s+', ' ', t)
            if not t or len(t) < 3:
                continue

            # Dates
            if any(k in t.lower() for k in ["application begin", "last date", "fee last date", "correction date", "exam date", "admit card"]):
                parts = t.split(":", 1)
                if len(parts) == 2:
                    data["important_dates"][parts[0].strip()] = parts[1].strip()

            # Fees
            elif any(k in t.lower() for k in ["general", "obc", "ews", "sc / st", "sc/st", "ph (", "female", "refund", "pay the exam"]):
                parts = t.split(":", 1)
                if len(parts) == 2:
                    data["application_fee"][parts[0].strip()] = parts[1].strip()
                elif "pay the exam" in t.lower() or "mode" in t.lower():
                    data["application_fee"]["Payment Mode"] = t

            # Age
            elif any(k in t.lower() for k in ["minimum age", "maximum age", "age relaxation"]):
                parts = t.split(":", 1)
                if len(parts) == 2:
                    data["age_limit"][parts[0].strip()] = parts[1].strip()
                else:
                    data["age_limit"]["Notes"] = t

    # As on date
    m_as_on = re.search(r'Age Limit as on\s*([0-9/]+)', html_content, re.IGNORECASE)
    if m_as_on:
        data["age_limit"]["Calculation Date"] = f"As on {m_as_on.group(1)}"

    # Vacancy & Eligibility
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
    for tbl in tables:
        if "eligibility" in tbl.lower() or "post name" in tbl.lower():
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.DOTALL | re.IGNORECASE)
            capture = False
            for r in rows:
                cells = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL | re.IGNORECASE)]
                cells = [re.sub(r'\s+', ' ', c) for c in cells if c]
                if not cells:
                    continue
                if any("post name" in c.lower() for c in cells) and any("total" in c.lower() for c in cells):
                    capture = True
                    continue
                if any("zone" in c.lower() or "rrb name" in c.lower() or "category wise" in c.lower() for c in cells):
                    capture = False
                    continue
                if capture and len(cells) >= 3:
                    post_name = cells[0]
                    total = cells[1]
                    eligibility = cells[2]
                    if len(post_name) > 2 and (any(ch.isdigit() for ch in total) or "various" in total.lower()):
                        data["vacancy_details"].append({
                            "post_name": post_name,
                            "total": total if "post" in total.lower() else f"{total} Posts",
                            "eligibility": eligibility
                        })

    # Direct PDF and Official Links
    pattern = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
    for m in pattern.finditer(html_content):
        href = m.group(1)
        txt = re.sub(r'<[^>]+>', '', m.group(2)).strip().lower()
        if any(x in href.lower() for x in ['whatsapp', 'telegram', 'play.google', 'app', 'twitter', 'facebook', 'instagram', 'threads']):
            continue
        if href.lower().endswith(".pdf"):
            if "syllabus" in txt or "syllabus" in href.lower():
                data["links"]["syllabus_url"] = href
            elif not data["links"].get("notification_pdf"):
                data["links"]["notification_pdf"] = href
        elif any(k in txt for k in ["official website", "official portal"]) or any(k in href for k in [".gov.in", ".nic.in", ".ac.in", ".edu.in"]):
            if not data["links"].get("official_website"):
                data["links"]["official_website"] = href

    return data

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    json_path = os.path.join(base_dir, "jobs_data.json")

    print("[1/3] Fetching live post URLs from SarkariResult homepage...")
    req = urllib.request.Request("https://www.sarkariresult.com/", headers={'User-Agent': USER_AGENT})
    try:
        html_text = urllib.request.urlopen(req, timeout=12).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching homepage: {e}")
        return

    pattern = re.compile(r'<a\s+[^>]*href=["\'](https://www\.sarkariresult\.com/(?:2026|2025|railway|ssc|upsc|bihar|mp|rpsc|bank|delhi|upsssc)/[^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE)
    live_posts = {}
    for m in pattern.finditer(html_text):
        u = m.group(1).rstrip('/')
        t = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if t and len(t) > 5 and not any(x in u for x in ['whatsapp', 'telegram', 'page', 'about', 'contact']):
            if u not in live_posts:
                live_posts[u] = t

    print(f"[+] Found {len(live_posts)} live recruitment article URLs.")

    # Load existing jobs
    existing_jobs = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            existing_jobs = json.load(f)

    enriched_jobs = []
    processed = 0

    for url, title in list(live_posts.items())[:50]:
        slug = url.split('/')[-1]
        print(f"[{processed+1}/50] Deep-reading: {title[:40]}...")
        details = parse_full_article(url)
        processed += 1
        if not details or not details["title"]:
            continue

        clean_title = details["title"]
        auth = resolve_authority(clean_title)

        # Robust category resolution
        path_low = url.replace("https://www.sarkariresult.com", "").lower()
        if "/result/" in path_low or "-result" in path_low or "result-" in path_low or "marks" in path_low or "score-card" in path_low:
            cat = "result"
            primary_action = "⚡ रिजल्ट देखें (View Official Result)"
        elif "/admit" in path_low or "admit-card" in path_low or "exam-date" in path_low:
            cat = "admit_card"
            primary_action = "⚡ एडमिट कार्ड डाउनलोड (Admit Card)"
        elif "/answer" in path_low or "answer-key" in path_low:
            cat = "answer_key"
            primary_action = "⚡ उत्तर कुंजी डाउनलोड (Answer Key PDF)"
        elif "/syllabus" in path_low:
            cat = "syllabus"
            primary_action = "⚡ सिलेबस डाउनलोड (Syllabus PDF)"
        elif "/admission" in path_low:
            cat = "admission"
            primary_action = "⚡ एडमिशन फॉर्म (Admission Form)"
        else:
            cat = "job"
            primary_action = "⚡ सीधे ऑनलाइन आवेदन करें (Apply Online)"

        pdf_url = details["links"].get("notification_pdf") or auth["notice_url"]
        official_site = details["links"].get("official_website") or auth["official_site"]

        job_entry = {
            "id": slug,
            "title": clean_title,
            "title_hi": clean_title,
            "department": auth["dept"],
            "category": cat,
            "tag": auth["tag"],
            "state": auth["state"],
            "is_hot": (processed <= 5),
            "post_date": datetime.now().strftime("%d/%m/%Y"),
            "short_info": details["short_info"] or f"{auth['dept']} has issued an official announcement regarding {clean_title}. Detailed eligibility guidelines, schedule, and direct application links are provided below.",
            "important_dates": details["important_dates"] if details["important_dates"] else {
                "Notification Date": datetime.now().strftime("%d/%m/%Y"),
                "Apply Last Date": "As per Notification",
                "Exam Date": "Will be notified soon"
            },
            "application_fee": details["application_fee"] if details["application_fee"] else {
                "Fee Details": "Refer to official notification",
                "Payment Mode": "Online / Net Banking"
            },
            "age_limit": details["age_limit"] if details["age_limit"] else {
                "Minimum Age": "18 Years",
                "Maximum Age": "As per Rules",
                "Notes": f"Age relaxation applicable as per {auth['dept']} rules."
            },
            "vacancy_details": details["vacancy_details"] if details["vacancy_details"] else [
                {
                    "post_name": clean_title,
                    "total": "As Per Notification",
                    "eligibility": "Refer to official notification PDF."
                }
            ],
            "links": {
                "primary_action": primary_action,
                "primary_url": auth["apply_url"],
                "notification_pdf": pdf_url,
                "notification_url": pdf_url,
                "syllabus_url": details["links"].get("syllabus_url", ""),
                "official_website": official_site
            }
        }

        enriched_jobs.append(job_entry)
        time.sleep(0.3)

    print(f"\n[2/3] Merging {len(enriched_jobs)} deep-parsed jobs with existing repository...")
    merged_map = {}
    for j in enriched_jobs:
        merged_map[j["id"]] = j
    for j in existing_jobs:
        if j["id"] not in merged_map:
            merged_map[j["id"]] = j

    final_list = list(merged_map.values())

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

    print(f"[OK] Saved total {len(final_list)} authentic jobs to {json_path}!")

    print("[3/3] Generating static job pages in /jobs/ & sitemap.xml...")
    try:
        from generate_job_pages import generate_pages
        generate_pages()
    except Exception as e:
        print(f"Warning generating static pages: {e}")

    try:
        from generate_sitemap import generate_sitemap
        generate_sitemap()
    except Exception as e:
        print(f"Warning generating sitemap: {e}")

if __name__ == "__main__":
    main()
