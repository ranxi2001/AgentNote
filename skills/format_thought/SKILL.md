---
name: format_thought
description: 将用户的零碎自然语言想法格式化为结构化 JSON，准备入库 AgentNote。这是 AgentNote 的核心智能 Skill。
---

# Format Thought Skill

**核心 Skill**：将零碎的自然语言想法格式化为结构化数据。

## 触发条件

当用户说：
- "帮我整理这个想法"
- "格式化入库"
- "结构化一下"

## 工作流程

1. 接收用户的自然语言输入
2. 由 Claude 分析并提取结构化信息
3. 输出标准 JSON 格式

## 格式化提示模板

当使用此 Skill 时，请让 Claude 按以下模板处理：

```
用户输入: {raw_text}

请将此零碎想法格式化为 JSON:
{
  "title": "简短标题（10字以内）",
  "category": "分类（如：AI、生产力、编程、生活、创意等）",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "content": "整理后的详细描述，保留核心观点，语言流畅",
  "suggested_relations": ["可能相关的已有想法关键词"]
}
```

## 使用示例

**输入**:
```
今天突然想到一个点子，用skills做知识库管理太香了，
比notion轻量多了，而且agent可以自动整理
```

**格式化输出**:
```json
{
  "title": "Skills驱动知识库",
  "category": "生产力",
  "keywords": ["skills", "知识库", "agent", "轻量化"],
  "content": "利用 Claude Skills 构建知识库管理工具，相比 Notion 更轻量。核心优势是 Agent 可以自动整理零碎想法，降低用户输入负担。",
  "suggested_relations": ["AgentNote", "Claude"]
}
```

## 后续操作

格式化完成后，建议调用 `add_idea` Skill 将数据写入数据库。
