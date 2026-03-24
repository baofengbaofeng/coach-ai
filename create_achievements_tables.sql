-- 创建成就系统数据库表

-- 1. 成就分类表
CREATE TABLE IF NOT EXISTS achievements_achievementcategory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7) NOT NULL DEFAULT '#3B82F6',
    "order" INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 2. 成就表
CREATE TABLE IF NOT EXISTS achievements_achievement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER REFERENCES achievements_achievementcategory(id),
    achievement_type VARCHAR(20) NOT NULL DEFAULT 'count',
    difficulty VARCHAR(20) NOT NULL DEFAULT 'medium',
    icon VARCHAR(50),
    badge_image VARCHAR(255),
    condition_type VARCHAR(50) NOT NULL,
    condition_value DECIMAL(10,2) NOT NULL,
    condition_operator VARCHAR(10) NOT NULL DEFAULT 'gte',
    time_limit_days INTEGER NOT NULL DEFAULT 0,
    reward_points INTEGER NOT NULL DEFAULT 0,
    reward_badge VARCHAR(100),
    reward_message TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_secret BOOLEAN NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 3. 用户成就表
CREATE TABLE IF NOT EXISTS achievements_userachievement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id),
    achievement_id INTEGER NOT NULL REFERENCES achievements_achievement(id),
    current_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    progress_percentage INTEGER NOT NULL DEFAULT 0,
    is_unlocked BOOLEAN NOT NULL DEFAULT 0,
    unlocked_at DATETIME,
    is_reward_claimed BOOLEAN NOT NULL DEFAULT 0,
    reward_claimed_at DATETIME,
    started_at DATETIME NOT NULL,
    last_updated_at DATETIME NOT NULL,
    metadata TEXT,
    UNIQUE(user_id, achievement_id)
);

-- 4. 成就奖励表
CREATE TABLE IF NOT EXISTS achievements_achievementreward (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_id INTEGER NOT NULL UNIQUE REFERENCES achievements_achievement(id),
    reward_type VARCHAR(50) NOT NULL,
    reward_value VARCHAR(255) NOT NULL,
    reward_description TEXT,
    is_limited BOOLEAN NOT NULL DEFAULT 0,
    limit_count INTEGER NOT NULL DEFAULT 0,
    limit_expires_at DATETIME,
    claimed_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

-- 5. 成就统计表
CREATE TABLE IF NOT EXISTS achievements_achievementstatistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statistic_type VARCHAR(50) NOT NULL,
    statistic_date DATE NOT NULL,
    data TEXT NOT NULL,
    total_count INTEGER NOT NULL DEFAULT 0,
    average_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    max_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    min_value DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE(statistic_type, statistic_date)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_achievement_category ON achievements_achievement(category_id);
CREATE INDEX IF NOT EXISTS idx_achievement_type ON achievements_achievement(achievement_type);
CREATE INDEX IF NOT EXISTS idx_achievement_difficulty ON achievements_achievement(difficulty);
CREATE INDEX IF NOT EXISTS idx_achievement_active ON achievements_achievement(is_active, display_order);
CREATE INDEX IF NOT EXISTS idx_achievement_secret ON achievements_achievement(is_secret);

CREATE INDEX IF NOT EXISTS idx_userachievement_user ON achievements_userachievement(user_id);
CREATE INDEX IF NOT EXISTS idx_userachievement_achievement ON achievements_userachievement(achievement_id);
CREATE INDEX IF NOT EXISTS idx_userachievement_unlocked ON achievements_userachievement(is_unlocked);
CREATE INDEX IF NOT EXISTS idx_userachievement_progress ON achievements_userachievement(progress_percentage);
CREATE INDEX IF NOT EXISTS idx_userachievement_unlocked_at ON achievements_userachievement(unlocked_at);

CREATE INDEX IF NOT EXISTS idx_achievementreward_achievement ON achievements_achievementreward(achievement_id);
CREATE INDEX IF NOT EXISTS idx_achievementreward_type ON achievements_achievementreward(reward_type);
CREATE INDEX IF NOT EXISTS idx_achievementreward_limited ON achievements_achievementreward(is_limited, limit_expires_at);

CREATE INDEX IF NOT EXISTS idx_achievementstatistic_type_date ON achievements_achievementstatistic(statistic_type, statistic_date);
CREATE INDEX IF NOT EXISTS idx_achievementstatistic_date ON achievements_achievementstatistic(statistic_date);

-- 更新django_migrations表
INSERT OR IGNORE INTO django_migrations (app, name, applied) VALUES 
    ('achievements', '0001_initial', datetime('now')),
    ('achievements', '0002_create_tables', datetime('now'));

PRAGMA foreign_keys = ON;

.print "✅ 成就系统表创建完成"