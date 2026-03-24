-- 创建任务模块的数据库表
-- 由于迁移问题，直接使用SQL创建表

-- 1. 任务分类表
CREATE TABLE IF NOT EXISTS tasks_taskcategory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    color VARCHAR(7),
    icon VARCHAR(50),
    "order" INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL,
    task_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 2. 任务表
CREATE TABLE IF NOT EXISTS tasks_task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id),
    category_id INTEGER REFERENCES tasks_taskcategory(id),
    status VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    due_date DATETIME,
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2) DEFAULT 0.0,
    progress DECIMAL(5,2) DEFAULT 0.0,
    attachment VARCHAR(255),
    attachment_name VARCHAR(255),
    is_recurring BOOLEAN NOT NULL,
    recurrence_rule VARCHAR(100),
    next_recurrence_date DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 3. 任务提醒表
CREATE TABLE IF NOT EXISTS tasks_taskreminder (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks_task(id),
    reminder_type VARCHAR(20) NOT NULL,
    reminder_time DATETIME NOT NULL,
    is_sent BOOLEAN NOT NULL,
    sent_at DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 4. 任务评论表
CREATE TABLE IF NOT EXISTS tasks_taskcomment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks_task(id),
    user_id INTEGER NOT NULL REFERENCES accounts_user(id),
    content TEXT NOT NULL,
    attachment VARCHAR(255),
    attachment_name VARCHAR(255),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_task_user ON tasks_task(user_id);
CREATE INDEX IF NOT EXISTS idx_task_category ON tasks_task(category_id);
CREATE INDEX IF NOT EXISTS idx_task_status ON tasks_task(status);
CREATE INDEX IF NOT EXISTS idx_task_priority ON tasks_task(priority);
CREATE INDEX IF NOT EXISTS idx_task_due_date ON tasks_task(due_date);
CREATE INDEX IF NOT EXISTS idx_taskreminder_task ON tasks_taskreminder(task_id);
CREATE INDEX IF NOT EXISTS idx_taskreminder_sent ON tasks_taskreminder(is_sent);
CREATE INDEX IF NOT EXISTS idx_taskcomment_task ON tasks_taskcomment(task_id);
CREATE INDEX IF NOT EXISTS idx_taskcomment_user ON tasks_taskcomment(user_id);

-- 更新django_migrations表，标记迁移为已应用
INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES 
    ('tasks', '0001_initial', datetime('now')),
    ('tasks', '0002_auto_20260324_0014', datetime('now'));

PRAGMA foreign_keys = ON;

.print "✅ 任务模块表创建完成"