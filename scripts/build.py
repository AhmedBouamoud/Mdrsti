#!/usr/bin/env python3
"""
يقرأ data.json ويدمجه في index.html
"""
import json, re

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# ===== بناء LESSONS من Google Sheets =====
def make_lesson(row, level, num):
    subj_map = {
        "التاريخ": "hist",
        "الجغرافيا": "geo",
        "التربية على المواطنة": "cit",
    }
    subj = subj_map.get(row.get("المادة",""), "hist")
    title = row.get("عنوان الدرس", "")
    notion_url = row.get("رابط Notion", "")
    sem = row.get("الفصل", "")
    
    return {
        "id": f"{level}-{subj[0]}{num}",
        "num": num,
        "title": title,
        "sem": f"د{num}" if level == "3ac" else "",
        "notionUrl": notion_url,
        "summary": [{"h": "ملخص الدرس", "p": f"درس: {title} — يمكن الاطلاع على التفاصيل الكاملة في Notion."}],
        "concepts": [{"t": "مصطلح أساسي", "d": f"راجع درس {title} في Notion للاطلاع على المصطلحات."}],
        "quiz": [
            {"q": f"ما موضوع هذا الدرس؟", "opts": [title, "درس آخر", "موضوع مختلف", "لا أعرف"], "ans": 0, "exp": f"موضوع الدرس هو: {title}"}
        ]
    }

# بناء هيكل LESSONS
lessons_3ac = {"hist": [], "geo": [], "cit": []}
counters = {"التاريخ": 0, "الجغرافيا": 0, "التربية على المواطنة": 0}

for row in data.get("3ac", []):
    mat = row.get("المادة", "")
    if mat not in counters: continue
    counters[mat] += 1
    subj = {"التاريخ": "hist", "الجغرافيا": "geo", "التربية على المواطنة": "cit"}.get(mat)
    if subj:
        lessons_3ac[subj].append(make_lesson(row, "3ac", counters[mat]))

lessons_1bac = {"hist": [], "geo": []}
counters_bac = {"التاريخ": 0, "الجغرافيا": 0}

for row in data.get("1bac", []):
    mat = row.get("المادة", "")
    if mat not in counters_bac: continue
    counters_bac[mat] += 1
    subj = {"التاريخ": "hist", "الجغرافيا": "geo"}.get(mat)
    if subj:
        lessons_1bac[subj].append(make_lesson(row, "1bac", counters_bac[mat]))

lessons_js = f"""const LESSONS = {{
  '3ac': {{
    'hist': {json.dumps(lessons_3ac['hist'], ensure_ascii=False)},
    'geo': {json.dumps(lessons_3ac['geo'], ensure_ascii=False)},
    'cit': {json.dumps(lessons_3ac['cit'], ensure_ascii=False)}
  }},
  '1bac': {{
    'hist': {json.dumps(lessons_1bac['hist'], ensure_ascii=False)},
    'geo': {json.dumps(lessons_1bac['geo'], ensure_ascii=False)}
  }}
}};"""

# ===== بناء INFOS من Google Sheets =====
infos = []
for row in data.get("infographie", []):
    infos.append({
        "id": f"i{row.get('الرقم','')}",
        "title": row.get("العنوان",""),
        "cat": {
            "التاريخ":"3ac","الجغرافيا":"3ac",
            "تاريخ المغرب":"hist-maroc","المنهجية":"meth"
        }.get(row.get("الفئة",""), "3ac"),
        "emoji": "📄",
        "imgUrl": row.get("رابط الصورة",""),
        "level": row.get("المستوى","")
    })

infos_js = f"const INFOS = {json.dumps(infos, ensure_ascii=False)};"

# ===== بناء METHODOLOGIES من Google Sheets =====
meths = []
ico_map = {"تحليل الوثيقة": "📜", "الخط الزمني": "📅", "نص جغرافي": "✍️",
           "خريطة": "🗺️", "مقالي": "📝", "رسم بياني": "📊", "جدول": "📋", "امتحان": "🎯"}
for row in data.get("manhajiya", []):
    t = row.get("العنوان","")
    ico = "📐"
    for k,v in ico_map.items():
        if k in t: ico = v; break
    meths.append({
        "title": t,
        "ico": ico,
        "steps": [row.get("الوصف","")]
    })

meths_js = f"const METHODOLOGIES = {json.dumps(meths, ensure_ascii=False)};"

# ===== الإحصائيات =====
total_lessons = len(lessons_3ac['hist']) + len(lessons_3ac['geo']) + len(lessons_3ac['cit']) + len(lessons_1bac['hist']) + len(lessons_1bac['geo'])
total_infos = len(infos)

# استبدال في HTML
html = re.sub(r'const LESSONS = \{.*?\};', lessons_js, html, flags=re.DOTALL)
html = re.sub(r'const INFOS = \[.*?\];', infos_js, html, flags=re.DOTALL)
html = re.sub(r'const METHODOLOGIES = \[.*?\];', meths_js, html, flags=re.DOTALL)

# تحديث الإحصائيات
html = re.sub(r'(<div class="num">)42(</div>\s*<div class="sl">درساً)', f'\\g<1>{total_lessons}\\2', html)
html = re.sub(r'(<div class="num">)42(</div>\s*<div class="lbl">درساً)', f'\\g<1>{total_lessons}\\2', html)
html = re.sub(r'(<div class="sn">)42(</div>\s*<div class="sl">درساً)', f'\\g<1>{total_lessons}\\2', html)
html = re.sub(r'(<div class="sfn">)42(</div>\s*<div class="sfl">درساً)', f'\\g<1>{total_lessons}\\2', html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ تم بناء index.html")
print(f"   دروس 3AC: {sum(len(v) for v in lessons_3ac.values())}")
print(f"   دروس 1Bac: {sum(len(v) for v in lessons_1bac.values())}")
print(f"   إنفوغرافيك: {total_infos}")
print(f"   منهجيات: {len(meths)}")
