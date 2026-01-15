-- AgentNote Database Schema
-- 知识库管理平台数据库结构

-- 想法主表
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    keywords TEXT, -- JSON array string
    content TEXT NOT NULL,
    source TEXT DEFAULT 'chat',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- 想法-标签关联表
CREATE TABLE IF NOT EXISTS idea_tags (
    idea_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (idea_id, tag_id),
    FOREIGN KEY (idea_id) REFERENCES ideas (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- 想法关系表
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id_1 INTEGER NOT NULL,
    idea_id_2 INTEGER NOT NULL,
    relation_type TEXT DEFAULT 'related', -- related, parent, inspired_by, contradict
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id_1) REFERENCES ideas (id) ON DELETE CASCADE,
    FOREIGN KEY (idea_id_2) REFERENCES ideas (id) ON DELETE CASCADE
);

-- 索引加速查询
CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas (category);

CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas (created_at);

CREATE INDEX IF NOT EXISTS idx_ideas_title ON ideas (title);

CREATE INDEX IF NOT EXISTS idx_relations_idea1 ON relations (idea_id_1);

CREATE INDEX IF NOT EXISTS idx_relations_idea2 ON relations (idea_id_2);