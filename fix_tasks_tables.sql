-- 修复任务模块表结构
-- 添加缺失的列

-- 1. 为tasks_task表添加缺失的列
ALTER TABLE tasks_task ADD COLUMN start_date DATETIME;
ALTER TABLE tasks_task ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE tasks_task ADD COLUMN parent_task_id INTEGER REFERENCES tasks_task(id);
ALTER TABLE tasks_task ADD COLUMN is_template BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE tasks_task ADD COLUMN template_name VARCHAR(100);
ALTER TABLE tasks_task ADD COLUMN tags TEXT;

-- 2. 为tasks_taskcategory表添加缺失的列（如果需要）
-- 检查是否已有这些列，如果没有则添加

-- 3. 创建缺失的索引
CREATE INDEX IF NOT EXISTS idx_task_start_date ON tasks_task(start_date);
CREATE INDEX IF NOT EXISTS idx_task_is_deleted ON tasks_task(is_deleted);
CREATE INDEX IF NOT EXISTS idx_task_parent ON tasks_task(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_task_is_template ON tasks_task(is_template);
CREATE INDEX IF NOT EXISTS idx_task_category_deleted ON tasks_task(category_id, is_deleted);

-- 4. 更新现有数据
UPDATE tasks_task SET is_deleted = 0 WHERE is_deleted IS NULL;
UPDATE tasks_task SET is_template = 0 WHERE is_template IS NULL;

.print "✅ 任务模块表结构修复完成"