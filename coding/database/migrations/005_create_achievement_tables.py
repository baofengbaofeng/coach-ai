"""
创建成就系统相关表的数据库迁移脚本
"""

from datetime import datetime
from sqlalchemy import text


def upgrade(engine):
    """
    执行升级：创建成就系统相关表
    
    Args:
        engine: SQLAlchemy引擎
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        print("Creating achievement system tables...")
        
        # 创建成就表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS achievements (
            id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            icon_url VARCHAR(500),
            banner_url VARCHAR(500),
            achievement_type ENUM('exercise', 'task', 'streak', 'milestone', 'special', 'collection') DEFAULT 'exercise',
            difficulty ENUM('easy', 'medium', 'hard', 'legendary') DEFAULT 'easy',
            category VARCHAR(100),
            tags JSON,
            trigger_type VARCHAR(100) NOT NULL,
            trigger_config JSON NOT NULL,
            target_value INT NOT NULL,
            current_value INT DEFAULT 0,
            reward_points INT DEFAULT 0,
            reward_badge_id INT,
            reward_items JSON,
            status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
            unlock_count INT DEFAULT 0,
            first_unlock_at DATETIME,
            last_unlock_at DATETIME,
            display_order INT DEFAULT 0,
            is_hidden BOOLEAN DEFAULT FALSE,
            is_secret BOOLEAN DEFAULT FALSE,
            tenant_id CHAR(36),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_achievement_type (achievement_type),
            INDEX idx_achievement_difficulty (difficulty),
            INDEX idx_achievement_status (status),
            INDEX idx_achievement_display_order (display_order),
            INDEX idx_achievement_created_at (created_at)
        )
        """))
        
        # 创建徽章表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS badges (
            id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            icon_url VARCHAR(500) NOT NULL,
            banner_url VARCHAR(500),
            badge_type ENUM('achievement', 'milestone', 'special', 'event', 'seasonal') DEFAULT 'achievement',
            rarity ENUM('common', 'uncommon', 'rare', 'epic', 'legendary') DEFAULT 'common',
            category VARCHAR(100),
            tags JSON,
            grant_condition TEXT,
            grant_config JSON,
            is_auto_grant BOOLEAN DEFAULT TRUE,
            display_order INT DEFAULT 0,
            is_hidden BOOLEAN DEFAULT FALSE,
            is_secret BOOLEAN DEFAULT FALSE,
            grant_count INT DEFAULT 0,
            first_grant_at DATETIME,
            last_grant_at DATETIME,
            status ENUM('active', 'inactive', 'archived') DEFAULT 'active',
            tenant_id CHAR(36),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_badge_type (badge_type),
            INDEX idx_badge_rarity (rarity),
            INDEX idx_badge_status (status),
            INDEX idx_badge_display_order (display_order),
            INDEX idx_badge_created_at (created_at)
        )
        """))
        
        # 创建用户成就表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            achievement_id CHAR(36) NOT NULL,
            status ENUM('locked', 'in_progress', 'unlocked', 'completed') DEFAULT 'locked',
            progress INT DEFAULT 0,
            target_value INT NOT NULL,
            progress_percentage INT DEFAULT 0,
            unlocked_at DATETIME,
            completed_at DATETIME,
            is_new BOOLEAN DEFAULT TRUE,
            reward_received BOOLEAN DEFAULT FALSE,
            reward_received_at DATETIME,
            reward_data JSON,
            progress_details JSON,
            last_updated_at DATETIME NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_user_achievement_user (user_id),
            INDEX idx_user_achievement_achievement (achievement_id),
            INDEX idx_user_achievement_status (status),
            INDEX idx_user_achievement_unlocked_at (unlocked_at),
            INDEX idx_user_achievement_created_at (created_at),
            UNIQUE INDEX idx_user_achievement_unique (user_id, achievement_id)
        )
        """))
        
        # 创建用户徽章表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS user_badges (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            badge_id CHAR(36) NOT NULL,
            granted_at DATETIME NOT NULL,
            granted_by CHAR(36),
            grant_reason TEXT,
            is_equipped BOOLEAN DEFAULT FALSE,
            is_favorite BOOLEAN DEFAULT FALSE,
            display_order INT DEFAULT 0,
            is_new BOOLEAN DEFAULT TRUE,
            is_hidden BOOLEAN DEFAULT FALSE,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_user_badge_user (user_id),
            INDEX idx_user_badge_badge (badge_id),
            INDEX idx_user_badge_granted_at (granted_at),
            INDEX idx_user_badge_created_at (created_at),
            UNIQUE INDEX idx_user_badge_unique (user_id, badge_id)
        )
        """))
        
        # 创建奖励表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS rewards (
            id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            icon_url VARCHAR(500),
            banner_url VARCHAR(500),
            reward_type ENUM('points', 'badge', 'item', 'discount', 'access', 'custom') DEFAULT 'points',
            reward_config JSON NOT NULL,
            value INT DEFAULT 0,
            grant_condition TEXT,
            grant_config JSON,
            is_auto_grant BOOLEAN DEFAULT TRUE,
            max_claims INT DEFAULT -1,
            claim_count INT DEFAULT 0,
            per_user_limit INT DEFAULT 1,
            require_achievement_id CHAR(36),
            available_from DATETIME,
            available_until DATETIME,
            claim_deadline DATETIME,
            status ENUM('active', 'inactive', 'archived', 'expired') DEFAULT 'active',
            display_order INT DEFAULT 0,
            is_hidden BOOLEAN DEFAULT FALSE,
            is_secret BOOLEAN DEFAULT FALSE,
            tenant_id CHAR(36),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_reward_type (reward_type),
            INDEX idx_reward_status (status),
            INDEX idx_reward_display_order (display_order),
            INDEX idx_reward_created_at (created_at),
            INDEX idx_reward_available_from (available_from),
            INDEX idx_reward_available_until (available_until)
        )
        """))
        
        # 创建用户奖励表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS user_rewards (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            reward_id CHAR(36) NOT NULL,
            achievement_id CHAR(36),
            claimed_at DATETIME NOT NULL,
            claimed_by CHAR(36),
            claim_reason TEXT,
            reward_data JSON NOT NULL,
            reward_value INT DEFAULT 0,
            status ENUM('claimed', 'used', 'expired', 'revoked') DEFAULT 'claimed',
            used_at DATETIME,
            used_for TEXT,
            used_data JSON,
            expires_at DATETIME,
            expired_at DATETIME,
            revoked_at DATETIME,
            revoked_by CHAR(36),
            revoke_reason TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            
            INDEX idx_user_reward_user (user_id),
            INDEX idx_user_reward_reward (reward_id),
            INDEX idx_user_reward_status (status),
            INDEX idx_user_reward_claimed_at (claimed_at),
            INDEX idx_user_reward_created_at (created_at)
        )
        """))
        
        # 添加外键约束
        print("Adding foreign key constraints...")
        
        # 成就表的外键约束
        connection.execute(text("""
        ALTER TABLE achievements
        ADD CONSTRAINT fk_achievements_reward_badge
        FOREIGN KEY (reward_badge_id) REFERENCES badges(id)
        ON DELETE SET NULL
        """))
        
        # 用户成就表的外键约束
        connection.execute(text("""
        ALTER TABLE user_achievements
        ADD CONSTRAINT fk_user_achievements_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        """))
        
        connection.execute(text("""
        ALTER TABLE user_achievements
        ADD CONSTRAINT fk_user_achievements_achievement
        FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        ON DELETE CASCADE
        """))
        
        # 用户徽章表的外键约束
        connection.execute(text("""
        ALTER TABLE user_badges
        ADD CONSTRAINT fk_user_badges_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        """))
        
        connection.execute(text("""
        ALTER TABLE user_badges
        ADD CONSTRAINT fk_user_badges_badge
        FOREIGN KEY (badge_id) REFERENCES badges(id)
        ON DELETE CASCADE
        """))
        
        connection.execute(text("""
        ALTER TABLE user_badges
        ADD CONSTRAINT fk_user_badges_granted_by
        FOREIGN KEY (granted_by) REFERENCES users(id)
        ON DELETE SET NULL
        """))
        
        # 奖励表的外键约束
        connection.execute(text("""
        ALTER TABLE rewards
        ADD CONSTRAINT fk_rewards_require_achievement
        FOREIGN KEY (require_achievement_id) REFERENCES achievements(id)
        ON DELETE SET NULL
        """))
        
        # 用户奖励表的外键约束
        connection.execute(text("""
        ALTER TABLE user_rewards
        ADD CONSTRAINT fk_user_rewards_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        """))
        
        connection.execute(text("""
        ALTER TABLE user_rewards
        ADD CONSTRAINT fk_user_rewards_reward
        FOREIGN KEY (reward_id) REFERENCES rewards(id)
        ON DELETE CASCADE
        """))
        
        connection.execute(text("""
        ALTER TABLE user_rewards
        ADD CONSTRAINT fk_user_rewards_achievement
        FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        ON DELETE SET NULL
        """))
        
        connection.execute(text("""
        ALTER TABLE user_rewards
        ADD CONSTRAINT fk_user_rewards_claimed_by
        FOREIGN KEY (claimed_by) REFERENCES users(id)
        ON DELETE SET NULL
        """))
        
        connection.execute(text("""
        ALTER TABLE user_rewards
        ADD CONSTRAINT fk_user_rewards_revoked_by
        FOREIGN KEY (revoked_by) REFERENCES users(id)
        ON DELETE SET NULL
        """))
        
        transaction.commit()
        print("Achievement system tables created successfully!")
        
    except Exception as e:
        transaction.rollback()
        print(f"Error creating achievement system tables: {str(e)}")
        raise
    finally:
        connection.close()


def downgrade(engine):
    """
    执行降级：删除成就系统相关表
    
    Args:
        engine: SQLAlchemy引擎
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        print("Dropping achievement system tables...")
        
        # 删除外键约束
        print("Dropping foreign key constraints...")
        
        try:
            connection.execute(text("ALTER TABLE user_rewards DROP FOREIGN KEY fk_user_rewards_revoked_by"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_rewards DROP FOREIGN KEY fk_user_rewards_claimed_by"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_rewards DROP FOREIGN KEY fk_user_rewards_achievement"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_rewards DROP FOREIGN KEY fk_user_rewards_reward"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_rewards DROP FOREIGN KEY fk_user_rewards_user"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE rewards DROP FOREIGN KEY fk_rewards_require_achievement"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_badges DROP FOREIGN KEY fk_user_badges_granted_by"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_badges DROP FOREIGN KEY fk_user_badges_badge"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_badges DROP FOREIGN KEY fk_user_badges_user"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_achievements DROP FOREIGN KEY fk_user_achievements_achievement"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE user_achievements DROP FOREIGN KEY fk_user_achievements_user"))
        except:
            pass
        
        try:
            connection.execute(text("ALTER TABLE achievements DROP FOREIGN KEY fk_achievements_reward_badge"))
        except:
            pass
        
        # 删除表
        connection.execute(text("DROP TABLE IF EXISTS user_rewards"))
        connection.execute(text("DROP TABLE IF EXISTS rewards"))
        connection.execute(text("DROP TABLE IF EXISTS user_badges"))
        connection.execute(text("DROP TABLE IF EXISTS user_achievements"))
        connection.execute(text("DROP TABLE IF EXISTS badges"))
        connection.execute(text("DROP TABLE IF EXISTS achievements"))
        
        transaction.commit()
        print("Achievement system tables dropped successfully!")
        
    except Exception as e:
        transaction.rollback()
        print(f"Error dropping achievement system tables: {str(e)}")
        raise
    finally:
        connection.close()