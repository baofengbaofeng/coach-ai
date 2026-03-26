"""
运动模块数据模型
定义运动相关的数据结构和业务对象
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
import json


class ExerciseStatistics:
    """
    运动统计数据模型
    """
    
    def __init__(self, user_id: str, period: str = 'daily'):
        """
        初始化运动统计数据
        
        Args:
            user_id: 用户ID
            period: 统计周期，可选值：daily, weekly, monthly, yearly
        """
        self.user_id = user_id
        self.period = period
        self.start_date = None
        self.end_date = None
        self.total_exercises = 0
        self.total_duration_minutes = 0
        self.total_calories = 0.0
        self.total_repetitions = 0
        self.total_sets = 0
        self.avg_quality_score = 0
        self.avg_posture_accuracy = 0
        self.exercise_type_distribution = {}  # {exercise_type_id: count}
        self.daily_completion_rate = 0.0
        self.streak_days = 0
        self.most_frequent_exercise = None
        self.best_quality_exercise = None
        self.recent_activities = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'user_id': self.user_id,
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_exercises': self.total_exercises,
            'total_duration_minutes': self.total_duration_minutes,
            'total_calories': self.total_calories,
            'total_repetitions': self.total_repetitions,
            'total_sets': self.total_sets,
            'avg_quality_score': self.avg_quality_score,
            'avg_posture_accuracy': self.avg_posture_accuracy,
            'exercise_type_distribution': self.exercise_type_distribution,
            'daily_completion_rate': self.daily_completion_rate,
            'streak_days': self.streak_days,
            'most_frequent_exercise': self.most_frequent_exercise,
            'best_quality_exercise': self.best_quality_exercise,
            'recent_activities': self.recent_activities
        }


class ExerciseGoal:
    """
    运动目标模型
    """
    
    def __init__(self, user_id: str):
        """
        初始化运动目标
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.daily_goal_minutes = 30
        self.weekly_goal_minutes = 210  # 30分钟 * 7天
        self.monthly_goal_minutes = 900  # 30分钟 * 30天
        self.daily_goal_calories = 300
        self.weekly_goal_calories = 2100
        self.monthly_goal_calories = 9000
        self.target_weight_kg = None
        self.target_body_fat_percentage = None
        self.target_muscle_mass_kg = None
        self.target_endurance_level = 'intermediate'
        self.target_strength_level = 'intermediate'
        self.target_flexibility_level = 'intermediate'
        self.start_date = datetime.utcnow().date()
        self.target_date = None
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'user_id': self.user_id,
            'daily_goal_minutes': self.daily_goal_minutes,
            'weekly_goal_minutes': self.weekly_goal_minutes,
            'monthly_goal_minutes': self.monthly_goal_minutes,
            'daily_goal_calories': self.daily_goal_calories,
            'weekly_goal_calories': self.weekly_goal_calories,
            'monthly_goal_calories': self.monthly_goal_calories,
            'target_weight_kg': self.target_weight_kg,
            'target_body_fat_percentage': self.target_body_fat_percentage,
            'target_muscle_mass_kg': self.target_muscle_mass_kg,
            'target_endurance_level': self.target_endurance_level,
            'target_strength_level': self.target_strength_level,
            'target_flexibility_level': self.target_flexibility_level,
            'start_date': self.start_date.isoformat(),
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_active': self.is_active
        }


class ExerciseAchievement:
    """
    运动成就模型
    """
    
    def __init__(self, user_id: str):
        """
        初始化运动成就
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.total_points = 0
        self.level = 1
        self.badges = []
        self.milestones = []
        self.recent_achievements = []
        self.next_milestone = None
        self.rank = None
    
    def add_badge(self, badge_id: str, badge_name: str, description: str, icon_url: str = None):
        """
        添加徽章
        
        Args:
            badge_id: 徽章ID
            badge_name: 徽章名称
            description: 徽章描述
            icon_url: 徽章图标URL
        """
        badge = {
            'id': badge_id,
            'name': badge_name,
            'description': description,
            'icon_url': icon_url,
            'earned_at': datetime.utcnow().isoformat()
        }
        self.badges.append(badge)
    
    def add_milestone(self, milestone_id: str, milestone_name: str, description: str, points_required: int):
        """
        添加里程碑
        
        Args:
            milestone_id: 里程碑ID
            milestone_name: 里程碑名称
            description: 里程碑描述
            points_required: 所需积分
        """
        milestone = {
            'id': milestone_id,
            'name': milestone_name,
            'description': description,
            'points_required': points_required,
            'achieved': self.total_points >= points_required,
            'achieved_at': datetime.utcnow().isoformat() if self.total_points >= points_required else None
        }
        self.milestones.append(milestone)
    
    def add_achievement(self, achievement_id: str, achievement_name: str, points_earned: int, description: str):
        """
        添加成就
        
        Args:
            achievement_id: 成就ID
            achievement_name: 成就名称
            points_earned: 获得的积分
            description: 成就描述
        """
        achievement = {
            'id': achievement_id,
            'name': achievement_name,
            'points_earned': points_earned,
            'description': description,
            'earned_at': datetime.utcnow().isoformat()
        }
        self.recent_achievements.append(achievement)
        self.total_points += points_earned
        
        # 更新等级（每1000点升一级）
        self.level = (self.total_points // 1000) + 1
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'user_id': self.user_id,
            'total_points': self.total_points,
            'level': self.level,
            'badges': self.badges,
            'milestones': self.milestones,
            'recent_achievements': self.recent_achievements[-10:],  # 最近10个成就
            'next_milestone': self.next_milestone,
            'rank': self.rank
        }


class CameraStreamConfig:
    """
    摄像头流配置模型
    """
    
    def __init__(self, camera_device_id: str):
        """
        初始化摄像头流配置
        
        Args:
            camera_device_id: 摄像头设备ID
        """
        self.camera_device_id = camera_device_id
        self.stream_type = 'webrtc'  # webrtc, rtsp, hls
        self.video_codec = 'h264'
        self.audio_codec = 'opus'
        self.resolution = '1920x1080'
        self.frame_rate = 30
        self.bitrate = 2000  # kbps
        self.quality_preset = 'medium'
        self.enable_audio = True
        self.enable_video = True
        self.enable_motion_detection = True
        self.enable_pose_estimation = True
        self.pose_estimation_model = 'mediapipe'
        self.motion_sensitivity = 0.5
        self.recording_enabled = False
        self.recording_duration = 300  # 秒
        self.stream_url = None
        self.webrtc_config = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'camera_device_id': self.camera_device_id,
            'stream_type': self.stream_type,
            'video_codec': self.video_codec,
            'audio_codec': self.audio_codec,
            'resolution': self.resolution,
            'frame_rate': self.frame_rate,
            'bitrate': self.bitrate,
            'quality_preset': self.quality_preset,
            'enable_audio': self.enable_audio,
            'enable_video': self.enable_video,
            'enable_motion_detection': self.enable_motion_detection,
            'enable_pose_estimation': self.enable_pose_estimation,
            'pose_estimation_model': self.pose_estimation_model,
            'motion_sensitivity': self.motion_sensitivity,
            'recording_enabled': self.recording_enabled,
            'recording_duration': self.recording_duration,
            'stream_url': self.stream_url,
            'webrtc_config': self.webrtc_config
        }


class PoseAnalysisResult:
    """
    姿势分析结果模型
    """
    
    def __init__(self, exercise_record_id: str):
        """
        初始化姿势分析结果
        
        Args:
            exercise_record_id: 运动记录ID
        """
        self.exercise_record_id = exercise_record_id
        self.timestamp = datetime.utcnow()
        self.landmarks = []  # 关键点坐标
        self.angles = {}  # 关节角度
        self.posture_score = 0
        self.alignment_errors = []
        self.movement_quality = 0
        self.repetition_count = 0
        self.repetition_phase = None  # up, down, hold
        self.velocity = 0.0
        self.acceleration = 0.0
        self.feedback_messages = []
        self.is_correct_posture = False
        self.confidence = 0.0
    
    def add_feedback(self, message: str, severity: str = 'info'):
        """
        添加反馈消息
        
        Args:
            message: 反馈消息
            severity: 严重程度，可选值：info, warning, error
        """
        feedback = {
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.feedback_messages.append(feedback)
    
    def calculate_posture_score(self):
        """
        计算姿势评分
        """
        # 这里可以实现复杂的姿势评分算法
        # 基于关节角度、对齐误差、运动质量等
        
        base_score = 100
        
        # 扣除对齐误差
        for error in self.alignment_errors:
            if error['severity'] == 'high':
                base_score -= 10
            elif error['severity'] == 'medium':
                base_score -= 5
            elif error['severity'] == 'low':
                base_score -= 2
        
        # 基于运动质量调整
        base_score = base_score * (self.movement_quality / 100)
        
        self.posture_score = max(0, min(100, int(base_score)))
        self.is_correct_posture = self.posture_score >= 70
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'exercise_record_id': self.exercise_record_id,
            'timestamp': self.timestamp.isoformat(),
            'landmarks': self.landmarks,
            'angles': self.angles,
            'posture_score': self.posture_score,
            'alignment_errors': self.alignment_errors,
            'movement_quality': self.movement_quality,
            'repetition_count': self.repetition_count,
            'repetition_phase': self.repetition_phase,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'feedback_messages': self.feedback_messages,
            'is_correct_posture': self.is_correct_posture,
            'confidence': self.confidence
        }


class ExerciseRecommendation:
    """
    运动推荐模型
    """
    
    def __init__(self, user_id: str):
        """
        初始化运动推荐
        
        Args:
            user_id: 用户ID
        """
        self.user_id = user_id
        self.recommendation_id = str(uuid.uuid4())
        self.recommended_exercises = []
        self.recommendation_reason = ''
        self.fitness_level = 'beginner'
        self.goals = []
        constraints = []
        self.schedule_preferences = {}
        self.equipment_available = []
        self.generated_at = datetime.utcnow()
        self.expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)
        self.priority = 'medium'
    
    def add_exercise(self, exercise_type_id: str, exercise_name: str, 
                    sets: int, repetitions: int, duration: int,
                    reason: str, difficulty: str = 'beginner'):
        """
        添加推荐运动
        
        Args:
            exercise_type_id: 运动类型ID
            exercise_name: 运动名称
            sets: 组数
            repetitions: 重复次数
            duration: 持续时间（秒）
            reason: 推荐理由
            difficulty: 难度级别
        """
        exercise = {
            'exercise_type_id': exercise_type_id,
            'exercise_name': exercise_name,
            'sets': sets,
            'repetitions': repetitions,
            'duration': duration,
            'reason': reason,
            'difficulty': difficulty,
            'estimated_calories': 0,
            'order': len(self.recommended_exercises) + 1
        }
        self.recommended_exercises.append(exercise)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        """
        return {
            'recommendation_id': self.recommendation_id,
            'user_id': self.user_id,
            'recommended_exercises': self.recommended_exercises,
            'recommendation_reason': self.recommendation_reason,
            'fitness_level': self.fitness_level,
            'goals': self.goals,
            'constraints': self.constraints,
            'schedule_preferences': self.schedule_preferences,
            'equipment_available': self.equipment_available,
            'generated_at': self.generated_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'priority': self.priority
        }


# 导入uuid模块
import uuid