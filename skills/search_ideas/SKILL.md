---
name: search_ideas
description: 在 AgentNote 知识库中搜索想法。支持关键词搜索和分类筛选。
---

# Search Ideas Skill

搜索知识库中的想法。

## 触发条件

当用户想要：
- 搜索某个关键词相关的想法
- 查找某个分类下的内容
- 回顾之前记录的知识

## 输入格式

```json
{
  "keyword": "搜索关键词（可选）",
  "category": "分类筛选（可选）",
  "limit": 20
}
```

## 使用方法

```bash
cd /home/AgentNote
python skills/search_ideas/search_ideas.py '{"keyword":"AI"}'
```

## 输出

返回匹配的想法列表，包含 id、title、content、category 等字段。
