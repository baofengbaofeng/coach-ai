"""
运动领域服务
包含运动类型管理、运动记录跟踪、运动计划制定等业务逻辑
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .value_objects import (
    ExerciseCategory, ExerciseDifficulty, Duration,
    Repetition, Weight, Intensity
)
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
        standard_movement: Optional[str] = None,
        standard_video_url: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> ExerciseType:
        """创建运动类型"""
        category_obj = ExerciseCategory(category)
        difficulty_obj = ExerciseDifficulty(difficulty)
        
        exercise_type = ExerciseType(
            name_zh=name_zh,
            name_en=name_en,
            code=code,
            category=category_obj,
            difficulty=difficulty_obj,
            description=description,
            standard_movement=standard_movement,
            standard_video_url=standard_video_url,
            tenant_id=tenant_id
        )
        
        return exercise_type
    
    def validate_exercise_type_code(self, code: str) -> Dict[str, Any]:
        """验证运动类型代码"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'suggestions': []
        }
        
        # 检查长度
        if len(code) < 3:
            validation_result['is_valid'] = False
            validation_result['errors'].append("运动类型代码长度必须至少3个字符")
        
        # 检查格式（建议使用小写字母、数字、下划线）
        if not code.replace('_', '').isalnum():
            validation_result['errors'].append("运动类型代码只能包含字母、数字和下划线")
            validation_result['is_valid'] = False
        
        # 建议使用小写
        if code != code.lower():
            validation_result['suggestions'].append(f"建议使用小写: {code.lower()}")
        
        return validation_result
    
    def calculate_calories_burned(
        self,
        exercise_type: ExerciseType,
        user_weight_kg: float,
        duration_minutes: float,
        intensity_level: int = 5
    ) -> float:
        """计算卡路里消耗"""
        # 基础代谢率（BMR）因子
        bmr_factor = 1.2
        
        # 运动强度因子（1-10）
        intensity_factor = intensity_level / 10.0
        
        # 运动类型因子
        category_factors = {
            'strength': 0.8,    # 力量训练
            'cardio': 1.2,      # 有氧运动
            'flexibility': 0.5, # 柔韧性训练
            'balance': 0.6,     # 平衡训练
            'mixed': 1.0        # 混合训练
        }
        
        category = str(exercise_type.category)
        category_factor = category_factors.get(category, 1.0)
        
        # 难度因子
        difficulty_factors = {
            'beginner': 0.7,
            'intermediate': 1.0,
            'advanced': 1.3,
            'expert': 1.6
        }
        
        difficulty = str(exercise_type.difficulty)
        difficulty_factor = difficulty_factors.get(difficulty, 1.0)
        
        # 计算公式：基础代谢 × 强度 × 类型 × 难度 × 时间
        base_calories = user_weight_kg * 0.035  # 每公斤每分钟基础消耗
        calories = (
            base_calories * 
            bmr_factor * 
            intensity_factor * 
            category_factor * 
            difficulty_factor * 
            duration_minutes
        )
        
        return round(calories, 1)
    
    def suggest_exercise_plan(
        self,
        user_level: str,
        goal: str,
        available_time_minutes: int,
        equipment_available: List[str] = None
    ) -> Dict[str, Any]:
        """建议运动计划"""
        suggestions = {
            'warmup': [],
            'main_exercises': [],
            'cooldown': [],
            'total_duration': 0,
            'estimated_calories': 0
        }
        
        # 根据用户水平选择难度
        level_difficulties = {
            'beginner': 'beginner',
            'intermediate': 'intermediate',
            'advanced': 'advanced',
            'expert': 'expert'
        }
        
        difficulty = level_difficulties.get(user_level, 'beginner')
        
        # 根据目标选择运动类型
        goal_categories = {
            'strength': ['strength'],
            'cardio': ['cardio'],
            'flexibility': ['flexibility'],
            'weight_loss': ['cardio', 'strength'],
            'muscle_gain': ['strength'],
            'general_fitness': ['strength', 'cardio', 'flexibility']
        }
        
        categories = goal_categories.get(goal, ['strength', 'cardio'])
        
        # 热身建议（5-10分钟）
        warmup_duration = min(10, available_time_minutes // 10)
        if warmup_duration > 0:
            suggestions['warmup'].append({
                'type': 'dynamic_stretching',
                'duration_minutes': warmup_duration,
                'description': '动态拉伸和关节活动'
            })
            suggestions['total_duration'] += warmup_duration
        
        # 主要运动建议
        main_duration = available_time_minutes - warmup_duration - 5  # 留5分钟冷却
        if main_duration > 10:
            # 根据可用时间分配运动
            if main_duration <= 20:
                # 短时间：单一类型
                exercise_type = categories[0] if categories else 'strength'
                suggestions['main_exercises'].append({
                    'category': exercise_type,
                    'duration_minutes': main_duration,
                    'intensity': 'moderate'
                })
            else:
                # 长时间：多种类型
                for i, category in enumerate(categories[:2]):  # 最多两种类型
                    if i == 0:
                        duration = main_duration * 0.6  # 60%时间给主要类型
                    else:
                        duration = main_duration * 0.4  # 40%时间给次要类型
                    
                    suggestions['main_exercises'].append({
                        'category': category,
                        'duration_minutes': int(duration),
                        'intensity': 'moderate'
                    })
            
            suggestions['total_duration'] += main_duration
        
        # 冷却建议（5分钟）
        cooldown_duration = 5
        suggestions['cooldown'].append({
            'type': 'static_stretching',
            'duration_minutes': cooldown_duration,
            'description': '静态拉伸和放松'
        })
        suggestions['total_duration'] += cooldown_duration
        
        # 估算卡路里消耗（假设用户体重70kg）
        estimated_calories = self._estimate_plan_calories(suggestions, 70.0)
        suggestions['estimated_calories'] = estimated_calories
        
        return suggestions
    
    def _estimate_plan_calories(self, plan: Dict[str, Any], user_weight_kg: float) -> float:
        """估算计划卡路里消耗"""
        total_calories = 0.0
        
        # 估算热身消耗
        for warmup in plan['warmup']:
            duration = warmup['duration_minutes']
            # 热身：低强度，约3-4 METs
            calories = user_weight_kg * 0.035 * 3.5 * duration
            total_calories += calories
        
        # 估算主要运动消耗
        for exercise in plan['main_exercises']:
            duration = exercise['duration_minutes']
            category = exercise['category']
            
            # METs值（代谢当量）
            mets_values = {
                'strength': 6.0,      # 力量训练
                'cardio': 8.0,        # 有氧运动
                'flexibility': 2.5,   # 柔韧性训练
                'balance': 3.0        # 平衡训练
            }
            
            mets = mets_values.get(category, 5.0)
            calories = user_weight_kg * 0.035 * mets * duration
            total_calories += calories
        
        # 估算冷却消耗
        for cooldown in plan['cooldown']:
            duration = cooldown['duration_minutes']
            # 冷却：低强度，约2-3 METs
            calories = user_weight_kg * 0.035 * 2.5 * duration
            total_calories += calories
        
        return round(total_calories, 1)
    
    def analyze_exercise_progress(
        self,
        exercise_records: List[ExerciseRecord],
        period_days: int = 30
    ) -> Dict[str, Any]:
        """分析运动进度"""
        if not exercise_records:
            return {
                'total_sessions': 0,
                'total_duration_minutes': 0,
                'average_duration_minutes': 0,
                'total_calories': 0,
                'consistency_score': 0,
                'progress_trend': 'no_data',
                'recommendations': []
            }
        
        # 过滤指定时间段内的记录
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_records = [
            r for r in exercise_records
            if r.completed_at and r.completed_at >= cutoff_date
        ]
        
        # 基本统计
        total_sessions = len(recent_records)
        
        total_duration = 0
        total_calories = 0
        
        for record in recent_records:
            if record.duration:
                # 将Duration对象转换为分钟
                duration_minutes = record.duration.seconds / 60
                total_duration += duration_minutes
            
            if record.calories_burned:
                total_calories += record.calories_burned
        
        average_duration = total_duration / total_sessions if total_sessions > 0 else 0
        
        # 一致性评分（基于运动频率）
        expected_sessions = period_days // 3  # 假设每周2-3次
        consistency_score = min(100, (total_sessions / expected_sessions) * 100) if expected_sessions > 0 else 0
        
        # 进度趋势分析
        progress_trend = self._analyze_trend(recent_records)
        
        # 生成建议
        recommendations = self._generate_progress_recommendations(
            total_sessions, average_duration, consistency_score, progress_trend
        )
        
        return {
            'total_sessions': total_sessions,
            'total_duration_minutes': round(total_duration, 1),
            'average_duration_minutes': round(average_duration, 1),
            'total_calories': round(total_calories, 1),
            'consistency_score': round(consistency_score, 1),
            'progress_trend': progress_trend,
            'recommendations': recommendations
        }
    
    def _analyze_trend(self, records: List[ExerciseRecord]) -> str:
        """分析趋势"""
        if len(records) < 4:
            return 'insufficient_data'
        
        # 按时间排序
        sorted_records = sorted(records, key=lambda r: r.completed_at)
        
        # 分成两半比较
        midpoint = len(sorted_records) // 2
        first_half = sorted_records[:midpoint]
        second_half = sorted_records[midpoint:]
        
        # 计算平均持续时间
        def avg_duration(records_list):
            durations = []
            for r in records_list:
                if r.duration:
                    durations.append(r.duration.seconds / 60)
            return sum(durations) / len(durations) if durations else 0
        
        first_avg = avg_duration(first_half)
        second_avg = avg_duration(second_half)
        
        if second_avg > first_avg * 1.2:
            return 'improving'
        elif second_avg < first_avg * 0.8:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_progress_recommendations(
        self,
        total_sessions: int,
        average_duration: float,
        consistency_score: float,
        progress_trend: str
    ) -> List[str]:
        """生成进度建议"""
        recommendations = []
        
        # 基于会话次数
        if total_sessions < 8:
            recommendations.append("建议增加运动频率，目标每周至少2-3次")
        elif total_sessions > 20:
            recommendations.append("运动频率很好，继续保持！")
        
        # 基于平均持续时间
        if average_duration < 20:
            recommendations.append("建议延长每次运动时间，目标30分钟以上")
        elif average_duration > 60:
            recommendations.append("运动时间充足，注意适当休息")
        
        # 基于一致性评分
        if consistency_score < 60:
            recommendations.append("运动一致性有待提高，尝试制定固定运动计划")
        elif consistency_score > 90:
            recommendations.append("运动一致性优秀！")
        
        # 基于趋势
        if progress_trend == 'declining':
            recommendations.append("近期运动表现有所下降，检查是否有过度训练或需要调整计划")
        elif progress_trend == 'improving':
            recommendations.append("运动表现持续提升，很棒！")
        
        return recommendations


class ExercisePlanService:
    """运动计划服务"""
    
    def create_personalized_plan(
        self,
        user_id: str,
        fitness_level: str,
        goals: List[str],
        available_days: List[int],  # 0-6，0表示周日
        daily_time_minutes: int,
        preferences: Optional[Dict[str, Any]] = None
    ) -> ExercisePlan:
        """创建个性化运动计划"""
        plan_name = f"{fitness_level.capitalize()} {goals[0]} 计划"
        description = self._generate_plan_description(fitness_level, goals)
        
        # 创建计划
        plan = ExercisePlan(
            user_id=user_id,
            plan_name=plan_name,
            description=description,
            schedule=self._generate_schedule(available_days, daily_time_minutes),
            is_active=True
        )
        
        # 添加计划项
        self._add_plan_items(plan, fitness_level, goals, available_days, daily_time_minutes, preferences)
        
        return plan
    
    def _generate_plan_description(self, fitness_level: str, goals: List[str]) -> str:
        """生成计划描述"""
        level_descriptions = {
            'beginner': '初级',
            'intermediate': '中级',
            'advanced': '高级',
            'expert': '专家'
        }
        
        goal_descriptions = {
            'weight_loss': '减脂',
            'muscle_gain': '增肌',
            'strength': '力量提升',
            'endurance': '耐力提升',
            'flexibility': '柔韧性提升',
            'general_fitness': '综合健身'
        }
        
        level_desc = level_descriptions.get(fitness_level, '适合')
        goal_desc = '、'.join([goal_descriptions.get(g, g) for g in goals[:2]])
        
        return f"{level_desc}水平的{goal_desc}训练计划"
    
    def _generate_schedule(self, available_days: List[int], daily_time_minutes: int) -> Dict[str, Any]:
        """生成计划安排"""
        schedule = {
            'available_days': available_days,
            'daily_time_minutes': daily_time_minutes,
            'weekly_sessions': len(available_days),
            'total_weekly_minutes': len(available_days) * daily_time_minutes
        }
        
        # 添加建议休息日
        all_days = set(range(7))
        available_set = set(available_days)
        rest_days = list(all_days - available_set)
        
        if rest_days:
            schedule['recommended_rest_days'] = rest_days
        
        return schedule
    
    def _add_plan_items(
        self,
        plan: ExercisePlan,
        fitness_level: str,
        goals: List[str],
        available_days: List[int],
        daily_time_minutes: int,
        preferences: Optional[Dict[str, Any]]
    ):
        """添加计划项"""
        # 根据水平和目标选择运动类型
        exercise_types = self._select_exercise_types(fitness_level, goals, preferences)
        
        # 分配每天的运动
        for day_index, day_of_week in enumerate(available_days):
            # 根据星期几选择不同类型的运动
            day_type = self._get_day_type(day_index, len(available_days))
            
            # 选择适合当天的运动
            day_exercises = self._get_day_exercises(exercise_types, day_type, fitness_level)
            
            # 添加运动项
            for i, (exercise_code, sets, reps) in enumerate(day_exercises):
                plan.add_plan_item(
                    exercise_type_id=exercise_code,
                    day_of_week=day_of_week,
                    order=i + 1,
                    sets=sets,
                    repetitions=reps
                )
    
    def _select_exercise_types(
        self,
        fitness_level: str,
        goals: List[str],
        preferences: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """选择运动类型"""
        # 基础运动类型库
        exercise_library = {
            'strength': [
                {'code': 'pushup', 'name_zh': '俯卧撑', 'sets': 3, 'reps': 10},
                {'code': 'squat', '