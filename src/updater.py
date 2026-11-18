"""LoLdle JS bundle + Data Dragon üzerinden otomatik güncelleme.

Birincil veri: loldle.net'in JS bundle'ına gömülü 173 kayıtlık şampiyon dizisi.
İkincil: Data Dragon (isim, başlık, tr_TR isim, ikon, patch).
"""

import hashlib
import json
import os
import re
import shutil
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (LoL champion table)"}


def _fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def loldle_index_url():
    html = _fetch("https://loldle.net/").decode("utf-8", "replace")
    m = re.search(r'(?:src|href)="([^"]*js/index\.[^"]+\.js)"', html)
    if not m:
        raise RuntimeError("loldle.net: index.js bulunamadı")
    u = m.group(1)
    return u if u.startswith("http") else "https://loldle.net/" + u.lstrip("/")


def extract_champions(js_text):
    """JS bundle'daki gömülü şampiyon dizisini çıkarır.

    Not: 'championName:' ifadesi JS'te başka bileşenlerde de geçer; bu yüzden
    veriye özgü tırnaklı 'championName:"' işareti aranır.
    """
    def q(s):
        return re.findall(r'"([^"]*)"', s)

    def parse(arr):
        out = []
        for o in re.findall(r"\{[^{}]*\}", arr):
            def f(k):
                m = re.search(k + r':("([^"]*)"|\[([^\]]*)\])', o)
                if not m:
                    return None
                return m.group(2) if m.group(2) is not None else q(m.group(3))
            out.append({"championName": f("championName"), "gender": f("gender"),
                        "positions": f("positions"), "species": f("species"),
                        "resource": f("resource"), "range_type": f("range_type"),
                        "regions": f("regions"), "release_date": f("release_date")})
        return out

    tried = []
    for marker in ('release_date:"', '_id:"', 'championName:"', 'championName":'):
        i = js_text.find(marker)
        if i < 0:
            continue
        start = js_text.rfind("[", 0, i)
        if start < 0:
            continue
        depth = 0
        end = None
        for j in range(start, len(js_text)):
            c = js_text[j]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end is None:
            continue
        try:
            out = parse(js_text[start:end])
        except Exception:
            continue
        tried.append(len(out))
        if len(out) > 50:
            return out
    raise RuntimeError(f"JS dizisi bulunamadi/çok kısa (adaylar: {tried})")


def build_champions(lol_list, dd_en, dd_tr):
    by_name = {v["name"].lower(): (k, v) for k, v in dd_en.items()}
    by_id = {k.lower(): (k, v) for k, v in dd_en.items()}
    out, unmatched = [], []
    for r in lol_list:
        nm = r["championName"]
        hit = by_name.get(nm.lower()) or by_id.get(nm.lower())
        if not hit:
            unmatched.append(nm)
            continue
        cid, c = hit
        rd = r.get("release_date")
        out.append({"id": cid, "name": c["name"], "name_tr": dd_tr.get(cid, {}).get("name", c["name"]),
                    "title": c.get("title", ""), "icon": f"assets/champions/{cid}.png",
                    "tags": c.get("tags", []), "gender": r.get("gender"),
                    "positions": r.get("positions") or [], "species": r.get("species") or [],
                    "resource": r.get("resource"), "range_type": r.get("range_type") or [],
                    "regions": r.get("regions") or [], "release_date": rd,
                    "year": int(rd[:4]) if rd else None})
    out.sort(key=lambda x: x["name"].lower())
    return out, unmatched


def update(root, progress=None):
    data_dir = os.path.join(root, "data")
    cache = os.path.join(root, "cache")
    os.makedirs(cache, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    rep = {"ok": False, "changed": False, "added": [], "removed": [], "icons": 0,
           "errors": [], "patch": None, "unmatched": []}

    def log(m):
        if progress:
            progress(m)

    meta_path = os.path.join(data_dir, "meta.json")
    prev_meta = {}
    if os.path.exists(meta_path):
        try:
            prev_meta = json.load(open(meta_path, encoding="utf-8"))
        except Exception:
            prev_meta = {}

    try:
        url = loldle_index_url()
        js = _fetch(url).decode("utf-8", "replace")
        with open(os.path.join(cache, "loldle_index.js"), "w", encoding="utf-8") as f:
            f.write(js)
        lol_list = extract_champions(js)
        log(f"LoLdle verisi: {len(lol_list)} kayıt")
    except Exception as e:
        rep["errors"].append("LoLdle: " + repr(e))
        return rep

    try:
        vers = json.loads(_fetch("https://ddragon.leagueoflegends.com/api/versions.json"))
        patch = vers[0]
        dd_en = json.loads(_fetch(f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"))["data"]
        dd_tr = json.loads(_fetch(f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/tr_TR/champion.json"))["data"]
        rep["patch"] = patch
    except Exception as e:
        rep["errors"].append("Data Dragon: " + repr(e))
        return rep

    champs, unmatched = build_champions(lol_list, dd_en, dd_tr)
    rep["unmatched"] = unmatched

    p = os.path.join(data_dir, "champions.json")
    old = {}
    if os.path.exists(p):
        try:
            old = {c["id"]: c for c in json.load(open(p, encoding="utf-8"))}
        except Exception:
            old = {}
    new_ids = {c["id"] for c in champs}
    rep["added"] = [c["name"] for c in champs if c["id"] not in old]
    rep["removed"] = [old[i]["name"] for i in old if i not in new_ids]
    changed = bool(rep["added"] or rep["removed"] or not old)
    if not changed:
        for c in champs:
            if old.get(c["id"]) != c:
                changed = True
                break
    rep["changed"] = changed

    if changed:
        backup = os.path.join(cache, "backup")
        os.makedirs(backup, exist_ok=True)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(backup, f"champions_{time.strftime('%Y%m%d_%H%M%S')}.json"))
        with open(p, "w", encoding="utf-8") as f:
            json.dump(champs, f, ensure_ascii=False, indent=1)
        log("champions.json güncellendi")

    meta = {"patch": patch, "count": len(champs), "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": ["LoLdle JS bundle (gömülü veri)", "Data Dragon", "wiki.leagueoflegends.com"],
            "loldle_js_hash": hashlib.md5(js.encode("utf-8", "replace")).hexdigest()}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    icons_dir = os.path.join(root, "assets", "champions")
    os.makedirs(icons_dir, exist_ok=True)
    redownload = prev_meta.get("patch") != patch

    def dl(c):
        path = os.path.join(icons_dir, c["id"] + ".png")
        if not redownload and os.path.exists(path) and os.path.getsize(path) > 1000:
            return 0
        try:
            data = _fetch(f"https://ddragon.leagueoflegends.com/cdn/{patch}/img/champion/{c['id']}.png")
            with open(path, "wb") as f:
                f.write(data)
            return 1
        except Exception:
            return 0

    with ThreadPoolExecutor(max_workers=8) as ex:
        rep["icons"] = sum(ex.map(dl, champs))
    rep["ok"] = True
    return rep
