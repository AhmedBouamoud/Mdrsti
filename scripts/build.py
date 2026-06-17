#!/usr/bin/env python3
import json, re

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

SUBJ_MAP = {"التاريخ":"hist","الجغرافيا":"geo","التربية على المواطنة":"cit"}
SUBJ_COLOR = {"hist":"#c0392b","geo":"#27ae60","cit":"#2980b9"}

QUIZ_DEFAULT = {
    "hist": [
        {"q":"ما الموضوع الرئيسي لهذا الدرس؟","opts":["الثورة الصناعية","الإمبريالية","الحرب العالمية","النازية"],"ans":0,"exp":"راجع الدرس كاملاً في Notion للإجابة الدقيقة"},
        {"q":"في أي مادة ينتمي هذا الدرس؟","opts":["التاريخ","الجغرافيا","المواطنة","الرياضيات"],"ans":0,"exp":"هذا درس تاريخ"}
    ],
    "geo": [
        {"q":"ما الموضوع الرئيسي لهذا الدرس؟","opts":["التنمية","التضاريس","المناخ","السكان"],"ans":0,"exp":"راجع الدرس كاملاً في Notion"},
        {"q":"في أي مادة ينتمي هذا الدرس؟","opts":["الجغرافيا","التاريخ","المواطنة","العلوم"],"ans":0,"exp":"هذا درس جغرافيا"}
    ],
    "cit": [
        {"q":"ما الموضوع الرئيسي لهذا الدرس؟","opts":["المواطنة","الحقوق","الواجبات","المشاركة"],"ans":0,"exp":"راجع الدرس كاملاً في Notion"},
        {"q":"في أي مادة ينتمي هذا الدرس؟","opts":["التربية على المواطنة","التاريخ","الجغرافيا","التربية الإسلامية"],"ans":0,"exp":"هذا درس تربية على المواطنة"}
    ]
}

def make_lesson(row, level, num, subj):
    title = row.get("عنوان الدرس","")
    notion_url = row.get("رابط Notion","")
    sem = row.get("الفصل","")
    ملخص = row.get("ملخص","") or row.get("الملخص","") or ""
    مفاهيم_raw = row.get("مفاهيم","") or row.get("المفاهيم","") or ""
    
    # Build summary sections
    if ملخص:
        parts = ملخص.split("//")
        summary = []
        for i,p in enumerate(parts):
            p = p.strip()
            if ":" in p:
                h,text = p.split(":",1)
                summary.append({"h":h.strip(),"p":text.strip()})
            elif p:
                summary.append({"h":f"الفكرة {i+1}","p":p})
    else:
        summary = [
            {"h":"📌 ملخص الدرس","p":f"درس: {title}"},
            {"h":"⬛ محتوى مفصّل","p":"اضغط زر 'فتح في Notion' أعلاه للاطلاع على الملخص الكامل والمفاهيم والأمثلة."}
        ]
    
    # Build concepts
    if مفاهيم_raw:
        concepts = []
        for item in مفاهيم_raw.split("//"):
            item = item.strip()
            if ":" in item:
                t,d = item.split(":",1)
                concepts.append({"t":t.strip(),"d":d.strip()})
    else:
        concepts = [{"t":"مصطلح أساسي","d":f"راجع درس {title} في Notion للاطلاع على المصطلحات الكاملة."}]
    
    return {
        "id": f"{level}-{subj[0]}{num}",
        "num": num,
        "title": title,
        "sem": f"د{num}",
        "notionUrl": notion_url,
        "summary": summary,
        "concepts": concepts,
        "quiz": QUIZ_DEFAULT.get(subj, QUIZ_DEFAULT["hist"])
    }

# Build 3AC lessons
lessons_3ac = {"hist":[],"geo":[],"cit":[]}
counters = {"التاريخ":0,"الجغرافيا":0,"التربية على المواطنة":0}
for row in data.get("3ac",[]):
    mat = row.get("المادة","")
    if mat not in counters: continue
    counters[mat] += 1
    subj = SUBJ_MAP.get(mat)
    if subj:
        lessons_3ac[subj].append(make_lesson(row,"3ac",counters[mat],subj))

# Build 1Bac lessons
lessons_1bac = {"hist":[],"geo":[]}
counters_bac = {"التاريخ":0,"الجغرافيا":0}
for row in data.get("1bac",[]):
    mat = row.get("المادة","")
    if mat not in counters_bac: continue
    counters_bac[mat] += 1
    subj = SUBJ_MAP.get(mat,"hist")
    if subj in lessons_1bac:
        lessons_1bac[subj].append(make_lesson(row,"1bac",counters_bac[mat],subj))

# Build INFOS
infos = []
CAT_MAP = {"التاريخ":"3ac","الجغرافيا":"3ac","تاريخ المغرب":"hist-maroc","المنهجية":"meth"}
EMOJI_MAP = {"التاريخ":"📜","الجغرافيا":"🌍","تاريخ المغرب":"🇲🇦","المنهجية":"📐"}
for row in data.get("infographie",[]):
    cat = row.get("الفئة","")
    infos.append({
        "id": f"i{row.get('الرقم','')}",
        "title": row.get("العنوان",""),
        "cat": CAT_MAP.get(cat,"3ac"),
        "emoji": EMOJI_MAP.get(cat,"📄"),
        "imgUrl": row.get("رابط الصورة",""),
        "level": row.get("المستوى","")
    })

# Build METHODOLOGIES
meths = []
ICO = {"وثيقة":"📜","زمني":"📅","جغراف":"✍️","خريطة":"🗺️","مقالي":"📝","بياني":"📊","جدول":"📋","امتحان":"🎯"}
for row in data.get("manhajiya",[]):
    t = row.get("العنوان","")
    desc = row.get("الوصف","")
    ico = "📐"
    for k,v in ICO.items():
        if k in t: ico=v; break
    # Parse steps from description
    steps = [s.strip() for s in desc.split("،") if s.strip()] if desc else [desc]
    meths.append({"title":t,"ico":ico,"steps":steps})

# Build JS
lessons_js = f"""const LESSONS = {{
  '3ac': {{
    'hist': {json.dumps(lessons_3ac['hist'],ensure_ascii=False)},
    'geo': {json.dumps(lessons_3ac['geo'],ensure_ascii=False)},
    'cit': {json.dumps(lessons_3ac['cit'],ensure_ascii=False)}
  }},
  '1bac': {{
    'hist': {json.dumps(lessons_1bac['hist'],ensure_ascii=False)},
    'geo': {json.dumps(lessons_1bac['geo'],ensure_ascii=False)}
  }}
}};"""

infos_js = f"const INFOS = {json.dumps(infos,ensure_ascii=False)};"
meths_js = f"const METHODOLOGIES = {json.dumps(meths,ensure_ascii=False)};"

# Stats
total = sum(len(v) for v in lessons_3ac.values()) + sum(len(v) for v in lessons_1bac.values())

# Replace in HTML — only when sheets actually returned data
if total > 0:
    html = re.sub(r'const LESSONS = \{.*?\};', lessons_js, html, flags=re.DOTALL)
else:
    print("⚠️  بيانات الدروس فارغة من Google Sheets — المحتوى الحالي في index.html محفوظ")

if infos:
    html = re.sub(r'const INFOS = \[.*?\];', infos_js, html, flags=re.DOTALL)
else:
    print("⚠️  بيانات الإنفوغرافيك فارغة — المحتوى الحالي محفوظ")

if meths:
    html = re.sub(r'const METHODOLOGIES = \[.*?\];', meths_js, html, flags=re.DOTALL)
else:
    print("⚠️  بيانات المنهجيات فارغة — المحتوى الحالي محفوظ")

# Update stats
for pattern, repl in [
    (r'(splash-stat[^>]*>.*?<div class="num">)42(</div>)', f'\\g<1>{total}\\2'),
    (r'(<div class="sn">)42(</div>\s*<div class="sl">درساً)', f'\\g<1>{total}\\2'),
    (r'(<div class="sfn">)42(</div>\s*<div class="sfl">درساً)', f'\\g<1>{total}\\2'),
]:
    html = re.sub(pattern, repl, html, flags=re.DOTALL)

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print(f"✅ index.html بُني بنجاح")
print(f"   3AC: تاريخ={len(lessons_3ac['hist'])} جغرافيا={len(lessons_3ac['geo'])} مواطنة={len(lessons_3ac['cit'])}")
print(f"   1Bac: تاريخ={len(lessons_1bac['hist'])} جغرافيا={len(lessons_1bac['geo'])}")
print(f"   إنفوغرافيك={len(infos)} منهجيات={len(meths)}")
