# Papers 目录说明

本目录由 `scripts/fetch_papers_to_md.py` 根据 `structured_papers1.json` 自动生成，对应知识库里的 `paper_url: Papers\md\...`。

## 内容

- `md/*.md`：每篇文献一个 Markdown（文件名与 JSON 中本地路径一致）
- `md/*.pdf`：若开放获取成功，会额外保存 PDF
- `download_manifest.json`：下载结果清单（status / doi / url）

## status 含义

| status | 含义 |
|--------|------|
| `oa_fulltext` | 已通过 Unpaywall/OpenAlex 等合法 OA 渠道下载全文 |
| `fulltext_pdf` / `webpage_text` | 原 http 链接可直接抓取 |
| `metadata_only` | 付费墙或无法自动获取全文；已写入题录/摘要/官方链接 |
| `error` | 处理异常 |

## 重新拉取

```bash
python scripts/fetch_papers_to_md.py
```

说明：ScienceDirect 等出版社全文通常需机构订阅，脚本**不会**走盗版渠道；LUMIR 检索本身只依赖 JSON 结构化字段，stub 已足够溯源。
