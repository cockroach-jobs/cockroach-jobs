# 🪳 Cockroach Jobs Portal (कॉकरोच जॉब्स पोर्टल)

> **भारत का सबसे तेज़, अटूट एवं सुपरफास्ट सरकारी नौकरी पोर्टल**  
> **Tagline:** *Unstoppable Like A Cockroach • 0% Downtime • 100% Verified Alerts*  
> **Tech Stack:** HTML5, CSS3, Vanilla JavaScript, JSON Data Engine  
> **Hosting:** Cloudflare Pages (Free Unlimited Bandwidth) + GitHub (Free Code Store)

---

## 📁 फ़ाइल संरचना (Project Directory)

```
cockroach_jobs_portal/
├── index.html           # मुख्य पोर्टल (SarkariResult 3-कॉलम + टिकर + सर्च + मोडल)
├── styles.css           # डार्क/लाइट थीम, रिस्पॉन्सिव ग्रिड, कलर-कोडेड बॉक्सेस
├── app.js               # डेटा लोडर, सर्च इंजन, 1-क्लिक मोडल, व्हाट्सएप शेयर
├── jobs_data.json       # डेटाबेस (12 असली लाइव भर्तियों का विस्तृत विवरण)
├── privacy-policy.html  # Adsterra/Monetag/AdSense कम्प्लायंस हेतु पॉलिसी
├── disclaimer.html      # गैर-सरकारी आधिकारिक अस्वीकरण (Legal Protection)
├── contact.html         # ईमेल, टेलीग्राम और व्हाट्सएप कम्युनिटी लिंक्स
└── README.md            # यह गाइड
```

---

## 🚀 Cloudflare Pages पर 2 मिनट में लाइव कैसे करें (FREE):

### स्टेप 1: GitHub पर रिपॉजिटरी बनाएं
1. [GitHub.com](https://github.com) पर लॉगिन करें।
2. **New Repository** पर क्लिक करें।
3. नाम दें: `cockroach-jobs` (Public रखें)।
4. इस फ़ोल्डर `d:\SKILL\cockroach_jobs_portal` की सभी फ़ाइलें ड्रैग-एंड-ड्रॉप करके अपलोड कर दें (या git push करें)।

### स्टेप 2: Cloudflare Pages से जोड़ें
1. [Cloudflare Dashboard](https://dash.cloudflare.com) पर जाएं।
2. बायीं तरफ **Workers & Pages** पर क्लिक करें।
3. **Create application** → **Pages** टैब चुनें।
4. **Connect to Git** पर क्लिक करके अपना `cockroach-jobs` रिपॉजिटरी चुनें।
5. Build Settings में कुछ भी बदलने की आवश्यकता नहीं है (Framework: None)।
6. **Save and Deploy** पर क्लिक करें!
7. **बधाई!** आपकी साइट **`https://cockroach-jobs.pages.dev`** (या आपके चुने गए नाम) पर लाइव हो जाएगी! 🥳

---

## 📝 नई नौकरी या परिणाम कैसे जोड़ें?

आपको कभी भी HTML या JS कोड एडिट करने की आवश्यकता नहीं है:
1. बस **`jobs_data.json`** फ़ाइल खोलें।
2. किसी भी जॉब ब्लॉक को कॉपी करके नया ऑब्जेक्ट जोड़ें:
```json
{
  "id": "new-job-2026",
  "title": "SSC CGL 2026 Online Form",
  "department": "Staff Selection Commission",
  "category": "job",
  "state": "All India",
  "important_dates": { "apply_start": "01/12/2026", "last_date": "30/12/2026" },
  "application_fee": { "gen_obc": "₹100", "sc_st": "₹0" },
  "age_limit": { "min_age": "18 Years", "max_age": "32 Years" },
  "vacancy_details": [{ "post_name": "Inspector / ASO", "total": "14,000 Posts", "eligibility": "Graduate" }],
  "links": { "primary_action": "Apply Online", "primary_url": "https://ssc.gov.in" }
}
```
3. सेव करें — आपकी साइट पर ऑटोमैटिक नया कार्ड और 3-कॉलम बॉक्स में लिंक लाइव हो जाएगा!

---

## 💰 विज्ञापन (Adsterra / Monetag / Affiliate) कैसे लगाएं?

1. `index.html` में हमने दो ख़ास स्लॉट बनाए हैं:
   * `<div class="ad-slot ad-header">` (हेडर के नीचे 728x90 बैनर)
   * `<div class="ad-slot ad-infeed">` (जॉब कार्ड्स के बीच में 300x250 या नेटिव बैनर)
2. Adsterra से मिलने वाला जावास्क्रिप्ट कोड सीधे इन `<div>` के अंदर पेस्ट कर दें।
3. लीगल पेजों (`privacy-policy.html`, `disclaimer.html`, `contact.html`) की वजह से Adsterra आपकी साइट को तुरंत अप्रूव कर देगा।

---

## 🛡️ SarkariResult से क्या बेहतर है?

* **0% लैग:** कोई भारी WordPress नहीं, 0.5 सेकंड में लोड होती है।
* **कभी डाउन नहीं होती:** Google / Cloudflare के ग्लोबल CDN पर चलती है।
* **1-Click Modal:** छात्र को 4 पेजों पर रीडायरेक्ट नहीं करती, एक क्लिक में पूरी टेबल सामने आती है।
* **WhatsApp Share:** एक क्लिक में पूरी भर्ती डिटेल दोस्तों और ग्रुप्स में शेयर हो जाती है।
