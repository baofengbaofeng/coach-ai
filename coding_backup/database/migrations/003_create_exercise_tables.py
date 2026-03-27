"""
创建运动相关表的数据库迁移脚本
"""

from datetime import datetime
from sqlalchemy import text


def upgrade(engine):
    """
    执行升级：创建运动相关表
    
    Args:
        engine: SQLAlchemy引擎
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        print("Creating exercise tables...")
        
        # 创建运动类型表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS exercise_types (
            id CHAR(36) PRIMARY KEY,
            name_zh VARCHAR(100) NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            category ENUM('strength', 'cardio', 'flexibility', 'balance', 'mixed') DEFAULT 'strength',
            difficulty ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
            description TEXT,
            standard_movement TEXT,
            standard_video_url TEXT,
            standard_image_url TEXT,
            target_muscles TEXT,
            secondary_muscles TEXT,
            standard_duration INT DEFAULT 0,
            standard_repetitions INT DEFAULT 10,
            standard_sets INT DEFAULT 3,
            rest_between_sets INT DEFAULT 60,
            calorie_factor FLOAT DEFAULT 0.1,
            is_active BOOLEAN DEFAULT TRUE,
            requires_equipment BOOLEAN DEFAULT FALSE,
            equipment_description TEXT,
            tenant_id CHAR(36),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            updated_by CHAR(36),
            
            INDEX idx_exercise_type_name_zh (name_zh),
            INDEX idx_exercise_type_name_en (name_en),
            INDEX idx_exercise_type_code (code),
            INDEX idx_exercise_type_category (category),
            INDEX idx_exercise_type_difficulty (difficulty),
            INDEX idx_exercise_type_active (is_active),
            INDEX idx_exercise_type_tenant (tenant_id),
            INDEX idx_exercise_type_created_at (created_at),
            
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        
        print("Created exercise_types table")
        
        # 创建摄像头设备表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS camera_devices (
            id CHAR(36) PRIMARY KEY,
            device_name VARCHAR(100) NOT NULL,
            serial_number VARCHAR(100) UNIQUE NOT NULL,
            device_type ENUM('webcam', 'ip_camera', 'mobile_camera', 'action_camera', 'other') DEFAULT 'webcam',
            brand VARCHAR(50),
            model VARCHAR(50),
            description TEXT,
            connection_status ENUM('online', 'offline', 'error', 'maintenance') DEFAULT 'offline',
            last_connected_at DATETIME,
            last_disconnected_at DATETIME,
            connection_error TEXT,
            ip_address VARCHAR(45),
            port INT,
            rtsp_url TEXT,
            webrtc_signaling_url TEXT,
            webrtc_peer_id VARCHAR(100),
            resolution_width INT DEFAULT 1920,
            resolution_height INT DEFAULT 1080,
            frame_rate INT DEFAULT 30,
            video_codec VARCHAR(20) DEFAULT 'h264',
            has_audio BOOLEAN DEFAULT FALSE,
            audio_codec VARCHAR(20),
            location VARCHAR(200),
            installation_angle INT,
            installation_height FLOAT,
            calibration_data TEXT,
            device_config TEXT,
            is_enabled BOOLEAN DEFAULT TRUE,
            is_in_use BOOLEAN DEFAULT FALSE,
            current_user_id CHAR(36),
            current_use_started_at DATETIME,
            tenant_id CHAR(36),
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            updated_by CHAR(36),
            
            INDEX idx_camera_device_name (device_name),
            INDEX idx_camera_device_serial (serial_number),
            INDEX idx_camera_device_status (connection_status),
            INDEX idx_camera_device_enabled (is_enabled),
            INDEX idx_camera_device_in_use (is_in_use),
            INDEX idx_camera_device_ip (ip_address),
            INDEX idx_camera_device_tenant (tenant_id),
            INDEX idx_camera_device_last_connected (last_connected_at),
            
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL,
            FOREIGN KEY (current_user_id) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        
        print("Created camera_devices table")
        
        # 创建运动记录表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS exercise_records (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            exercise_type_id CHAR(36) NOT NULL,
            tenant_id CHAR(36),
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            status ENUM('completed', 'in_progress', 'paused', 'cancelled') DEFAULT 'completed',
            mode ENUM('manual', 'camera_auto', 'sensor_auto') DEFAULT 'manual',
            total_repetitions INT DEFAULT 0,
            total_sets INT DEFAULT 0,
            total_duration INT DEFAULT 0,
            avg_heart_rate INT,
            max_heart_rate INT,
            min_heart_rate INT,
            estimated_calories FLOAT DEFAULT 0.0,
            user_weight_kg FLOAT,
            quality_score INT,
            posture_accuracy INT,
            completion_score INT,
            fatigue_level INT,
            subjective_feeling INT,
            notes TEXT,
            camera_device_id CHAR(36),
            sensor_data TEXT,
            video_analysis_data TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            verified_by CHAR(36),
            verified_at DATETIME,
            verification_notes TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            updated_by CHAR(36),
            
            INDEX idx_exercise_record_user (user_id),
            INDEX idx_exercise_record_exercise_type (exercise_type_id),
            INDEX idx_exercise_record_tenant (tenant_id),
            INDEX idx_exercise_record_start_time (start_time),
            INDEX idx_exercise_record_end_time (end_time),
            INDEX idx_exercise_record_status (status),
            INDEX idx_exercise_record_mode (mode),
            INDEX idx_exercise_record_camera (camera_device_id),
            INDEX idx_exercise_record_verified (is_verified),
            INDEX idx_exercise_record_user_date (user_id, start_time),
            INDEX idx_exercise_record_tenant_date (tenant_id, start_time),
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id) ON DELETE CASCADE,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL,
            FOREIGN KEY (camera_device_id) REFERENCES camera_devices(id) ON DELETE SET NULL,
            FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        
        print("Created exercise_records table")
        
        # 创建运动计划表
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS exercise_plans (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            exercise_type_id CHAR(36) NOT NULL,
            tenant_id CHAR(36),
            plan_name VARCHAR(200) NOT NULL,
            description TEXT,
            plan_type ENUM('daily', 'weekly', 'custom') DEFAULT 'daily',
            status ENUM('active', 'paused', 'completed', 'cancelled') DEFAULT 'active',
            start_date DATE NOT NULL,
            end_date DATE,
            target_repetitions INT DEFAULT 0,
            target_sets INT DEFAULT 0,
            target_duration INT DEFAULT 0,
            weekly_frequency INT DEFAULT 7,
            weekly_days TEXT,
            daily_time TIME,
            priority INT DEFAULT 5,
            enable_reminder BOOLEAN DEFAULT TRUE,
            reminder_minutes_before INT DEFAULT 15,
            reward_points INT DEFAULT 10,
            progress INT DEFAULT 0,
            completed_count INT DEFAULT 0,
            failed_count INT DEFAULT 0,
            last_completed_at DATE,
            streak_days INT DEFAULT 0,
            max_streak_days INT DEFAULT 0,
            custom_rules TEXT,
            notes TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            created_by CHAR(36),
            updated_by CHAR(36),
            
            INDEX idx_exercise_plan_user (user_id),
            INDEX idx_exercise_plan_exercise_type (exercise_type_id),
            INDEX idx_exercise_plan_tenant (tenant_id),
            INDEX idx_exercise_plan_name (plan_name),
            INDEX idx_exercise_plan_status (status),
            INDEX idx_exercise_plan_type (plan_type),
            INDEX idx_exercise_plan_dates (start_date, end_date),
            INDEX idx_exercise_plan_priority (priority),
            INDEX idx_exercise_plan_user_status (user_id, status),
            
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id) ON DELETE CASCADE,
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """))
        
        print("Created exercise_plans table")
        
        # 插入默认运动类型数据
        default_exercises = [
            {
                'id': '11111111-1111-1111-1111-111111111111',
                'name_zh': '俯卧撑',
                'name_en': 'Push-up',
                'code': 'pushup',
                'category': 'strength',
                'difficulty': 'beginner',
                'description': '经典的上肢力量训练动作，主要锻炼胸肌、三角肌和肱三头肌',
                'standard_movement': '1. 双手与肩同宽，手掌平放在地面上\n2. 身体保持一条直线，核心收紧\n3. 缓慢下降身体，直到胸部接近地面\n4. 用力推起身体回到起始位置',
                'target_muscles': '["chest", "triceps", "shoulders"]',
                'secondary_muscles': '["core", "back"]',
                'standard_repetitions': 15,
                'standard_sets': 3,
                'rest_between_sets': 60,
                'calorie_factor': 0.12,
                'is_active': True,
                'requires_equipment': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': '22222222-2222-2222-2222-222222222222',
                'name_zh': '深蹲',
                'name_en': 'Squat',
                'code': 'squat',
                'category': 'strength',
                'difficulty': 'beginner',
                'description': '经典的下肢力量训练动作，主要锻炼大腿、臀部和核心肌群',
                'standard_movement': '1. 双脚与肩同宽，脚尖略微外展\n2. 保持背部挺直，核心收紧\n3. 缓慢下蹲，直到大腿与地面平行\n4. 用力站起回到起始位置',
                'target_muscles': '["quadriceps", "glutes", "hamstrings"]',
                'secondary_muscles': '["core", "calves"]',
                'standard_repetitions': 20,
                'standard_sets': 3,
                'rest_between_sets': 60,
                'calorie_factor': 0.15,
                'is_active': True,
                'requires_equipment': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': '33333333-3333-3333-3333-333333333333',
                'name_zh': '仰卧起坐',
                'name_en': 'Sit-up',
                'code': 'situp',
                'category': 'strength',
                'difficulty': 'beginner',
                'description': '经典的核心训练动作，主要锻炼腹肌',
                'standard_movement': '1. 仰卧，膝盖弯曲，双脚平放在地面上\n2. 双手放在头后或胸前\n3. 用腹肌力量抬起上半身\n4. 缓慢下降回到起始位置',
                'target_muscles': '["abs", "core"]',
                'secondary_muscles': '["hip flexors"]',
                'standard_repetitions': 25,
                'standard_sets': 3,
                'rest_between_sets': 45,
                'calorie_factor': 0.08,
                'is_active': True,
                'requires_equipment': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': '44444444-4444-4444-4444-444444444444',
                'name_zh': '平板支撑',
                'name_en': 'Plank',
                'code': 'plank',
                'category': 'strength',
                'difficulty': 'beginner',
                'description': '核心稳定性训练动作，锻炼全身核心肌群',
                'standard_movement': '1. 俯卧，用前臂和脚尖支撑身体\n2. 身体保持一条直线，核心收紧\n3. 保持这个姿势，避免臀部下沉或抬高',
                'target_muscles': '["core", "abs", "back"]',
                'secondary_muscles': '["shoulders", "glutes"]',
                'standard_duration': 60,
                'standard_sets': 3,
                'rest_between_sets': 30,
                'calorie_factor': 0.05,
                'is_active': True,
                'requires_equipment': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            },
            {
                'id': '55555555-5555-5555-5555-555555555555',
                'name_zh': '开合跳',
                'name_en': 'Jumping Jack',
                'code': 'jumping_jack',
                'category': 'cardio',
                'difficulty': 'beginner',
                'description': '有氧运动，提高心率和协调性',
                'standard_movement': '1. 站立，双脚并拢，双手放在身体两侧\n2. 跳起时双脚分开，双手举过头顶\n3. 跳回时双脚并拢，双手放回身体两侧',
                'target_muscles': '["legs", "shoulders"]',
                'secondary_muscles': '["core"]',
                'standard_repetitions': 50,
                'standard_sets': 3,
                'rest_between_sets': 30,
                'calorie_factor': 0.18,
                'is_active': True,
                'requires_equipment': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        ]
        
        for exercise in default_exercises:
            connection.execute(text("""
            INSERT IGNORE INTO exercise_types 
            (id, name_zh, name_en, code, category, difficulty, description, 
             standard_movement, target_muscles, secondary_muscles, standard_duration,
             standard_repetitions, standard_sets, rest_between_sets, calorie_factor,
             is_active, requires_equipment, created_at, updated_at)
            VALUES 
            (:id, :name_zh, :name_en, :code, :category, :difficulty, :description,
             :standard_movement, :target_muscles, :secondary_muscles, :standard_duration,
             :standard_repetitions, :standard_sets, :rest_between_sets, :calorie_factor,
             :is_active, :requires_equipment, :created_at, :updated_at)
            """), exercise)
        
        print(f"Inserted {len(default_exercises)} default exercise types")
        
        transaction.commit()
        print("Exercise tables created successfully!")
        
    except Exception as e:
        transaction.rollback()
        print(f"Error creating exercise tables: {e}")
        raise
    finally:
        connection.close()


def downgrade(engine):
    """
    执行降级：删除运动相关表
    
    Args:
        engine: SQLAlchemy引擎
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        print("Dropping exercise tables...")
        
        # 删除表的顺序很重要（外键约束）
        connection.execute(text("DROP TABLE IF EXISTS exercise_plans"))
        print("Dropped exercise_plans table")
        
        connection.execute(text("DROP TABLE IF EXISTS exercise_records"))
        print("Dropped exercise_records table")
        
        connection.execute(text("DROP TABLE IF EXISTS camera_devices"))
        print("Dropped camera_devices table")
        
        connection.execute(text("DROP TABLE IF EXISTS exercise_types"))
        print("Dropped exercise_types table")
        
        transaction.commit()
        print("Exercise tables dropped successfully!")
        
    except Exception as e:
        transaction.rollback()
        print(f"Error dropping exercise tables: {e}")
        raise
    finally:
        connection.close()