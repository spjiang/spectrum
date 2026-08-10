# 知识库说明（SDAAP 结构化文献）

## 主库（已内嵌，分发必备）

```text
knowledge_base/structured_papers1.json
```

约 129 条。`primary: auto` 即指向此文件。整包 zip Skill 时**必须带上**。

## 演示数据（已内嵌）

```text
data/Chenpi|milk|CN_medicine|corn|tecator|H2O|...
```

## 文献溯源（可选）

```text
Papers/md/ ...
```

E2E **不读**该目录；仅人工核对原文。体积大时可从分发包中删除。

## 什么时候追加文献？

当你的材料在主库里搜不到（或总命中无关论文）时，才需要追加。

1. 复制模板：

```bash
cp knowledge_base/extra_papers.example.json knowledge_base/extra_papers.json
```

2. 按同名字段增删条目（JSON 数组）。
3. 运行 E2E 时会把 `extra` 合并进 BM25 索引（追加在主库之后）。

## 单条字段模板

| 字段 | 必填 | 含义 |
|------|------|------|
| `paper_name` | 是 | 文献标题（参与检索分词） |
| `research_object` | 是 | 研究对象，检索主字段 |
| `preprocessing_method` | 是 | 预处理描述（给 LLM 映射成函数名） |
| `feature_extracting_method` | 是 | 特征方法描述 |
| `paper_url` | 否 | 来源链接 |
| `best_preprocessing_method` | 否 | 最优预处理（可选） |
| `best_feature_extracting_method` | 否 | 最优特征（可选） |
| `machine_learning_method` | 否 | 建模方法 |
| `best_machine_learning_method` | 否 | 最优建模 |

## 与流水线的关系

```text
实体抽取得到 research_object
  → BM25 在 primary(+extra) 上检索
  → 得到 preprocessing_method / feature_extracting_method 文本
  → LLM 映射为代码函数名并投票
  → 本地执行预处理与特征（不是 LLM）
```
