"""
任务领域服务
包含任务管理、分配、提交、评估等业务逻辑
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from .value_objects import (
    TaskType, TaskStatus, TaskPriority, TaskDifficulty,
    AssignmentStatus, EvaluationStatus, SubmissionStatus,
    TaskContent, TaskMetadata
)
from .entities import Task, TaskAssignment, TaskSubmission


class TaskService:
    """任务管理服务"""
    
    def create_task(
        self,
        title: str,
        task_type: str,
        created_by: str,
        tenant_id: Optional[str] = None,
        description: Optional[str] = None,
        priority: str = "medium",
        difficulty: str = "beginner",
        tags: Optional[List[str]] = None,
        content: Optional[Dict[str, Any]] = None,
        start_time: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        estimated_duration: Optional[int] = None
    ) -> Task:
        """创建新任务"""
        task_type_obj = TaskType(task_type)
        priority_obj = TaskPriority(priority)
        difficulty_obj = TaskDifficulty(difficulty)
        content_obj = TaskContent(content or {})
        
        task = Task(
            title=title,
            task_type=task_type_obj,
            created_by=created_by,
            tenant_id=tenant_id,
            description=description,
            priority=priority_obj,
            difficulty=difficulty_obj,
            tags=tags or [],
            content=content_obj,
            start_time=start_time,
            deadline=deadline,
            estimated_duration=estimated_duration
        )
        
        return task
    
    def validate_task_content(self, task_type: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """验证任务内容"""
        task_type_obj = TaskType(task_type)
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if task_type_obj.is_homework():
            # 作业任务验证
            if 'questions' not in content:
                validation_result['is_valid'] = False
                validation_result['errors'].append("作业任务必须包含questions字段")
            
            if 'questions' in content and not isinstance(content['questions'], list):
                validation_result['is_valid'] = False
                validation_result['errors'].append("questions必须是列表")
        
        elif task_type_obj.is_exercise():
            # 运动任务验证
            required_fields = ['exercise_type_id', 'sets', 'repetitions']
            for field in required_fields:
                if field not in content:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"运动任务必须包含{field}字段")
        
        elif task_type_obj.is_custom():
            # 自定义任务验证
            if 'custom_type' not in content:
                validation_result['warnings'].append("建议为自定义任务指定custom_type字段")
        
        return validation_result
    
    def calculate_estimated_duration(
        self,
        task_type: str,
        content: Dict[str, Any],
        difficulty: str
    ) -> int:
        """计算预计完成时间（分钟）"""
        difficulty_obj = TaskDifficulty(difficulty)
        base_duration = 30  # 基础30分钟
        
        if task_type == "homework":
            # 作业任务：根据问题数量计算
            question_count = len(content.get('questions', []))
            duration = question_count * 10  # 每个问题10分钟
        
        elif task_type == "exercise":
            # 运动任务：根据组数和次数计算
            sets = content.get('sets', 3)
            reps = content.get('repetitions', 10)
            rest = content.get('rest_between_sets', 60)  # 秒
            
            # 每组大约2分钟，加上休息时间
            exercise_time = sets * 2  # 分钟
            rest_time = (sets - 1) * (rest / 60)  # 分钟
            duration = exercise_time + rest_time
        
        else:
            # 自定义任务：基础时间
            duration = base_duration
        
        # 根据难度调整
        difficulty_multiplier = {
            'beginner': 0.8,
            'intermediate': 1.0,
            'advanced': 1.2,
            'expert': 1.5
        }
        
        multiplier = difficulty_multiplier.get(difficulty, 1.0)
        return int(duration * multiplier)
    
    def check_task_dependencies(self, task: Task, all_tasks: List[Task]) -> Dict[str, Any]:
        """检查任务依赖关系"""
        result = {
            'can_start': True,
            'blocking_tasks': [],
            'completed_dependencies': [],
            'pending_dependencies': []
        }
        
        for dep_id in task.dependencies:
            # 查找依赖任务
            dep_task = next((t for t in all_tasks if t.id == dep_id), None)
            
            if not dep_task:
                result['blocking_tasks'].append({
                    'task_id': dep_id,
                    'reason': '任务不存在'
                })
                result['can_start'] = False
            
            elif not dep_task.status.is_completed():
                result['blocking_tasks'].append({
                    'task_id': dep_id,
                    'reason': f'任务状态为{dep_task.status}，未完成'
                })
                result['pending_dependencies'].append(dep_id)
                result['can_start'] = False
            
            else:
                result['completed_dependencies'].append(dep_id)
        
        return result
    
    def suggest_deadline(
        self,
        start_time: datetime,
        estimated_duration: int,
        priority: str,
        user_schedule: Optional[Dict[str, Any]] = None
    ) -> datetime:
        """建议截止时间"""
        priority_obj = TaskPriority(priority)
        
        # 基础：开始时间 + 预计时间
        base_deadline = start_time + timedelta(minutes=estimated_duration)
        
        # 根据优先级调整
        priority_adjustments = {
            'urgent': timedelta(hours=2),  # 紧急任务：2小时内
            'high': timedelta(days=1),     # 高优先级：1天内
            'medium': timedelta(days=3),   # 中优先级：3天内
            'low': timedelta(days=7)       # 低优先级：7天内
        }
        
        adjustment = priority_adjustments.get(priority, timedelta(days=3))
        suggested_deadline = start_time + adjustment
        
        # 取较近的时间
        deadline = min(base_deadline, suggested_deadline)
        
        # 考虑用户日程
        if user_schedule and 'busy_periods' in user_schedule:
            # 这里可以添加更复杂的日程冲突检查
            pass
        
        return deadline


class AssignmentService:
    """任务分配服务"""
    
    def create_assignment(
        self,
        task_id: str,
        student_id: str,
        assigner_id: str,
        tenant_id: Optional[str] = None,
        expected_completion_time: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> TaskAssignment:
        """创建任务分配"""
        assignment = TaskAssignment(
            task_id=task_id,
            student_id=student_id,
            assigner_id=assigner_id,
            tenant_id=tenant_id,
            expected_completion_time=expected_completion_time,
            notes=notes
        )
        
        return assignment
    
    def can_assign_task(
        self,
        task: Task,
        student_id: str,
        existing_assignments: List[TaskAssignment]
    ) -> Dict[str, Any]:
        """检查是否可以分配任务"""
        result = {
            'can_assign': True,
            'reasons': [],
            'warnings': []
        }
        
        # 检查任务状态
        if not task.status.is_active():
            result['can_assign'] = False
            result['reasons'].append(f"任务状态为{task.status}，无法分配")
        
        # 检查是否已分配给该学员
        existing = next(
            (a for a in existing_assignments 
             if a.task_id == task.id and a.student_id == student_id),
            None
        )
        
        if existing:
            if existing.status.is_completed():
                result['warnings'].append("该学员已完成此任务")
            elif existing.status.is_in_progress():
                result['can_assign'] = False
                result['reasons'].append("该学员正在执行此任务")
            elif existing.status.is_assigned():
                result['can_assign'] = False
                result['reasons'].append("此任务已分配给该学员")
        
        # 检查学员当前任务负载
        active_assignments = [
            a for a in existing_assignments
            if a.student_id == student_id and 
            (a.status.is_assigned() or a.status.is_in_progress())
        ]
        
        if len(active_assignments) >= 5:  # 假设最大并发任务数为5
            result['warnings'].append(f"学员已有{len(active_assignments)}个活跃任务")
        
        return result
    
    def calculate_workload(
        self,
        student_id: str,
        assignments: List[TaskAssignment],
        tasks: List[Task]
    ) -> Dict[str, Any]:
        """计算学员工作负载"""
        student_assignments = [
            a for a in assignments if a.student_id == student_id
        ]
        
        # 活跃任务
        active_assignments = [
            a for a in student_assignments
            if a.status.is_assigned() or a.status.is_in_progress()
        ]
        
        # 计算总预计时间
        total_estimated = 0
        for assignment in active_assignments:
            task = next((t for t in tasks if t.id == assignment.task_id), None)
            if task and task.estimated_duration:
                total_estimated += task.estimated_duration
        
        # 计算逾期任务
        overdue_assignments = [
            a for a in student_assignments
            if a.is_overdue() and not a.status.is_completed()
        ]
        
        return {
            'total_assignments': len(student_assignments),
            'active_assignments': len(active_assignments),
            'overdue_assignments': len(overdue_assignments),
            'total_estimated_minutes': total_estimated,
            'workload_level': self._calculate_workload_level(len(active_assignments), total_estimated)
        }
    
    def _calculate_workload_level(self, active_count: int, total_minutes: int) -> str:
        """计算工作负载级别"""
        if active_count == 0:
            return "空闲"
        elif active_count <= 2 and total_minutes <= 120:
            return "轻松"
        elif active_count <= 4 and total_minutes <= 240:
            return "适中"
        elif active_count <= 6 and total_minutes <= 360:
            return "繁忙"
        else:
            return "超载"
    
    def suggest_assignment_schedule(
        self,
        task: Task,
        student_id: str,
        existing_assignments: List[TaskAssignment],
        student_schedule: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """建议分配计划"""
        suggestions = {
            'recommended_start_time': None,
            'recommended_deadline': None,
            'estimated_completion_time': None,
            'schedule_conflicts': [],
            'recommendations': []
        }
        
        # 基础：任务开始时间作为建议开始时间
        if task.start_time:
            suggestions['recommended_start_time'] = task.start_time
        else:
            suggestions['recommended_start_time'] = datetime.now()
        
        # 基础：任务截止时间作为建议截止时间
        if task.deadline:
            suggestions['recommended_deadline'] = task.deadline
        elif task.estimated_duration:
            suggestions['recommended_deadline'] = (
                suggestions['recommended_start_time'] + 
                timedelta(minutes=task.estimated_duration)
            )
        
        # 检查与其他任务的冲突
        student_active_assignments = [
            a for a in existing_assignments
            if a.student_id == student_id and
            (a.status.is_assigned() or a.status.is_in_progress())
        ]
        
        for assignment in student_active_assignments:
            assigned_task = next((t for t in [task] if t.id == assignment.task_id), None)
            if assigned_task and assigned_task.deadline:
                # 检查截止时间冲突
                if (suggestions['recommended_start_time'] and 
                    suggestions['recommended_start_time'] < assigned_task.deadline):
                    suggestions['schedule_conflicts'].append({
                        'task_id': assignment.task_id,
                        'conflict_type': 'deadline_overlap',
                        'message': f"与任务'{assigned_task.title}'的截止时间冲突"
                    })
        
        # 根据优先级调整建议
        if task.priority.is_urgent():
            suggestions['recommendations'].append("这是紧急任务，建议立即开始")
        elif task.priority.is_high_or_urgent():
            suggestions['recommendations'].append("这是高优先级任务，建议优先处理")
        
        # 考虑学生日程
        if student_schedule:
            # 这里可以添加更复杂的日程匹配逻辑
            pass
        
        return suggestions


class EvaluationService:
    """任务评估服务"""
    
    def evaluate_submission(
        self,
        submission: TaskSubmission,
        evaluator_id: str,
        score: float,
        feedback: str,
        criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """评估任务提交"""
        evaluation_result = {
            'submission_id': submission.id,
            'evaluator_id': evaluator_id,
            'score': score,
            'feedback': feedback,
            'criteria_scores': {},
            'overall_rating': None,
            'recommendations': [],
            'is_passed': False
        }
        
        # 验证分数范围
        if not 0.0 <= score <= 100.0:
            raise ValueError("分数必须在0-100之间")
        
        # 计算总体评级
        evaluation_result['overall_rating'] = self._calculate_rating(score)
        
        # 检查是否通过（假设60分及格）
        evaluation_result['is_passed'] = score >= 60.0
        
        # 根据分数生成建议
        if score < 60.0:
            evaluation_result['recommendations'].append("未达到及格标准，建议重新学习相关知识点")
        elif score < 80.0:
            evaluation_result['recommendations'].append("表现良好，但仍有提升空间")
        elif score < 90.0:
            evaluation_result['recommendations'].append("表现优秀，继续保持")
        else:
            evaluation_result['recommendations'].append("表现卓越，值得表扬")
        
        # 如果有评估标准，计算各项得分
        if criteria:
            evaluation_result['criteria_scores'] = self._evaluate_by_criteria(
                submission, criteria
            )
        
        return evaluation_result
    
    def _calculate_rating(self, score: float) -> str:
        """根据分数计算评级"""
        if score >= 90.0:
            return "卓越"
        elif score >= 80.0:
            return "优秀"
        elif score >= 70.0:
            return "良好"
        elif score >= 60.0:
            return "及格"
        else:
            return "不及格"
    
    def _evaluate_by_criteria(
        self,
        submission: TaskSubmission,
        criteria: Dict[str, Any]
    ) -> Dict[str, float]:
        """根据标准评估"""
        criteria_scores = {}
        
        # 这里可以实现具体的标准评估逻辑
        # 例如：内容完整性、技术正确性、创新性等
        
        return criteria_scores
    
    def generate_feedback_template(
        self,
        submission: TaskSubmission,
        score: float,
        task_type: str
    ) -> str:
        """生成反馈模板"""
        templates = {
            'homework': self._generate_homework_feedback,
            'exercise': self._generate_exercise_feedback,
            'custom': self._generate_custom_feedback
        }
        
        generator = templates.get(task_type, self._generate_general_feedback)
        return generator(submission, score)
    
    def _generate_homework_feedback(self, submission: TaskSubmission, score: float) -> str:
        """生成作业反馈"""
        if score >= 80.0:
            return f"作业完成得很好！得分：{score}。继续保持！"
        elif score >= 60.0:
            return f"作业基本完成，得分：{score}。建议检查错误并改进。"
        else:
            return f"作业需要改进，得分：{score}。请重新学习相关知识点。"
    
    def _generate_exercise_feedback(self, submission: TaskSubmission, score: float) -> str:
        """生成运动任务反馈"""
        if score >= 80.0:
            return f"运动完成得很好！得分：{score}。动作标准，继续保持！"
        elif score >= 60.0:
            return f"运动基本完成，得分：{score}。注意动作规范性。"
        else:
            return f"运动需要改进，得分：{score}。建议观看标准动作视频。"
    
    def _generate_custom_feedback(self, submission: TaskSubmission, score: float) -> str:
        """生成自定义任务反馈"""
        return f"任务完成情况：得分{score}。请根据具体内容提供详细反馈。"
    
    def _generate_general_feedback(self, submission: TaskSubmission, score: float) -> str:
        """生成通用反馈"""
        return f"任务评估完成，得分：{score}。"