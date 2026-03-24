-- 修复任务模块表结构 - 第二部分
-- 添加更多缺失的列

-- 1. 为tasks_task表添加progress_percentage列
ALTER TABLE tasks_task ADD COLUMN progress_percentage INTEGER NOT NULL DEFAULT 0;

-- 2. 检查并添加其他可能缺失的列
-- 先检查表结构
.schema tasks_task

-- 3. 根据模型定义，可能还需要这些列：
-- end_date, reminder_count, subtask_count, efficiency_score等
-- 但为了简化，我们先添加必需的列

-- 4. 添加end_date列（如果模型中有）
ALTER TABLE tasks_task ADD COLUMN end_date DATETIME;

-- 5. 添加reminder_count列
ALTER TABLE tasks_task ADD COLUMN reminder_count INTEGER NOT NULL DEFAULT 0;

-- 6. 添加subtask_count列
ALTER TABLE tasks_task ADD COLUMN subtask_count INTEGER NOT NULL DEFAULT 0;

-- 7. 更新现有数据
UPDATE tasks_task SET progress_percentage = CAST(progress * 100 AS INTEGER) WHERE progress_percentage = 0;

-- 8. 创建索引
CREATE INDEX IF NOT EXISTS idx_task_progress_pct ON tasks_task(progress_percentage);
CREATE INDEX IF NOT EXISTS idx_task_end_date ON tasks_task(end_date);

.print "✅ 任务模块表结构修复完成（第二部分）"