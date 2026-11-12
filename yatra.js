/* ============================================================
   COCKROACH JOBS — Interactive Yatra (SarkariYatra journey)
   Qualification चुनो → 3 अध्यायों की निजी यात्रा:
   1) तुम्हारे लिए खुली भर्तियाँ  2) सबसे नज़दीक आख़िरी तारीख
   3) फ़ॉर्म के बाद के कदम. Data: jobs_data.json (same engine).
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Reveal-on-scroll animation ---------- */
  var io = ("IntersectionObserver" in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("revealed"); io.unobserve(e.target); } });
  }, { threshold: 0.08 }) : null;
  document.querySelectorAll(".reveal").forEach(function (el) { if (io) io.observe(el); else el.classList.add("revealed"); });

  /* ---------- Helpers ---------- */
  var LEVELS = { tenth: 1, twelfth: 2, diploma: 2, graduate: 3 };
  var MONTHS = { january:0, february:1, march:2, april:3, may:4, june:5, july:6, august:7, september:8, october:9, november:10, december:11 };

  function parseDate(str) {
    if (!str) return null;
    var s = String(str).trim();
    var m = s.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
    if (m) return new Date(+m[3], +m[2] - 1, +m[1]);
    m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) return new Date(+m[1], +m[2] - 1, +m[3]);
    m = s.match(/(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/);
    if (m && MONTHS[m[2].toLowerCase()] !== undefined) return new Date(+m[3], MONTHS[m[2].toLowerCase()], +m[1]);
    return null;
  }

  function requiredLevel(job) {
    var text = "";
    (job.vacancy_details || []).forEach(function (v) { text += " " + (v.eligibility || ""); });
    text += " " + (job.title || "") + " " + (job.short_info || "");
    text = text.toLowerCase();
    var found = [];
    if (/(10th|matric|high school|class 10|10वीं)/.test(text)) found.push(1);
    if (/(12th|intermediate|class 12|\+2|12वीं)/.test(text)) found.push(2);
    if (/(diploma|iti|polytechnic)/.test(text)) found.push(2);
    if (/(graduate|bachelor|degree|स्नातक)/.test(text)) found.push(3);
    if (/(post graduate|postgraduate|master degree|pg\b)/.test(text)) found.push(4);
    /* Boilerplate listing every level at once ("10th / 12th / Graduate ... as per
       official notification") means per-post eligibility — return null (unknown)
       instead of pretending it is open to everyone. */
    var uniq = found.filter(function (v, i) { return found.indexOf(v) === i; });
    if (uniq.length >= 3 && /as per official notification/.test(text)) return null;
    if (!found.length) return 1;
    return Math.min.apply(null, found);
  }

  function lastDateOf(job) {
    var d = job.important_dates || {};
    var keys = Object.keys(d);
    for (var i = 0; i < keys.length; i++) {
      if (/last date|अंतिम/i.test(keys[i])) { var p = parseDate(d[keys[i]]); if (p) return p; }
    }
    for (var j = 0; j < keys.length; j++) { var q = parseDate(d[keys[j]]); if (q) return q; }
    return null;
  }

  function fmtDate(d) {
    return d.getDate() + " " + ["जनवरी","फरवरी","मार्च","अप्रैल","मई","जून","जुलाई","अगस्त","सितंबर","अक्टूबर","नवंबर","दिसंबर"][d.getMonth()] + " " + d.getFullYear();
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]; }); }

  /* ---------- Controls ---------- */
  var selectedQual = "graduate";
  document.querySelectorAll(".qual-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      document.querySelectorAll(".qual-chip").forEach(function (c) { c.classList.remove("selected"); });
      chip.classList.add("selected");
      selectedQual = chip.getAttribute("data-qual");
    });
  });

  var jobsCache = null;
  function loadJobs() {
    if (jobsCache) return Promise.resolve(jobsCache);
    return fetch("jobs_data.json?v=" + Date.now()).then(function (r) { return r.json(); }).then(function (d) { jobsCache = d; return d; });
  }

  /* Fill state dropdown from data */
  loadJobs().then(function (jobs) {
    var states = {};
    jobs.forEach(function (j) { if (j.state) states[j.state] = true; });
    var sel = document.getElementById("yatraState");
    if (sel) Object.keys(states).sort().forEach(function (st) {
      if (st === "All India") return;
      var o = document.createElement("option"); o.value = st; o.textContent = st; sel.appendChild(o);
    });
  }).catch(function () {});

  function jobRow(job, badgeText, urgent) {
    return '<div class="yatra-job" onclick="window.openJobModal && openJobModal(\'' + job.id + '\')">' +
      '<div><div class="yj-title">' + esc(job.title_hi || job.title) + '</div>' +
      '<div class="yj-meta">' + esc(job.department || "") + (job.state ? " • " + esc(job.state) : "") + '</div></div>' +
      (badgeText ? '<span class="yj-badge' + (urgent ? " urgent" : "") + '">' + esc(badgeText) + '</span>' : "") + '</div>';
  }

  function startYatra() {
    var story = document.getElementById("yatraStory");
    var stateSel = document.getElementById("yatraState");
    var chosenState = stateSel ? stateSel.value : "all";
    var userLevel = LEVELS[selectedQual] || 3;
    story.innerHTML = '<p class="lead">⏳ आपकी यात्रा तैयार हो रही है…</p>';
    story.classList.add("show");

    loadJobs().then(function (jobs) {
      var now = new Date(); now.setHours(0, 0, 0, 0);
      function inState(j) { return chosenState === "all" || j.state === chosenState || j.state === "All India"; }
      var open = jobs.filter(function (j) {
        if (j.category !== "job" || !inState(j)) return false;
        var lv = requiredLevel(j);
        return lv !== null && lv <= userLevel;
      });
      var unknown = jobs.filter(function (j) {
        return j.category === "job" && inState(j) && requiredLevel(j) === null;
      });
      var byDateDesc = function (a, b) { return (parseDate(b.post_date) || 0) - (parseDate(a.post_date) || 0); };
      open.sort(byDateDesc); unknown.sort(byDateDesc);

      /* Chapter 1 */
      var ch1 = "";
      if (!open.length && !unknown.length) {
        ch1 = '<div class="yatra-empty">इस योग्यता और राज्य के लिए अभी कोई खुली भर्ती डेटाबेस में नहीं मिली। योग्यता या राज्य बदलकर फिर कोशिश करो — डेटाबेस हर घंटे अपडेट होता है।</div>';
      } else {
        if (open.length) {
          ch1 += '<p class="lead">आपकी योग्यता के हिसाब से <strong>' + open.length + ' भर्तियाँ</strong> पक्के तौर पर खुली हैं। सबसे ताज़ा ये रहीं — किसी पर भी क्लिक करो, पूरा विवरण खुलेगा:</p>' +
            open.slice(0, 8).map(function (j) { return jobRow(j, "विवरण देखो →", false); }).join("");
        }
        if (unknown.length) {
          ch1 += '<p class="lead" style="margin-top:14px;">इसके अलावा <strong>' + unknown.length + ' भर्तियाँ</strong> ऐसी हैं जिनमें हर पद की पात्रता अलग-अलग है — इनमें तुम्हारे लायक पद हो सकता है, खोलकर जाँचो:</p>' +
            unknown.slice(0, 4).map(function (j) { return jobRow(j, "पात्रता जाँचो →", false); }).join("");
        }
      }

      /* Chapter 2 */
      var dated = open.map(function (j) { return { job: j, date: lastDateOf(j) }; })
        .filter(function (x) { return x.date && x.date >= now; })
        .sort(function (a, b) { return a.date - b.date; });
      var ch2 = "";
      if (dated.length) {
        ch2 = '<p class="lead">समय सबसे कीमती है। इनकी आख़िरी तारीख सबसे पहले आ रही है:</p>' + dated.slice(0, 3).map(function (x) {
          var days = Math.round((x.date - now) / 86400000);
          var label = days <= 0 ? "आज आख़िरी दिन!" : ("सिर्फ़ " + days + " दिन बचे • " + fmtDate(x.date));
          return jobRow(x.job, label, days <= 7);
        }).join("");
      } else {
        ch2 = '<p class="lead">इन भर्तियों की आख़िरी तारीख नोटिफ़िकेशन में अलग से दी गई है — किसी भर्ती को खोलकर "महत्वपूर्ण तिथियां" ज़रूर देखो।</p>';
      }

      /* Chapter 3 */
      var admitCount = jobs.filter(function (j) { return j.category === "admit_card"; }).length;
      var resultCount = jobs.filter(function (j) { return j.category === "result"; }).length;
      var ch3 = '<p class="lead">फ़ॉर्म भरना सिर्फ़ शुरुआत है। आगे का रास्ता ऐसा दिखेगा:</p>' +
        '<ol class="yatra-steps">' +
        '<li>📄 <strong>दस्तावेज़ तैयार रखो:</strong> फोटो, हस्ताक्षर, आधार, जाति/आय प्रमाण पत्र और योग्यता की मार्कशीट की स्कैन कॉपी।</li>' +
        '<li>🖱️ <strong>आवेदन सिर्फ़ आधिकारिक लिंक से</strong> करो — भर्ती खोलने पर नीचे सीधे .gov.in लिंक मिलता है।</li>' +
        '<li>🎟️ <strong>फिर एडमिट कार्ड:</strong> साइट पर अभी ' + admitCount + ' एडमिट कार्ड लाइव हैं — <a href="#admit-cards">यहाँ देखो</a>।</li>' +
        '<li>🏆 <strong>आख़िर में परिणाम:</strong> अभी ' + resultCount + ' परिणाम घोषित हैं — <a href="#results">यहाँ देखो</a>।</li>' +
        '</ol>' +
        '<p class="lead" style="margin-top:10px;">यही आपकी कहानी है — योग्यता से नौकरी तक। हर घंटे नई भर्तियाँ जुड़ती हैं, कल फिर आकर देखना। 🪳</p>';

      story.innerHTML =
        '<div class="chapter" style="animation-delay:0s"><div class="chapter-num">1</div><h3>अध्याय 1 — तुम्हारे लिए खुली भर्तियाँ</h3>' + ch1 + '</div>' +
        '<div class="chapter" style="animation-delay:0.25s"><div class="chapter-num">2</div><h3>अध्याय 2 — सबसे नज़दीक आख़िरी तारीख</h3>' + ch2 + '</div>' +
        '<div class="chapter" style="animation-delay:0.5s"><div class="chapter-num">3</div><h3>अध्याय 3 — फ़ॉर्म के बाद का रास्ता</h3>' + ch3 + '</div>';
      story.querySelectorAll(".chapter").forEach(function (c) { c.classList.add("play"); });
      story.scrollIntoView({ behavior: "smooth", block: "start" });
    }).catch(function () {
      story.innerHTML = '<div class="yatra-empty">डेटा लोड नहीं हो पाया। पेज को एक बार फिर से लोड करके कोशिश करो।</div>';
    });
  }

  var btn = document.getElementById("yatraStartBtn");
  if (btn) btn.addEventListener("click", startYatra);
})();
