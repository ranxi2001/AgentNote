-- AgentNote Database Schema
-- Markdown 文档知识库

-- 文档主表
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,           -- URL友好的标识符
    title TEXT NOT NULL,
    content TEXT NOT NULL,               -- Markdown 内容
    category TEXT,
    summary TEXT,                        -- 摘要
    source TEXT DEFAULT 'chat',          -- 来源: chat, web, import
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

-- 文档-标签关联表
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);

-- 文档关系表
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_id_1 INTEGER NOT NULL,
    doc_id_2 INTEGER NOT NULL,
    relation_type TEXT DEFAULT 'related', -- related, series, reference
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id_1) REFERENCES documents (id) ON DELETE CASCADE,
    FOREIGN KEY (doc_id_2) REFERENCES documents (id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents (category);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents (created_at);
CREATE INDEX IF NOT EXISTS idx_documents_slug ON documents (slug);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags (name);
