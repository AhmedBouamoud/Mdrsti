#!/usr/bin/env python3
"""
يقرأ Google Sheets ويولّد ملف data.json للموقع
"""
import json, urllib.request, csv, io, sys

SHEETS = {
    "3ac":  "1AfvzuwlVJ5T5E4wV86gE7yDefL_BQk2KlVa9FccIi4g",
    "1bac": "1Rz4Wif8pSwB7E0ulcCVM0933Poa0PoAeeT8DcQGPX2U",
    "manhajiya": "1D1RDpYA2XnjAuBCyYlTRlsPjYwOs_NRr30CKggvSsuA",
    "infographie": "1de8IlX_t05ymVetHCvOK2g36fIaYWx3nvTXdUylnmgo",
}

def fetch_csv(sheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return r.read().decode("utf-8-sig")
    except Exception as e:
        print(f"⚠️ خطأ في جلب {sheet_id}: {e}", file=sys.stderr)
        return ""

def parse_csv(text):
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        rows.append({k.strip(): v.strip() for k, v in row.items() if k})
    return rows

data = {}
for key, sid in SHEETS.items():
    print(f"📥 جلب {key}...")
    text = fetch_csv(sid)
    if text:
        rows = parse_csv(text)
        data[key] = rows
        print(f"   ✅ {len(rows)} سطر")
    else:
        data[key] = []

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ تم توليد data.json")
print(f"   3AC: {len(data.get('3ac',[]))} درس")
print(f"   1Bac: {len(data.get('1bac',[]))} درس")
print(f"   منهجية: {len(data.get('manhajiya',[]))} عنصر")
print(f"   إنفوغرافيك: {len(data.get('infographie',[]))} عنصر")
