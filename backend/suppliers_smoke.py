# suppliers_smoke.py
import argparse, json, os
import requests

def log(title, res):
    try:
        data = res.json()
    except Exception:
        data = res.text
    print(f"\n== {title} [{res.status_code}] ==")
    print(json.dumps(data, ensure_ascii=False, indent=2) if isinstance(data, (dict, list)) else data)
    return data

def get_token(base, username, password):
    r = requests.post(f"{base}/api/token/", json={"username": username, "password": password})
    data = log("TOKEN", r)
    if r.ok:
        return data["access"]
    raise SystemExit("✗ Login failed")

def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-b", "--base", default="http://127.0.0.1:8000", help="Base URL")
    ap.add_argument("-u", "--username", required=True)
    ap.add_argument("-p", "--password", required=True)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    token = get_token(base, args.username, args.password)
    H = auth_headers(token)

    # 1) Scope of Work
    sow_payload = {"code": "SOW-ELC", "name_en": "Electrical", "name_ar": "كهرباء"}
    r = requests.post(f"{base}/api/scopes-of-work/", json=sow_payload, headers=H)
    data = log("Create ScopeOfWork", r)
    sow_id = data.get("id") if r.ok else None

    # 2) Supplier Group
    grp_payload = {"code": "GRP-MAIN", "name_en": "Main Vendors", "name_ar": "الموردون الرئيسيون"}
    if sow_id: grp_payload["scope_of_work_id"] = sow_id
    r = requests.post(f"{base}/api/supplier-groups/", json=grp_payload, headers=H)
    data = log("Create SupplierGroup", r)
    grp_id = data.get("id") if r.ok else None

    # 3) Supplier (multipart لدعم ملفات لاحقًا بسهولة)
    sup_payload = {
        "code": "SUP-001",
        "name_en": "AL NOOR TRADING",
        "name_ar": "النور للتجارة",
        "email": "info@alnoor.com",
        "telephone_number": "0501112223",
        "supplier_type": "supplier",
        "supplier_history": "new",
        "company_website": "https://alnoor.example",
    }
    # علاقات
    files = {}
    data = sup_payload.copy()
    if sow_id: data["scope_of_work_id"] = str(sow_id)
    if grp_id: data["supplier_group_ids"] = [str(grp_id)]

    r = requests.post(f"{base}/api/suppliers/", headers=H, files=files, data=data)
    data = log("Create Supplier", r)
    supplier_id = data.get("id") if r.ok else None

    # 4) Contact Person
    if supplier_id:
        contact_payload = {
            "supplier": supplier_id,
            "name": "Ahmed Ali",
            "email": "ahmed@alnoor.com",
            "phone": "0503334445",
            "job_title": "Sales",
            "is_primary": True,
            "status": "active",
        }
        r = requests.post(f"{base}/api/supplier-contact-people/", json=contact_payload, headers=H)
        log("Create ContactPerson", r)

    # 5) (اختياري) Legal Person — قد تختلف الحقول عندك حسب الـ core
    if supplier_id:
        try_payloads = [
            # جرّب باسم + ايميل/تليفون لو موديلك بسيط
            {"supplier": supplier_id, "name_en": "Mohamed Saleh", "email": "legal@alnoor.com", "telephone_number": "0507778889"},
            # أو لو عندك حقول BasePerson مختلفة، ضيفها هنا وجرب
        ]
        for idx, payload in enumerate(try_payloads, 1):
            r = requests.post(f"{base}/api/supplier-legal-person/", json=payload, headers=H)
            ok = r.ok
            log(f"Create LegalPerson (try {idx})", r)
            if ok:
                break
        else:
            print("\n⚠️  Legal Person creation skipped/failed (fields likely differ in your BasePerson).")

    print("\n✅ Done. Open /admin or hit /api/suppliers/ to verify.")

if __name__ == "__main__":
    main()
