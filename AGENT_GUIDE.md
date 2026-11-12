# AGENT GUIDE — Cockroach Jobs Portal automation

यह फ़ाइल किसी भी AI agent के लिए है जो इस system को आगे चलाए। मालिक (SUNDER) का
Android app ("Jobs Panel") और यह repo मिलकर पूरा system बनाते हैं। Muse के
tokens ख़त्म हो जाएँ या agent बदल जाए, तो नया agent सिर्फ़ यह guide पढ़कर और
repo की write-पहुँच लेकर काम जारी रख सकता है — मालिक को कुछ दोबारा समझाना
नहीं पड़ेगा।

## System क्या है

- **Live site:** https://cockroachjobsportal.pages.dev — सरकारी भर्तियों के cards
  (भर्ती / Admit Card / Result / Answer Key), सरल हिंदी में।
- **Repo:** github.com/cockroach-jobs/cockroach-jobs (public) — इस repo में push
  होते ही Cloudflare Pages site को अपने आप deploy कर देता है।
- **jobs_data.json** — site का असली data। हर item का schema:
  `id, cat (job|admit|result|answer_key), title, org, posts, qual
  (10वीं|12वीं|ITI|Diploma|Graduate), state, salary, feeGen, feeText, age,
  startDate, lastDate, examDate (ISO तारीख़ या null), isNew, breakup
  [[पद, संख्या, योग्यता], ...], selection [कदम...], docs [दस्तावेज़...],
  applyUrl, pdfUrl, siteUrl, sourceUrl, blogSteps (optional)`
- **panel_state.json** — app और agent के बीच की साझा कतार (नीचे देखो)।
  यही फ़ाइल इस guide के साथ repo में रहती है।
- **Android app (Jobs Panel)** — मालिक के phone पर: site की live भर्तियाँ,
  जानकारी भेजना (submissions), तैयार कतार देखना और upload के लिए queue करना।
  App इस repo के `panel_state.json` को GitHub API से पढ़ता/लिखता है (मालिक का
  अपना GitHub token सिर्फ़ उसके phone पर रहता है)।

## मालिक के सख़्त नियम (कभी मत तोड़ो)

1. **Data सिर्फ़ आधिकारिक स्रोत से:** card की जानकारी असली सरकारी
   notification से; हर card में official notification PDF का link (pdfUrl)।
   SarkariResult/FreeJobAlert जैसी aggregator sites सिर्फ़ नई भर्तियों की
   *खोज* (discovery) के लिए हैं — card का data वहाँ से कभी मत लो।
2. **Cross-check:** हर आँकड़ा कम से कम 2 स्रोतों से जाँचो।
3. **तारीख़ का नियम:** दो तारीख़ें दिखें तो अक्सर last date बढ़ी होती है —
   card में हमेशा बढ़ी हुई **नवीनतम** तारीख़ ही आएगी; पुरानी और नई mix
   नहीं होंगी। रद्द हो चुकी घोषणा की तारीख़ें बिल्कुल नहीं।
4. **अंदाज़ से कुछ मत भरो:** जो न मिले वह `"—"` या `null`। Link सिर्फ़ सच
   में मिला हो तभी।
5. **भाषा:** सरल बोलचाल की हिंदी (देवनागरी), technical शब्दों के साथ English
   भी — जैसे "अंतिम तिथि (Last Date)"।
6. बीत चुका चरण मत डालो (last date निकल चुकी भर्ती, हो चुकी परीक्षा का
   admit card आदि)।
7. **Deploy का नियम (quota बचाने के लिए):** Cloudflare Pages free पर
   500 builds/महीना की सीमा है और repo का हर push एक build गिनता है।
   इसलिए site (jobs_data.json) **सिर्फ़ तब** बदलो जब मालिक चैट में कहे या
   उसने कोई prepared entry queue की हो (workflow B)। नई खोजी गई जानकारी
   हमेशा prepared entry बनकर कतार में लगेगी (workflow C) — सीधे site पर
   कभी नहीं। panel_state.json के बदलाव भी एक बार में एक ही commit में
   समेटो; कुछ न बदला हो तो commit ही मत करो।

## panel_state.json की बनावट

```json
{
  "version": 1,
  "updatedAt": "ISO समय",
  "submissions": [
    { "id": "sub-<समय>", "kind": "pack", "jobId": null,
      "bulkText": "मालिक की लिखी/चिपकाई जानकारी",
      "sourceUrl": "जानकारी वाले page का link",
      "fileName": "लगी file का नाम", "fileB64": "image/PDF की base64 (optional)",
      "status": "pending | prepared | applied",
      "createdAt": "ISO समय" }
  ],
  "prepared": [
    { "id": "prep-<नाम>", "kind": "new_job | update", "jobId": null,
      "title": "भर्ती का नाम",
      "fields": { "title": {"value": "...", "state": "ok"},
                  "pdfUrl": {"value": null, "state": "missing"},
                  "examDate": {"value": "2027-01-18", "state": "check"} },
      "verifyNote": "cross-check की note — स्रोत, कमी, पुष्टि बाकी",
      "status": "ready | queued | live",
      "sourceSubmissionId": "sub-... या null",
      "createdBy": "agent का नाम", "createdAt": "ISO समय" }
  ]
}
```

fields के keys: title, org, cat, posts, qual, state, startDate, lastDate,
examDate, feeGen, feeText, salary, age, applyUrl, pdfUrl, siteUrl, sourceUrl।
state के मायने: `ok` = पक्का/cross-checked, `missing` = मिली नहीं (value null),
`check` = value है पर पुष्टि बाकी (tentative आदि)।

## Agent के काम (workflow)

### A. Submissions → Prepared बनाना
1. `panel_state.json` पढ़ो; `status: "pending"` submissions लो।
2. जानकारी निकालो: bulkText पढ़ो; file लगी हो (fileB64) तो उसे decode करके
   पढ़ो (image हो तो देखकर, PDF हो तो text निकालकर); sourceUrl हो तो वह
   page खोलकर पढ़ो।
3. नियमों के हिसाब से internet से cross-check करो; जो जानकारी अधूरी हो
   (official PDF link आदि) वह खोजकर भरो।
4. `prepared` में नई entry जोड़ो (status `"ready"`), हर field का state और
   ईमानदार verifyNote के साथ। Submission का status `"prepared"` करो।
   Site पर अभी **कुछ मत डालो**।
5. बदलाव commit + push करो (message साफ़ हो, जैसे
   `panel: 2 prepared entries तैयार`)।

### B. Queued → Site पर upload
1. `prepared` में `status: "queued"` entries लो — यही मालिक की मंज़ूरी है।
2. **Dedupe पहले:** jobs_data.json में title/org मिलान से देखो — वही भर्ती
   पहले से live हो (हो सकता है यही जानकारी Muse के Jobs Update Panel से
   भी तैयार हुई हो और वहाँ से live हो गई हो), तो नया card मत बनाओ; सिर्फ़
   entry का status `"live"` करके आगे बढ़ो।
3. kind `new_job`: fields से पूरा card बनाओ — jobs_data.json schema के बचे
   fields (breakup, selection, docs) अपनी cross-check की हुई जानकारी से
   भरो; missing वाले `"—"`/null। kind `update`: सिर्फ़ `ok` state वाले
   fields उस job के record में मिलाओ।
4. jobs_data.json validate करो (सही JSON, तारीख़ें ISO), commit + push।
5. https://cockroachjobsportal.pages.dev/jobs_data.json खोलकर जाँचो कि
   बदलाव सच में live है (गिनती/नया card)।
6. Entry का status `"live"` करो, source submission हो तो उसका status
   `"applied"` करो, फिर से commit + push।
7. **Listing का समय ज़रूर लिखो (मालिक का नियम, 13 Nov 2026):** हर entry
   के status `"live"` करते समय उसी entry में `listedAt` भी जोड़ो — वह IST
   समय जब listing सच में website पर live हुई, ISO रूप में, जैसे
   `"2026-11-13T04:35:45+05:30"`। मालिक को report में भी upload का समय
   बताना है। (ध्यान: LOYATI के computer पर `TZ=Asia/Calcutta date` समय
   नहीं बदलता — UTC समय में 5 घंटे 30 मिनट जोड़कर IST बनाओ।)

### C. (Optional) हर घंटे की खोज — सिर्फ़ कतार तक, site पर नहीं
Top discovery sites (sarkariresult.com, sarkariexam.com, freejobalert.com,
rojgarresult.com, projobalert.com) की ताज़ा सूचियों से site पर न मौजूद और
कतार में भी न मौजूद नई भर्तियाँ छाँटो (एक बार में अधिकतम 5), data
YouTube video + 2-स्रोत cross-check से निकालो और हर एक की **prepared
entry `panel_state.json` में** जोड़ो (status `"ready"`, createdBy में अपना
नाम) — नियम 7 के कारण सीधे jobs_data.json में **मत** डालो। मालिक app/panel
में देखकर queue करेगा, तभी workflow B से वह site पर जाएगी।
किसी live card की last date बढ़ी (extend) हुई मिले तो jobs_data.json मत
बदलो — उस job के लिए kind `"update"` की prepared entry बनाओ (jobId = उस
job की id, fields में नई lastDate `"ok"` state के साथ, verifyNote में
पुरानी → नई तारीख़ और extension का स्रोत)।

## लिखने का शिष्टाचार
- panel_state.json और jobs_data.json हमेशा **पहले ताज़ा pull/read** करके
  बदलो, ताकि app से आए बदलाव न मिटें। JSON हमेशा valid रखो।
- एक बार में एक ही काम का commit — message से पता चले क्या हुआ।
- कुछ समझ न आए या स्रोत टकराएँ, तो मालिक को छोटा message करके पूछो —
  अंदाज़ से site मत बदलो।
