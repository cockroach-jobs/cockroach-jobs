#!/usr/bin/env python3
"""
Cockroach Jobs Portal - OFFICIAL-ONLY Auto-Updater (v2, LOYATI rebuild, Nov 2026)

Owner's rule: NO aggregator websites (no SarkariResult, no FreeJobAlert, nothing similar).
Every listing on this portal comes ONLY from an official government source:
  - The notice page of a government authority (SSC, UPSC, IBPS, state commissions, boards)
  - The ORIGINAL notification PDF hosted on the authority's own / .gov.in / .nic.in domain
Cards carry the official apply link, the original notification PDF link and the
official website. Details (dates, fees, posts, eligibility) are extracted from the
official PDF text itself; anything not found is honestly marked
"आधिकारिक नोटिफ़िकेशन देखें" instead of being invented.

State: scripts/official_seen.json remembers first-seen dates of notification URLs,
so hourly runs only add genuinely new notices and old official entries persist.
"""

import urllib.request
import urllib.parse
import json
import re
import html
import os
import sys
import io
import time
import hashlib
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

BASE_DIR = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(BASE_DIR, "jobs_data.json")
SEEN_PATH = os.path.join(SCRIPT_DIR, "official_seen.json")

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    'Referer': 'https://www.google.com/'
}

AUTHORITIES = {
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
    },
    "CENTRAL_INDIA_POST": {
        "dept": "India Post (Department of Posts)",
        "tag": "India Post",
        "state": "All India",
        "apply_url": "https://www.indiapost.gov.in",
        "notice_url": "https://www.indiapost.gov.in",
        "official_site": "https://www.indiapost.gov.in"
    },
    "CENTRAL_ARMY": {
        "dept": "Indian Army (Join Indian Army)",
        "tag": "Army",
        "state": "All India",
        "apply_url": "https://joinindianarmy.nic.in",
        "notice_url": "https://joinindianarmy.nic.in",
        "official_site": "https://joinindianarmy.nic.in"
    },
    "CENTRAL_SBI": {
        "dept": "State Bank of India (SBI)",
        "tag": "SBI",
        "state": "All India",
        "apply_url": "https://sbi.co.in/web/careers",
        "notice_url": "https://sbi.co.in/web/careers",
        "official_site": "https://sbi.co.in"
    },
    "CENTRAL_RBI": {
        "dept": "Reserve Bank of India (RBI)",
        "tag": "RBI",
        "state": "All India",
        "apply_url": "https://opportunities.rbi.org.in",
        "notice_url": "https://opportunities.rbi.org.in",
        "official_site": "https://www.rbi.org.in"
    },
    "DELHI_DSSSB": {
        "dept": "Delhi Subordinate Services Selection Board (DSSSB)",
        "tag": "DSSSB",
        "state": "Delhi",
        "apply_url": "https://dsssb.delhi.gov.in",
        "notice_url": "https://dsssb.delhi.gov.in",
        "official_site": "https://dsssb.delhi.gov.in"
    },
    "CENTRAL_ESIC": {
        "dept": "Employees State Insurance Corporation (ESIC)",
        "tag": "ESIC",
        "state": "All India",
        "apply_url": "https://www.esic.gov.in/recruitments",
        "notice_url": "https://www.esic.gov.in/recruitments",
        "official_site": "https://www.esic.gov.in"
    }
}

MAX_NEW_PER_RUN = 60
MAX_NEW_PER_AUTHORITY = 12
MAX_TOTAL = 500
PDF_MAX_BYTES = 8 * 1024 * 1024
SKIP_WORDS = ('tender', 'e-tender', 'auction', 'quotation', 'eoi', 'expression of interest', 'corrigendum to tender')
# A PDF becomes a listing ONLY with a positive recruitment/exam signal in its
# label, filename or path — this keeps RTI docs, FAQs, certificates, circulars
# and speaking orders out of the portal.
POSITIVE_WORDS = ('advert', 'advt', 'recruit', 'vacanc', 'notification', 'vigyapti', 'विज्ञप्ति',
                  'भर्ती', 'result', 'परिणाम', 'answer key', 'answerkey', 'admit', 'प्रवेश पत्र',
                  'examination', 'exam notice', 'online application', 'combined graduate',
                  'combined higher', 'constable', 'sub inspector', 'clerk', 'assistant', 'officer')
JUNK_WORDS = ('rti', 'faq', 'innovation', 'accessibility', 'conformance', 'speaking order',
              'circular', 'annual report', 'press release', 'newsletter', 'minutes of',
              'tender', 'auction', 'quotation', 'eoi', 'corrigendum', 'budget speech')
CATEGORY_PATHS = ('/result', '/answerkey', '/answer-key', '/advert', '/recruit', '/vacancy', '/notice')

def relevance(label, pdf_url):
    """Return True only for genuine recruitment/exam/result documents."""
    text = ((label or '') + ' ' + urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(pdf_url).path))).lower()
    path = urllib.parse.urlparse(pdf_url).path.lower()
    has_positive = any(w in text for w in POSITIVE_WORDS) or any(p in path for p in CATEGORY_PATHS)
    if not has_positive:
        return False
    has_junk = any(w in text for w in JUNK_WORDS)
    has_category = any(w in text for w in ('result', 'परिणाम', 'answer key', 'answerkey', 'admit',
                                           'recruit', 'advert', 'vacanc', 'vigyapti', 'भर्ती'))
    if has_junk and not has_category:
        return False
    # Bare administrative labels like "notice no 212" carry no information.
    if re.fullmatch(r'(notice|order|circular|letter)[\s\w]{0,16}', (label or '').strip().lower()):
        return False
    return True

def quote_url(url):
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc,
                                    urllib.parse.quote(parts.path), parts.query, parts.fragment))

# ----------------------------- fetching -----------------------------

def fetch(url, timeout=20, max_bytes=None):
    try:
        req = urllib.request.Request(url, headers=BROWSER_HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read(max_bytes + 1 if max_bytes else -1)
            if max_bytes and len(data) > max_bytes:
                return None
            return data
    except Exception as e:
        print(f"    [fetch fail] {url[:90]} -> {type(e).__name__}")
        return None

def host_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:
        return ""

def official_host_ok(url, authority):
    """A link counts as official only if it lives on the authority's own host,
    a subdomain of it, or any .gov.in / .nic.in host."""
    h = host_of(url)
    if not h:
        return False
    own = host_of(authority.get("official_site", ""))
    if h == own or (own and h.endswith("." + own)):
        return True
    return h.endswith(".gov.in") or h.endswith(".nic.in") or h == "gov.in" or h == "nic.in"

ANCHOR_RE = re.compile(r'<a\s+[^>]*href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)

def extract_pdf_links(page_url, authority):
    data = fetch(page_url)
    if not data:
        return []
    try:
        text = data.decode('utf-8', errors='ignore')
    except Exception:
        return []
    out = []
    for href, label in ANCHOR_RE.findall(text):
        href = href.strip()
        if not href or href.startswith(('#', 'javascript:', 'mailto:')):
            continue
        full = urllib.parse.urljoin(page_url, href)
        if not full.lower().split('?')[0].endswith('.pdf'):
            continue
        if not official_host_ok(full, authority):
            continue
        label = re.sub(r'<[^>]+>', ' ', label)
        label = html.unescape(re.sub(r'\s+', ' ', label)).strip()
        out.append((quote_url(full), label))
    return out

def discover_notice_pages(home_url, authority, limit=3):
    """Depth-1 discovery: from the authority homepage, follow internal links
    whose address smells like advertisements / recruitment / what's new."""
    data = fetch(home_url)
    if not data:
        return []
    text = data.decode('utf-8', errors='ignore')
    pages = []
    for href, label in ANCHOR_RE.findall(text):
        h = (href or '').strip().lower()
        if not h or h.startswith(('#', 'javascript:', 'mailto:')) or h.endswith('.pdf'):
            continue
        if not any(k in h for k in ('advert', 'recruit', 'vacancy', 'whatsnew', 'whats-new', 'notices', 'career')):
            continue
        full = urllib.parse.urljoin(home_url, href.strip())
        if host_of(full) != host_of(home_url):
            continue
        if full not in pages:
            pages.append(full)
        if len(pages) >= limit:
            break
    return pages

# ----------------------------- text mining -----------------------------

MONTHS = {m: i + 1 for i, m in enumerate(['january','february','march','april','may','june',
    'july','august','september','october','november','december'])}
DATE_PATTERNS = [
    re.compile(r'(\d{1,2})[./\-](\d{1,2})[./\-](\d{4})'),
    re.compile(r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s*,?\s*(\d{4})', re.I),
    re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})\s*,?\s*(\d{4})', re.I),
]

def find_date(s):
    if not s:
        return None
    for idx, pat in enumerate(DATE_PATTERNS):
        m = pat.search(s)
        if not m:
            continue
        g = m.groups()
        try:
            if idx == 0:
                d = datetime(int(g[2]), int(g[1]), int(g[0]))
            elif idx == 1:
                d = datetime(int(g[2]), MONTHS[g[1].lower()], int(g[0]))
            else:
                d = datetime(int(g[2]), MONTHS[g[0].lower()], int(g[1]))
            if 2023 <= d.year <= 2032:
                return d.strftime('%d/%m/%Y')
        except Exception:
            continue
    return None

def window_after(text, keywords, size):
    low = text.lower()
    for kw in keywords:
        i = low.find(kw)
        if i >= 0:
            return text[i:i + size]
    return ""

def extract_pdf_text(pdf_bytes):
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for page in reader.pages[:6]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return re.sub(r'\s+', ' ', ' '.join(parts))
    except Exception:
        return ""

def mine_details(text):
    det = {}
    if not text:
        return det
    last_win = window_after(text, ['last date', 'closing date', 'अंतिम तिथि', 'last date of receipt',
                                   'last date for submission', 'last date for online application'], 200)
    d = find_date(last_win)
    if d:
        det['last_date'] = d
    start_win = window_after(text, ['starting date', 'start date', 'opening date', 'commencement of online application'], 160)
    d2 = find_date(start_win)
    if d2:
        det['start_date'] = d2
    fee_win = window_after(text, ['application fee', 'examination fee', 'आवेदन शुल्क'], 420)
    if fee_win:
        amounts = re.findall(r'(?:₹|Rs\.?|INR)\s*([\d,]+)', fee_win)
        if amounts:
            det['fee_general'] = '₹' + amounts[0]
        elif re.search(r'\bnil\b|no fee|शुल्क नहीं', fee_win, re.I):
            det['fee_general'] = 'कोई शुल्क नहीं (Nil)'
    m = re.search(r'([\d,]{2,7})\s*(?:posts|vacancies|पदों|पद\b)', text, re.I)
    if m:
        try:
            n = int(m.group(1).replace(',', ''))
            if 0 < n <= 300000:
                det['total_posts'] = f"{n:,}"
        except Exception:
            pass
    elig_win = window_after(text, ['educational qualification', 'eligibility', 'qualification required'], 260)
    if elig_win:
        det['eligibility'] = elig_win.strip()[:240]
    age_win = window_after(text, ['age limit', 'आयु सीमा'], 200)
    if age_win:
        det['age'] = age_win.strip()[:200]
    return det

# ----------------------------- listing build -----------------------------

def slugify(text):
    s = re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')
    return s[:64] or 'notice'

def clean_title(label, pdf_url, authority):
    t = (label or '').strip()
    junk = {'', 'click here', 'here', 'download', 'pdf', 'view', 'details', 'link', 'new'}
    if t.lower() in junk or len(t) < 12:
        name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(pdf_url).path))
        name = re.sub(r'\.pdf$', '', name, flags=re.I)
        name = re.sub(r'[_+]+', ' ', name)
        name = re.sub(r'-{2,}', ' ', name)
        t = re.sub(r'\s+', ' ', name).strip()
    if len(t) < 12:
        t = f"{authority['dept']} - Official Notification"
    return t[:180]

def classify(title):
    t = (title or '').lower()
    if 'result' in t or 'परिणाम' in t or 'merit list' in t or 'cut off' in t or 'cutoff' in t:
        return 'result'
    if 'admit card' in t or 'hall ticket' in t or 'प्रवेश पत्र' in t or 'e-admit' in t:
        return 'admit_card'
    if 'answer key' in t or 'उत्तर कुंजी' in t:
        return 'answer_key'
    if 'syllabus' in t:
        return 'syllabus'
    if 'admission' in t:
        return 'admission'
    return 'job'

def title_is_meaningful(title):
    """A listing we cannot honestly name is worse than no listing:
    blocks CMS path fragments ('CMS\\Recruitment\\IO'), bare admin labels
    ('notice no 212') and the generic fallback title."""
    if not title or '\\' in title:
        return False
    if len(title) < 18:
        return False
    if title.endswith('- Official Notification'):
        return False
    if re.fullmatch(r'(notice|order|circular|letter)[\s\w]{0,16}', title.strip().lower()):
        return False
    return True

def build_listing(authority, pdf_url, label, first_seen, details, title=None):
    title = title or clean_title(label, pdf_url, authority)
    uid = hashlib.md5(pdf_url.encode()).hexdigest()[:6]
    dates = {"Notification Date": first_seen}
    if details.get('start_date'):
        dates["Apply Start Date"] = details['start_date']
    dates["Apply Last Date"] = details.get('last_date', 'आधिकारिक नोटिफ़िकेशन देखें')
    dates["Exam Date"] = "Will be notified soon"
    fee = {
        "General / OBC / EWS": details.get('fee_general', 'आधिकारिक नोटिफ़िकेशन देखें'),
        "SC / ST / PwD": 'आधिकारिक नोटिफ़िकेशन देखें'
    }
    return {
        "id": slugify(authority['tag'] + ' ' + title) + '-' + uid,
        "title": title,
        "title_hi": title,
        "department": authority['dept'],
        "category": classify(title),
        "tag": authority['tag'],
        "state": authority.get('state', 'All India'),
        "is_hot": False,
        "post_date": first_seen,
        "short_info": (f"{authority['dept']} की आधिकारिक वेबसाइट पर जारी नोटिफ़िकेशन। "
                       f"पूरी और सही जानकारी के लिए नीचे दिया आधिकारिक PDF देखें — "
                       f"स्रोत: {authority['official_site']} (केवल आधिकारिक स्रोत)।"),
        "important_dates": dates,
        "application_fee": fee,
        "age_limit": details.get('age', 'आधिकारिक नोटिफ़िकेशन के अनुसार (PDF देखें)'),
        "vacancy_details": [{
            "post_name": title[:90],
            "total": (details.get('total_posts', 'Various') + " Posts") if details.get('total_posts') else "Various Posts",
            "eligibility": details.get('eligibility', 'आधिकारिक नोटिफ़िकेशन देखें — PDF लिंक नीचे दिया है।')
        }],
        "links": {
            "primary_action": "⚡ आधिकारिक वेबसाइट से आवेदन / विवरण देखें",
            "primary_url": authority.get('apply_url') or authority['official_site'],
            "notification_pdf": pdf_url,
            "notification_url": pdf_url,
            "syllabus_url": "",
            "official_website": authority['official_site']
        },
        "source": "official",
        "source_url": authority.get('notice_url') or authority['official_site']
    }

# ----------------------------- main -----------------------------

def main():
    today_str = datetime.now().strftime('%d/%m/%Y')

    seen = {}
    if os.path.exists(SEEN_PATH):
        try:
            seen = json.load(open(SEEN_PATH, encoding='utf-8'))
        except Exception:
            seen = {}

    existing = []
    if os.path.exists(JSON_PATH):
        try:
            existing = json.load(open(JSON_PATH, encoding='utf-8'))
        except Exception:
            existing = []
    # CLEAN BREAK: only official-sourced entries survive. All aggregator-era
    # entries are dropped here (git history preserves them if ever needed).
    kept = [j for j in existing if j.get('source') == 'official']
    dropped = len(existing) - len(kept)
    print(f"[*] Existing entries: {len(existing)} | official kept: {len(kept)} | aggregator-era dropped: {dropped}")
    known_urls = {j['links']['notification_pdf'] for j in kept if j.get('links', {}).get('notification_pdf')}
    known_urls |= set(seen.keys())

    new_listings = []
    for key, authority in AUTHORITIES.items():
        if len(new_listings) >= MAX_NEW_PER_RUN:
            break
        page = authority.get('notice_url') or authority['official_site']
        print(f"[*] {authority['tag']}: scanning {page}")
        links = extract_pdf_links(page, authority)
        good = [x for x in links if relevance(x[1], x[0])]
        if len(good) < 3:
            extra_pages = []
            if page != authority['official_site']:
                extra_pages.append(authority['official_site'])
            extra_pages += discover_notice_pages(authority['official_site'], authority)
            for ep in extra_pages:
                if len(good) >= 6:
                    break
                more = extract_pdf_links(ep, authority)
                good += [x for x in more if relevance(x[1], x[0]) and x not in good]
            links = good
        else:
            links = good
        added_here = 0
        for pdf_url, label in links:
            if len(new_listings) >= MAX_NEW_PER_RUN or added_here >= MAX_NEW_PER_AUTHORITY:
                break
            if pdf_url in known_urls:
                continue
            probe = (label + ' ' + pdf_url).lower()
            if any(w in probe for w in SKIP_WORDS):
                continue
            title_probe = clean_title(label, pdf_url, authority)
            if not title_is_meaningful(title_probe):
                continue
            seen[pdf_url] = today_str
            known_urls.add(pdf_url)
            pdf_bytes = fetch(pdf_url, timeout=25, max_bytes=PDF_MAX_BYTES)
            details = mine_details(extract_pdf_text(pdf_bytes)) if pdf_bytes else {}
            new_listings.append(build_listing(authority, pdf_url, label, today_str, details, title_probe))
            added_here += 1
            time.sleep(0.4)
        print(f"    -> {added_here} new official notices")

    final = new_listings + kept
    # newest first by post_date
    def pdate(j):
        try:
            return datetime.strptime(j.get('post_date', '01/01/2020'), '%d/%m/%Y')
        except Exception:
            return datetime(2020, 1, 1)
    final.sort(key=pdate, reverse=True)
    final = final[:MAX_TOTAL]
    for idx, item in enumerate(final):
        item['is_hot'] = idx < 8

    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    with open(SEEN_PATH, 'w', encoding='utf-8') as f:
        json.dump(seen, f, indent=1, ensure_ascii=False)
    print(f"[OK] jobs_data.json now holds {len(final)} OFFICIAL-ONLY listings ({len(new_listings)} new this run).")

    try:
        import generate_job_pages
        generate_job_pages.generate_pages()
    except Exception as e:
        print(f"[-] Warning generating static pages: {e}")
    try:
        import generate_sitemap
        generate_sitemap.generate_sitemap()
    except Exception as e:
        print(f"[-] Warning generating sitemap: {e}")
    print("[SUCCESS] Official-only update complete.")

if __name__ == "__main__":
    main()
