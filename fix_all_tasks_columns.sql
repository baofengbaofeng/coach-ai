-- 修复任务模块所有缺失的列
-- 根据模型定义添加所有列

-- 1. 添加difficulty_level列
ALTER TABLE tasks_task ADD COLUMN difficulty_level INTEGER DEFAULT 3;

-- 2. 添加satisfaction_score列
ALTER TABLE tasks_task ADD COLUMN satisfaction_score INTEGER DEFAULT 0;

-- 3. 添加efficiency_score列（如果模型中有）
ALTER TABLE tasks_task ADD COLUMN efficiency_score DECIMAL(5,2) DEFAULT 0.0;

-- 4. 添加rating列（如果模型中有）
ALTER TABLE tasks_task ADD COLUMN rating INTEGER DEFAULT 0;

-- 5. 添加notes列
ALTER TABLE tasks_task ADD COLUMN notes TEXT;

-- 6. 添加metadata列（用于存储额外数据）
ALTER TABLE tasks_task ADD COLUMN metadata TEXT;

-- 7. 添加version列（用于乐观锁）
ALTER TABLE tasks_task ADD COLUMN version INTEGER DEFAULT 1;

-- 8. 更新现有数据
UPDATE tasks_task SET difficulty_level = 3 WHERE difficulty_level IS NULL;
UPDATE tasks_task SET satisfaction_score = 0 WHERE satisfaction_score IS NULL;
UPDATE tasks_task SET efficiency_score = 0.0 WHERE efficiency_score IS NULL;
UPDATE tasks_task SET rating = 0 WHERE rating IS NULL;
UPDATE tasks_task SET version = 1 WHERE version IS NULL;

-- 9. 创建索引
CREATE INDEX IF NOT EXISTS idx_task_difficulty ON tasks_task(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_task_satisfaction ON tasks_task(satisfaction_score);
CREATE INDEX IF NOT EXISTS idx_task_efficiency ON tasks_task(efficiency_score);
CREATE INDEX IF NOT EXISTS idx_task_rating ON tasks_task(rating);

-- 10. 显示最终表结构
.schema tasks_task

.print "✅ 所有缺失列已添加完成"