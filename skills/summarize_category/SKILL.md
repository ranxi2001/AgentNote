---
name: summarize_category
description: 获取 AgentNote 知识库中指定分类的想法并生成总结。
---

# Summarize Category Skill

获取某个分类下的所有想法，供 Claude 生成总结。

## 输入格式

```json
{
  "category": "AI"
}
```

不提供 category 时返回所有分类统计。

## 使用方法

```bash
cd /home/AgentNote
python skills/summarize_category/summarize_category.py '{"category": "AI"}'
python skills/summarize_category/summarize_category.py
```

## 后续操作

获取分类数据后，可让 Claude 分析并生成该分类的知识总结。
