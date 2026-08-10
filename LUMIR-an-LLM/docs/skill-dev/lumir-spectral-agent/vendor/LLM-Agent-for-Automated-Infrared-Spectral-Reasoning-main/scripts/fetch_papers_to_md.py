#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 structured_papers1.json 解析文献并下载到 Papers/md。

策略（合法公开渠道）：
1. 已有 http paper_url → 抓取页面可读文本
2. 文件名含 ScienceDirect PII → 拼官方链接 + Crossref/OpenAlex 查 DOI
3. 标题检索 Crossref → Unpaywall 查 OA PDF
4. 有 OA PDF → 下载 PDF 并尽量转成 md；否则写入题录+摘要+官方链接的 stub md

不使用盗版渠道。付费全文无法下载时以 stub 标记 status=metadata_only。
"""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import certifi

ROOT = Path(__file__).resolve().parents[1]  # .../LLM-Agent-for-Automated-Infrared-Spectral-Reasoning-main
KB = ROOT / "structured_papers1.json"
OUT = ROOT / "Papers" / "md"
MANIFEST = ROOT / "Papers" / "download_manifest.json"
UA = "LUMIR-PaperFetcher/1.0 (mailto:research@example.com; academic metadata)"
SSL_CTX = ssl.create_default_context(cafile=certifi.where())

OUT.mkdir(parents=True, exist_ok=True)


def http_get(url: str, timeout: int = 45) -> Tuple[int, bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LUMIR-PaperFetcher/1.0; +https://example.com)",
            "Accept": "*/*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            return resp.status, resp.read(), resp.headers.get_content_type() or ""
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b"", ""
    except Exception as e:  # noqa: BLE001
        return 0, str(e).encode(), ""


def http_get_json(url: str) -> Optional[Any]:
    code, body, _ = http_get(url)
    if code != 200:
        return None
    try:
        return json.loads(body.decode("utf-8", errors="replace"))
    except Exception:
        return None


def target_filename(entry: Dict[str, Any]) -> str:
    u = (entry.get("paper_url") or "").replace("/", "\\")
    if u.lower().startswith("papers\\md\\"):
        return u.split("\\")[-1]
    # http 条目：用标题生成稳定文件名
    name = entry.get("paper_name") or "paper"
    slug = re.sub(r"[^\w\-]+", "_", name, flags=re.U).strip("_")
    return (slug[:100] or "paper") + ".md"


def extract_pii(fname: str) -> Optional[str]:
    m = re.search(r"1-s2\.0-(S\d+[A-Z0-9]*)-main", fname, re.I)
    return m.group(1) if m else None


def crossref_by_title(title: str) -> Optional[Dict[str, Any]]:
    q = urllib.parse.urlencode({"query.title": title, "rows": 1})
    data = http_get_json(f"https://api.crossref.org/works?{q}")
    if not data:
        return None
    items = data.get("message", {}).get("items") or []
    if not items:
        return None
    return items[0]


def crossref_by_pii_guess(pii: str) -> Optional[Dict[str, Any]]:
    # Crossref 不直接吃 PII；用 PII 当 query 碰运气
    q = urllib.parse.urlencode({"query": pii, "rows": 3})
    data = http_get_json(f"https://api.crossref.org/works?{q}")
    if not data:
        return None
    for it in data.get("message", {}).get("items") or []:
        alt = " ".join(it.get("alternative-id") or [])
        if pii in alt or pii in json.dumps(it):
            return it
    items = data.get("message", {}).get("items") or []
    return items[0] if items else None


def unpaywall(doi: str) -> Optional[Dict[str, Any]]:
    # 公开邮箱占位；Unpaywall 要求 email 参数
    email = urllib.parse.quote("lumir-fetcher@example.com")
    return http_get_json(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={email}")


def pick_oa_pdf(up: Dict[str, Any]) -> Optional[str]:
    loc = up.get("best_oa_location") or {}
    if loc.get("url_for_pdf"):
        return loc["url_for_pdf"]
    if (loc.get("url") or "").lower().endswith(".pdf"):
        return loc["url"]
    for loc in up.get("oa_locations") or []:
        if loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
    return None


def pdf_to_text(pdf_bytes: bytes, max_chars: int = 120000) -> str:
    try:
        import io
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
            if sum(len(p) for p in parts) > max_chars:
                break
        text = "\n\n".join(parts)
        return text[:max_chars]
    except Exception as e:  # noqa: BLE001
        return f"[PDF text extract failed: {e}]"


def html_to_rough_text(html: bytes) -> str:
    t = html.decode("utf-8", errors="replace")
    t = re.sub(r"(?is)<script.*?>.*?</script>", " ", t)
    t = re.sub(r"(?is)<style.*?>.*?</style>", " ", t)
    t = re.sub(r"(?is)<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()[:80000]


def format_md(entry: Dict[str, Any], meta: Dict[str, Any], body: str, status: str) -> str:
    lines = [
        "---",
        f"status: {status}",
        f"paper_name: {json.dumps(entry.get('paper_name') or '', ensure_ascii=False)}",
        f"research_object: {json.dumps(entry.get('research_object') or '', ensure_ascii=False)}",
        f"original_paper_url: {json.dumps(entry.get('paper_url') or '', ensure_ascii=False)}",
        f"resolved_doi: {json.dumps(meta.get('doi') or '', ensure_ascii=False)}",
        f"resolved_url: {json.dumps(meta.get('url') or '', ensure_ascii=False)}",
        f"oa_pdf: {json.dumps(meta.get('oa_pdf') or '', ensure_ascii=False)}",
        f"preprocessing_method: {json.dumps(entry.get('preprocessing_method') or '', ensure_ascii=False)}",
        f"feature_extracting_method: {json.dumps(entry.get('feature_extracting_method') or '', ensure_ascii=False)}",
        "---",
        "",
        f"# {entry.get('paper_name') or 'Untitled'}",
        "",
    ]
    if meta.get("authors"):
        lines += [f"**Authors:** {meta['authors']}", ""]
    if meta.get("container"):
        lines += [f"**Journal:** {meta['container']}", ""]
    if meta.get("year"):
        lines += [f"**Year:** {meta['year']}", ""]
    if meta.get("abstract"):
        lines += ["## Abstract", "", meta["abstract"], ""]
    lines += ["## Content", "", body or "_No full text available via open channels._", ""]
    return "\n".join(lines)


def parse_crossref_item(it: Dict[str, Any]) -> Dict[str, Any]:
    title = " ".join(it.get("title") or [])
    authors = []
    for a in it.get("author") or []:
        authors.append(f"{a.get('given','')} {a.get('family','')}".strip())
    abstract = it.get("abstract") or ""
    abstract = re.sub(r"<[^>]+>", "", abstract)
    issued = it.get("issued", {}).get("date-parts", [[None]])[0]
    year = issued[0] if issued else None
    url = it.get("URL")
    doi = it.get("DOI")
    container = " ".join(it.get("container-title") or [])
    return {
        "title": title,
        "authors": ", ".join(authors),
        "abstract": abstract.strip(),
        "year": year,
        "url": url,
        "doi": doi,
        "container": container,
    }


def openalex_by_title(title: str) -> Optional[Dict[str, Any]]:
    q = urllib.parse.quote(title)
    data = http_get_json(f"https://api.openalex.org/works?search={q}&per_page=3")
    if not data:
        return None
    results = data.get("results") or []
    if not results:
        return None
    # 选标题最接近的
    tnorm = re.sub(r"\W+", "", title.lower())
    best = results[0]
    best_score = 0
    for r in results:
        rt = " ".join(r.get("title") or []) if isinstance(r.get("title"), list) else (r.get("title") or "")
        rnorm = re.sub(r"\W+", "", rt.lower())
        score = len(tnorm) if tnorm and tnorm in rnorm else (10 if rnorm and rnorm in tnorm else 0)
        if score > best_score:
            best, best_score = r, score
    return best


def parse_openalex(w: Dict[str, Any]) -> Dict[str, Any]:
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    title = w.get("title") or ""
    abstract_inv = w.get("abstract_inverted_index") or {}
    abstract = ""
    if abstract_inv:
        # reconstruct
        positions: Dict[int, str] = {}
        for word, idxs in abstract_inv.items():
            for i in idxs:
                positions[i] = word
        abstract = " ".join(positions[i] for i in sorted(positions))
    loc = w.get("primary_location") or {}
    pdf = loc.get("pdf_url") or (w.get("open_access") or {}).get("oa_url")
    authors = []
    for a in w.get("authorships") or []:
        authors.append((a.get("author") or {}).get("display_name") or "")
    year = w.get("publication_year")
    container = ((loc.get("source") or {}).get("display_name")) if loc else None
    url = loc.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else None)
    return {
        "title": title,
        "authors": ", ".join([a for a in authors if a]),
        "abstract": abstract,
        "year": year,
        "url": url,
        "doi": doi,
        "container": container,
        "oa_pdf": pdf,
    }


# MDPI 期刊 slug → ISSN 路径前缀（常见）
MDPI_PREFIX = {
    "sensors": "1424-8220",
    "water": "2073-4441",
    "foods": "2304-8158",
    "biosensors": "2079-6374",
    "cancers": "2072-6694",
    "molecules": "1420-3049",
    "remotesensing": "2072-4292",
}


def guess_mdpi_pdf(fname: str) -> Optional[str]:
    # sensors-23-05149.md / cancers-14-05015-v3.md
    m = re.match(
        r"(?i)(sensors|water|foods|biosensors|cancers|molecules|remotesensing)-(\d+)-(\d+)(?:-v\d+)?\.md$",
        fname,
    )
    if not m:
        return None
    journal, vol, art = m.group(1).lower(), m.group(2), str(int(m.group(3)))
    issn = MDPI_PREFIX.get(journal)
    if not issn:
        return None
    # 常见形式 /issn/vol/issue/art/pdf 不确定 issue；改用 doi 风格检索前先试:
    # https://www.mdpi.com/xml/article?doi=... 更稳的是用 OpenAlex。
    # 备选：https://www.mdpi.com/{issn}/{vol}/{issue}/{art}/pdf — issue 未知时用通配不可行。
    # 使用 MDPI 搜索 API 不便；返回 landing 让后续 OpenAlex 处理。
    return f"https://www.mdpi.com/{issn}/{vol}/1/{art}/pdf"


def process_one(entry: Dict[str, Any]) -> Dict[str, Any]:
    fname = target_filename(entry)
    out_path = OUT / fname
    result: Dict[str, Any] = {
        "file": fname,
        "paper_name": entry.get("paper_name"),
        "status": "pending",
        "path": str(out_path),
    }

    meta: Dict[str, Any] = {}
    body = ""
    status = "metadata_only"
    pii = extract_pii(fname)
    title = entry.get("paper_name") or ""

    # 1) 已有 http
    src = entry.get("paper_url") or ""
    if src.startswith("http"):
        meta["url"] = src
        code, raw, ctype = http_get(src)
        result["http_status"] = code
        if code == 200 and raw:
            if "pdf" in ctype or src.lower().endswith(".pdf") or raw[:4] == b"%PDF":
                pdf_path = out_path.with_suffix(".pdf")
                pdf_path.write_bytes(raw)
                body = pdf_to_text(raw)
                status = "fulltext_pdf"
                result["pdf"] = str(pdf_path)
            else:
                body = html_to_rough_text(raw)
                status = "webpage_text"

    # 2) OpenAlex（优先，含 OA pdf）
    if title:
        ow = openalex_by_title(title)
        time.sleep(0.2)
        if ow:
            om = parse_openalex(ow)
            meta.update({k: v for k, v in om.items() if v})

    # 3) Crossref 补全
    it = None
    if pii and not meta.get("doi"):
        it = crossref_by_pii_guess(pii)
        time.sleep(0.2)
        meta.setdefault("url", f"https://www.sciencedirect.com/science/article/pii/{pii}")
    if (not meta.get("doi")) and title:
        it = crossref_by_title(title)
        time.sleep(0.25)
    if it:
        cm = parse_crossref_item(it)
        for k, v in cm.items():
            if v and not meta.get(k):
                meta[k] = v

    # 4) Unpaywall / OpenAlex OA PDF
    pdf_url = meta.get("oa_pdf")
    doi = meta.get("doi")
    if doi and not pdf_url:
        up = unpaywall(doi)
        time.sleep(0.2)
        if up:
            pdf_url = pick_oa_pdf(up)
            meta["oa_pdf"] = pdf_url

    # 5) MDPI 文件名猜测（OpenAlex 未给出 pdf 时）
    if not pdf_url:
        guess = guess_mdpi_pdf(fname)
        if guess:
            pdf_url = guess
            meta.setdefault("oa_pdf", guess)

    if pdf_url and status not in ("fulltext_pdf", "oa_fulltext"):
        code, raw, ctype = http_get(pdf_url, timeout=60)
        result["oa_http_status"] = code
        if code == 200 and raw and (raw[:4] == b"%PDF" or "pdf" in ctype):
            pdf_path = out_path.with_suffix(".pdf")
            pdf_path.write_bytes(raw)
            body = pdf_to_text(raw)
            status = "oa_fulltext"
            result["pdf"] = str(pdf_path)
            meta["oa_pdf"] = pdf_url

    # 6) stub
    if not body:
        bits = []
        if meta.get("url"):
            bits.append(f"Official URL: {meta['url']}")
        if meta.get("doi"):
            bits.append(f"DOI: https://doi.org/{meta['doi']}")
        if pii:
            bits.append(f"ScienceDirect: https://www.sciencedirect.com/science/article/pii/{pii}")
        bits.append(
            "\nFull text is not openly available via automated legal channels. "
            "This stub preserves metadata for LUMIR KB traceability. "
            "Use institutional access to obtain the publisher PDF if needed."
        )
        body = "\n".join(bits)
        status = "metadata_only"

    out_path.write_text(format_md(entry, meta, body, status), encoding="utf-8")
    result["status"] = status
    result["doi"] = meta.get("doi")
    result["resolved_url"] = meta.get("url")
    result["oa_pdf"] = meta.get("oa_pdf")
    return result


def main() -> None:
    entries = json.loads(KB.read_text(encoding="utf-8"))
    print(f"KB entries: {len(entries)}")
    print(f"Output dir: {OUT}")

    manifest: List[Dict[str, Any]] = []
    for i, entry in enumerate(entries, 1):
        name = (entry.get("paper_name") or "")[:70]
        print(f"[{i}/{len(entries)}] {name}")
        try:
            r = process_one(entry)
        except Exception as e:  # noqa: BLE001
            r = {
                "file": target_filename(entry),
                "paper_name": entry.get("paper_name"),
                "status": "error",
                "error": str(e),
            }
            # 仍写最小 stub，保证文件存在
            (OUT / r["file"]).write_text(
                format_md(entry, {}, f"Download error: {e}", "error"),
                encoding="utf-8",
            )
        print(f"    -> {r.get('status')}  {r.get('file')}")
        manifest.append(r)

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    stats: Dict[str, int] = {}
    for r in manifest:
        stats[r.get("status", "?")] = stats.get(r.get("status", "?"), 0) + 1
    print("\nDone. Status counts:")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print(f"Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
