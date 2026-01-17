-- X Bookmarks Database Schema
-- 存储 X (Twitter) 书签数据

-- 书签主表
CREATE TABLE IF NOT EXISTS x_bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tweet_id TEXT UNIQUE NOT NULL,        -- 推文ID
    tweet_url TEXT,                       -- 推文链接
    full_text TEXT NOT NULL,              -- 推文完整内容
    lang TEXT,                            -- 语言
    created_at DATETIME,                  -- 推文创建时间
    bookmarked_at DATETIME,               -- 书签获取时间

-- 用户信息
user_id TEXT,
user_name TEXT,
user_screen_name TEXT,
user_avatar_url TEXT,

-- 统计数据
bookmark_count INTEGER DEFAULT 0,
favorite_count INTEGER DEFAULT 0,
retweet_count INTEGER DEFAULT 0,
reply_count INTEGER DEFAULT 0,
quote_count INTEGER DEFAULT 0,
view_count INTEGER DEFAULT 0,

-- 链接和媒体（JSON格式）
urls TEXT, -- JSON: [{display_url, expanded_url}]
media TEXT, -- JSON: [{type, url, ...}]
hashtags TEXT, -- JSON: [tag1, tag2, ...]
user_mentions TEXT, -- JSON: [{screen_name, name}]

-- 引用和转发
is_quote_status INTEGER DEFAULT 0,
is_retweet INTEGER DEFAULT 0,
quoted_tweet_id TEXT,

-- 原始数据
raw_json TEXT, -- 完整原始JSON备份

-- 元数据
sync_cursor TEXT,                     -- 同步时的游标位置
    created_in_db DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_in_db DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 同步状态表
CREATE TABLE IF NOT EXISTS x_sync_state (
    id INTEGER PRIMARY KEY,
    last_cursor TEXT, -- 最后同步的游标
    last_sync_at DATETIME, -- 最后同步时间
    total_synced INTEGER DEFAULT 0 -- 总同步数量
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_x_bookmarks_tweet_id ON x_bookmarks (tweet_id);

CREATE INDEX IF NOT EXISTS idx_x_bookmarks_created ON x_bookmarks (created_at);

CREATE INDEX IF NOT EXISTS idx_x_bookmarks_user ON x_bookmarks (user_screen_name);

CREATE INDEX IF NOT EXISTS idx_x_bookmarks_lang ON x_bookmarks (lang);

CREATE INDEX IF NOT EXISTS idx_x_bookmarks_bookmarked ON x_bookmarks (bookmarked_at);