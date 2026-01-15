---
name: add_idea
description: 添加新想法到 AgentNote 知识库。接收结构化 JSON 数据并存入 SQLite。
---

# Add Idea Skill

将新想法添加到 AgentNote 知识库。

## 触发条件

当用户想要：
- 保存一个想法
- 记录一条笔记
- 添加知识条目

## 输入格式

```json
{
  "title": "想法标题",
  "content": "详细内容",
  "category": "分类（可选）",
  "keywords": ["关键词1", "关键词2"]
}
```

## 使用方法

```bash
cd /home/AgentNote
python skills/add_idea/add_idea.py '{"title":"测试","content":"内容"}'
```

## 输出

返回新创建的想法 ID 和确认信息。
