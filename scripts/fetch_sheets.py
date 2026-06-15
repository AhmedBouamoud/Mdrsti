#!/usr/bin/env python3
"""يقرأ Google Sheets ويولّد data.json"""
import json, urllib.request, csv, io, sys

SHEETS = {
    "3ac":  "1PITPOxTO83DdOLdn-oFz-_RBwqu1eZwzESDcDMqgi6w",
    "1bac": "1YfVByIBWridKn_Y3w82AweRZeAqmAgcmyQehTJB4W_Q",
    "manhajiya": "1KrJjKXXnlAoJTpR-fMtVlcH0Yy0FslFAiZAW2qR9Jbg",
    "infographie": "1Ri2-Tr4-VtWjasceV5XmxTHVi9S8qLfOaYEDMRjyQA4",
}

def fetch_csv(sheet_id):
    urls = [
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8-sig")
        except Exception as e:
            print(f"   محاولة فشلت: {e}", file=sys.stderr)
    return ""

def parse_csv(text):
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        rows.append({k.strip(): (v.strip() if v else "") for k, v in row.items() if k})
    return rows

data = {}
for key, sid in SHEETS.items():
    print(f"جلب {key}...")
    text = fetch_csv(sid)
    if text:
        rows = parse_csv(text)
        data[key] = rows
        print(f"   تم {len(rows)} سطر")
    else:
        data[key] = []
        print(f"   تعذر الجلب - تأكد أن الجدول عام")

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nالمجموع: 3AC={len(data.get('3ac',[]))} 1Bac={len(data.get('1bac',[]))} منهجية={len(data.get('manhajiya',[]))} إنفوغرافيك={len(data.get('infographie',[]))}")
