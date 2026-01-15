---
name: update_idea
description: 更新 AgentNote 知识库中的想法内容。
---

# Update Idea Skill

更新已有想法的内容。

## 输入格式

```json
{
  "id": 1,
  "title": "新标题",
  "content": "新内容",
  "category": "新分类",
  "keywords": ["新关键词"]
}
```

只需提供要更新的字段。

## 使用方法

```bash
cd /home/AgentNote
python skills/update_idea/update_idea.py '{"id":1,"title":"更新后的标题"}'
```
