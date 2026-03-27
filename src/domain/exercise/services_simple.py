"""
运动领域服务（简化版）
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .value_objects import ExerciseCategory, ExerciseDifficulty, Duration
from .entities import ExerciseType, ExerciseRecord, ExercisePlan


class ExerciseService:
    """运动管理服务"""
    
    def create_exercise_type(
        self,
        name_zh: str,
        name_en: str,
        code: str,
        category: str,
        difficulty: str = "beginner",
        description: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> ExerciseType:
        """创建运动类型"""
        category_obj = ExerciseCategory(category)
        difficulty_obj = ExerciseDifficulty(difficulty)
        
        return ExerciseType(
            name_zh=name_zh,
            name_en=name_en,
            code=code,
            category=category_obj,
            difficulty=difficulty_obj,
            description=description,
            tenant_id=tenant_id
        )
    
    def calculate_calories(
        self,
        exercise_type: ExerciseType,
        user_weight_kg: float,
        duration_minutes: float
    ) -> float:
        """计算卡路里消耗"""
        # 简单计算公式
        base_rate = 0.035  # 每公斤每分钟基础消耗
        
        # 运动类型系数
        category_factors = {
            'strength': 0.8,
            'cardio': 1.2,
            'flexibility': 0.5,
            'balance': 0.6,
            'mixed': 1.0
        }
        
        category = str(exercise_type.category)
        category_factor = category_factors.get(category, 1.0)
        
        calories = user_weight_kg * base_rate * category_factor * duration_minutes
        return round(calories, 1)
    
    def analyze_progress(self, records: List[ExerciseRecord], days: int = 30) -> Dict[str, Any]:
        """分析运动进度"""
        if not records:
            return {'total_sessions': 0, 'total_minutes': 0, 'avg_minutes': 0}
        
        # 过滤最近记录
        cutoff = datetime.now() - timedelta(days=days)
        recent = [r for r in records if r.completed_at and r.completed_at >= cutoff]
        
        # 计算统计
        total_sessions = len(recent)
        total_minutes = 0
        
        for record in recent:
            if record.duration:
                total_minutes += record.duration.seconds / 60
        
        avg_minutes = total_minutes / total_sessions if total_sessions > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_minutes': round(total_minutes, 1),
            'avg_minutes': round(avg_minutes, 1),
            'consistency': self._calculate_consistency(total_sessions, days)
        }
    
    def _calculate_consistency(self, sessions: int, days: int) -> str:
        """计算一致性"""
        expected = days // 3  # 每周2-3次
        ratio = sessions / expected if expected > 0 else 0
        
        if ratio >= 1.0:
            return "优秀"
        elif ratio >= 0.7:
            return "良好"
        elif ratio >= 0.5:
            return "一般"
        else:
            return "需要改进"


class ExercisePlanService:
    """运动计划服务"""
    
    def create_plan(
        self,
        user_id: str,
        level: str,
        goal: str,
        days_per_week: int,
        minutes_per_day: int
    ) -> ExercisePlan:
        """创建运动计划"""
        plan_name = f"{level} {goal} 计划"
        description = f"{level}水平{goal}训练，每周{days_per_week}天，每天{minutes_per_day}分钟"
        
        plan = ExercisePlan(
            user_id=user_id,
            plan_name=plan_name,
            description=description,
            schedule={
                'days_per_week': days_per_week,
                'minutes_per_day': minutes_per_day
            }
        )
        
        # 添加示例计划项
        self._add_sample_items(plan, level, goal, days_per_week)
        
        return plan
    
    def _add_sample_items(self, plan: ExercisePlan, level: str, goal: str, days: int):
        """添加示例计划项"""
        # 根据水平和目标选择运动
        exercises = self._get_exercises_for_goal(level, goal)
        
        # 分配每天的运动
        for day in range(min(days, 7)):
            for i, (ex_code, sets, reps) in enumerate(exercises[:3]):  # 每天最多3个运动
                plan.add_plan_item(
                    exercise_type_id=ex_code,
                    day_of_week=day,
                    order=i + 1,
                    sets=sets,
                    repetitions=reps
                )
    
    def _get_exercises_for_goal(self, level: str, goal: str) -> List[tuple]:
        """根据目标获取运动"""
        # 基础运动库
        exercises = {
            'strength': [
                ('pushup', 3, 10),
                ('squat', 3, 12),
                ('plank', 3, 30),  # 秒
            ],
            'cardio': [
                ('running', 1, 20),  # 分钟
                ('jumping_jacks', 3, 50),
                ('high_knees', 3, 30),
            ],
            'flexibility': [
                ('stretching', 1, 15),
                ('yoga', 1, 20),
            ]
        }
        
        goal_map = {
            'weight_loss': 'cardio',
            'muscle_gain': 'strength',
            'general_fitness': 'strength'
        }
        
        exercise_type = goal_map.get(goal, 'strength')
        return exercises.get(exercise_type, exercises['strength'])