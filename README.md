# AgentNote 📝

> Agent 驱动的轻量知识库管理平台

在 Agent 时代，传统表格文档工具如 Notion 反而拖累生产力。AgentNote 采用 **Claude Skills + SQLite** 的极简架构，让你只管输入零碎想法，Agent 负责格式化、分类和入库。

## ✨ 特性

- **极致轻量**：无框架依赖，整个项目就是 Skills 脚本 + SQLite 文件
- **Agent 中心**：用户专注思考，Claude 处理格式化和入库
- **零负担输入**：自然语言输入，自动结构化
- **本地存储**：数据存在本地 SQLite，隐私安全

## 📁 项目结构

```
AgentNote/
├── skills/                 # Claude Skills
│   ├── add_idea/          # 添加想法
│   ├── search_ideas/      # 搜索
│   ├── get_idea/          # 获取单条
│   ├── update_idea/       # 更新
│   ├── delete_idea/       # 删除
│   ├── relate_ideas/      # 创建关联
│   ├── format_thought/    # 格式化零碎思考 ⭐
│   ├── get_recent/        # 最近记录
│   ├── find_similar/      # 相似查找
│   └── summarize_category/# 分类总结
├── utils/
│   └── db.py              # 数据库工具
├── data/
│   └── agentnote.db       # SQLite 数据库
├── schema.sql             # 数据库结构
└── README.md
```

## 🚀 快速开始

### 1. 初始化数据库

```bash
cd /home/AgentNote
python utils/db.py init
```

### 2. 添加第一个想法

```bash
python skills/add_idea/add_idea.py '{"title":"AgentNote真香","category":"生产力","keywords":["agent","知识库"],"content":"用 Skills 做知识库管理比 Notion 轻量多了"}'
```

### 3. 搜索想法

```bash
python skills/search_ideas/search_ideas.py '{"keyword":"agent"}'
```

### 4. 与 Claude 配合使用

在 Claude 对话中：

```
我：帮我记录一个想法 - 今天想到用 skills 管理知识库很酷

Claude：让我帮你格式化并入库...
[调用 format_thought] → [调用 add_idea]

已保存！ID: 1
标题：Skills知识库管理
分类：生产力
```

## 📖 Skills 列表

| Skill | 描述 | 示例 |
|-------|------|------|
| `add_idea` | 添加新想法 | `{"title":"标题","content":"内容"}` |
| `search_ideas` | 搜索想法 | `{"keyword":"AI"}` |
| `get_idea` | 获取单条 | `{"id":1}` |
| `update_idea` | 更新想法 | `{"id":1,"title":"新标题"}` |
| `delete_idea` | 删除想法 | `{"id":1}` |
| `relate_ideas` | 创建关联 | `{"idea_id_1":1,"idea_id_2":2}` |
| `format_thought` | 格式化零碎想法 | 自然语言文本 |
| `get_recent` | 最近 N 条 | `{"limit":10}` |
| `find_similar` | 相似查找 | `{"idea_id":1}` |
| `summarize_category` | 分类总结 | `{"category":"AI"}` |

## 🗄️ 数据库结构

- `ideas` - 想法主表（id, title, category, keywords, content, source, timestamps）
- `tags` - 标签表
- `idea_tags` - 想法-标签关联
- `relations` - 想法关系表（支持 related, parent, inspired_by, contradict）

## 🔮 后续扩展

- [ ] 向量嵌入搜索（FAISS）
- [ ] Web UI（Streamlit）
- [ ] 知识图谱可视化
- [ ] 多设备同步

## 📄 License

MIT
