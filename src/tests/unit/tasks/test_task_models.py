"""
任务模型单元测试
测试任务相关的数据库模型
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from coding.database.models import Task, TaskAssignment, TaskSubmission, TaskEvaluation, User, Tenant
from coding.database.session import get_db_session


class TestTaskModel:
    """测试任务模型"""
    
    def test_create_task(self, db_session: Session, test_tenant: Tenant, test_user: User):
        """测试创建任务"""
        task = Task(
            title="数学作业",
            description="完成第一章练习题",
            task_type="homework",
            status="draft",
            priority="medium",
            difficulty="beginner",
            tags=["数学", "作业"],
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        assert task.id is not None
        assert task.title == "数学作业"
        assert task.task_type == "homework"
        assert task.status == "draft"
        assert task.priority == "medium"
        assert task.difficulty == "beginner"
        assert "数学" in task.tags
        assert task.creator_id == test_user.id
        assert task.tenant_id == test_tenant.id
    
    def test_task_to_dict(self, db_session: Session, test_tenant: Tenant, test_user: User):
        """测试任务转换为字典"""
        task = Task(
            title="英语阅读",
            description="阅读一篇英文文章",
            task_type="homework",
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        task_dict = task.to_dict()
        
        assert task_dict["id"] == task.id
        assert task_dict["title"] == "英语阅读"
        assert task_dict["task_type"] == "homework"
        assert task_dict["status"] == "draft"
        assert "created_at" in task_dict
        assert "updated_at" in task_dict
    
    def test_task_is_overdue(self, db_session: Session, test_tenant: Tenant, test_user: User):
        """测试任务是否过期"""
        # 未设置截止时间的任务
        task1 = Task(
            title="无截止时间任务",
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        # 已过期的任务
        task2 = Task(
            title="已过期任务",
            deadline=datetime.utcnow() - timedelta(days=1),
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        # 未过期的任务
        task3 = Task(
            title="未过期任务",
            deadline=datetime.utcnow() + timedelta(days=1),
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        assert not task1.is_overdue()
        assert task2.is_overdue()
        assert not task3.is_overdue()
    
    def test_task_can_be_assigned(self, db_session: Session, test_tenant: Tenant, test_user: User):
        """测试任务是否可以分配"""
        # 草稿状态的任务
        task1 = Task(
            title="草稿任务",
            status="draft",
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        # 活跃状态的任务
        task2 = Task(
            title="活跃任务",
            status="active",
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        # 已完成的任务
        task3 = Task(
            title="已完成任务",
            status="completed",
            creator_id=test_user.id,
            tenant_id=test_tenant.id
        )
        
        assert task1.can_be_assigned()
        assert task2.can_be_assigned()
        assert not task3.can_be_assigned()


class TestTaskAssignmentModel:
    """测试任务分配模型"""
    
    def test_create_assignment(self, db_session: Session, test_tenant: Tenant, 
                              test_user: User, test_task: Task, test_student: User):
        """测试创建任务分配"""
        assignment = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="assigned",
            progress=0.0,
            tenant_id=test_tenant.id
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        assert assignment.id is not None
        assert assignment.task_id == test_task.id
        assert assignment.student_id == test_student.id
        assert assignment.assigner_id == test_user.id
        assert assignment.status == "assigned"
        assert assignment.progress == 0.0
        assert assignment.tenant_id == test_tenant.id
    
    def test_update_progress(self, db_session: Session, test_tenant: Tenant,
                            test_user: User, test_task: Task, test_student: User):
        """测试更新进度"""
        assignment = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="assigned",
            progress=0.0,
            tenant_id=test_tenant.id
        )
        
        db_session.add(assignment)
        db_session.commit()
        db_session.refresh(assignment)
        
        # 更新进度到50%
        success = assignment.update_progress(50.0, {"details": "完成了一半"})
        db_session.commit()
        db_session.refresh(assignment)
        
        assert success
        assert assignment.progress == 50.0
        assert assignment.status == "in_progress"
        assert assignment.started_at is not None
        assert len(assignment.progress_details) == 1
        
        # 更新进度到100%
        success = assignment.update_progress(100.0, {"details": "全部完成"})
        db_session.commit()
        db_session.refresh(assignment)
        
        assert success
        assert assignment.progress == 100.0
        assert assignment.status == "completed"
        assert assignment.completed_at is not None
    
    def test_assignment_is_overdue(self, db_session: Session, test_tenant: Tenant,
                                  test_user: User, test_task: Task, test_student: User):
        """测试分配是否过期"""
        # 未设置预计完成时间的分配
        assignment1 = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="assigned",
            tenant_id=test_tenant.id
        )
        
        # 已过期的分配
        assignment2 = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="assigned",
            expected_completion_at=datetime.utcnow() - timedelta(days=1),
            tenant_id=test_tenant.id
        )
        
        # 未过期的分配
        assignment3 = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="assigned",
            expected_completion_at=datetime.utcnow() + timedelta(days=1),
            tenant_id=test_tenant.id
        )
        
        # 已完成的任务不过期
        assignment4 = TaskAssignment(
            task_id=test_task.id,
            student_id=test_student.id,
            assigner_id=test_user.id,
            status="completed",
            expected_completion_at=datetime.utcnow() - timedelta(days=1),
            tenant_id=test_tenant.id
        )
        
        assert not assignment1.is_overdue()
        assert assignment2.is_overdue()
        assert not assignment3.is_overdue()
        assert not assignment4.is_overdue()


class TestTaskSubmissionModel:
    """测试任务提交模型"""
    
    def test_create_submission(self, db_session: Session, test_tenant: Tenant,
                              test_user: User, test_assignment: TaskAssignment):
        """测试创建任务提交"""
        submission = TaskSubmission(
            assignment_id=test_assignment.id,
            submitter_id=test_user.id,
            status="submitted",
            content={"type": "text", "text": "这是我的作业"},
            version=1,
            tenant_id=test_tenant.id
        )
        
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)
        
        assert submission.id is not None
        assert submission.assignment_id == test_assignment.id
        assert submission.submitter_id == test_user.id
        assert submission.status == "submitted"
        assert submission.content["type"] == "text"
        assert submission.version == 1
        assert submission.tenant_id == test_tenant.id
    
    def test_review_submission(self, db_session: Session, test_tenant: Tenant,
                              test_user: User, test_reviewer: User, test_assignment: TaskAssignment):
        """测试审核任务提交"""
        submission = TaskSubmission(
            assignment_id=test_assignment.id,
            submitter_id=test_user.id,
            status="submitted",
            content={"type": "text", "text": "这是我的作业"},
            version=1,
            tenant_id=test_tenant.id
        )
        
        db_session.add(submission)
        db_session.commit()
        db_session.refresh(submission)
        
        # 审核提交
        success = submission.review(test_reviewer.id, "accepted", "作业完成得很好")
        db_session.commit()
        db_session.refresh(submission)
        
        assert success
        assert submission.status == "accepted"
        assert submission.reviewer_id == test_reviewer.id
        assert submission.reviewed_at is not None
        assert submission.review_notes == "作业完成得很好"
    
    def test_get_content_summary(self, db_session: Session, test_tenant: Tenant,
                                test_user: User, test_assignment: TaskAssignment):
        """测试获取内容摘要"""
        # 文本类型提交
        submission1 = TaskSubmission(
            assignment_id=test_assignment.id,
            submitter_id=test_user.id,
            status="submitted",
            content={"type": "text", "text": "这是一段很长的文本内容，需要被截断"},
            tenant_id=test_tenant.id
        )
        
        # 运动类型提交
        submission2 = TaskSubmission(
            assignment_id=test_assignment.id,
            submitter_id=test_user.id,
            status="submitted",
            content={"type": "exercise", "exercise_type": "俯卧撑", "count": 50},
            tenant_id=test_tenant.id
        )
        
        # 文件类型提交
        submission3 = TaskSubmission(
            assignment_id=test_assignment.id,
            submitter_id=test_user.id,
            status="submitted",
            content={"type": "file", "files": ["file1.pdf", "file2.jpg"]},
            tenant_id=test_tenant.id
        )
        
        summary1 = submission1.get_content_summary()
        summary2 = submission2.get_content_summary()
        summary3 = submission3.get_content_summary()
        
        assert "这是一段很长的文本内容" in summary1
        assert "运动任务：俯卧撑，完成50次" in summary2
        assert "文件提交：2个文件" in summary3


class TestTaskEvaluationModel:
    """测试任务评价模型"""
    
    def test_create_evaluation(self, db_session: Session, test_tenant: Tenant,
                              test_user: User, test_reviewer: User, test_assignment: TaskAssignment):
        """测试创建任务评价"""
        evaluation = TaskEvaluation(
            assignment_id=test_assignment.id,
            evaluator_id=test_reviewer.id,
            student_id=test_user.id,
            overall_score=85.5,
            comments="作业完成得很好",
            status="draft",
            tenant_id=test_tenant.id
        )
        
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)
        
        assert evaluation.id is not None
        assert evaluation.assignment_id == test_assignment.id
        assert evaluation.evaluator_id == test_reviewer.id
        assert evaluation.student_id == test_user.id
        assert evaluation.overall_score == 85.5
        assert evaluation.comments == "作业完成得很好"
        assert evaluation.status == "draft"
        assert evaluation.tenant_id == test_tenant.id
    
    def test_get_score_grade(self, db_session: Session, test_tenant: Tenant,
                            test_user: User, test_reviewer: User, test_assignment: TaskAssignment):
        """测试获取评分等级"""
        # A+等级
        evaluation1 = TaskEvaluation(
            assignment_id=test_assignment.id,
            evaluator_id=test_reviewer.id,
            student_id=test_user.id,
            overall_score=95.0,
            tenant_id=test_tenant.id
        )
        
        # B等级
        evaluation2 = TaskEvaluation(
            assignment_id=test_assignment.id,
            evaluator_id=test_reviewer.id,
            student_id=test_user.id,
            overall_score=72.0,
            tenant_id=test_tenant.id
        )
        
        # F等级
        evaluation3 = TaskEvaluation(
            assignment_id=test_assignment.id,
            evaluator_id=test_reviewer.id,
            student_id=test_user.id,
            overall_score=35.0,
            tenant_id=test_tenant.id
        )
        
        assert evaluation1.get_score_grade() == "A+"
        assert evaluation2.get_score_grade() == "B"
        assert evaluation3.get_score_grade() == "F"
    
    def test_update_score_details(self, db_session: Session, test_tenant: Tenant,
                                 test_user: User, test_reviewer: User, test_assignment: TaskAssignment):
        """测试更新评分详情"""
        evaluation = TaskEvaluation(
            assignment_id=test_assignment.id,
            evaluator_id=test_reviewer.id,
            student_id=test_user.id,
            overall_score=0.0,
            tenant_id=test_tenant.id
        )
        
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)
        
        # 更新评分详情
        score_details = {
            "完成度": 85.0,
            "准确性": 90.0,
            "创新性": 80.0,
            "规范性": 75.0
        }
        
        success = evaluation.update_score_details(score_details)
        db_session.commit()
        db_session.refresh(evaluation)
        
        assert success
        assert evaluation.score_details == score_details
        assert evaluation.overall_score == 82.5  # (85+90+80+75)/4 = 82.5


# 测试夹具
@pytest.fixture
def test_tenant(db_session: Session) -> Tenant:
    """测试租户夹具"""
    tenant = Tenant(
        name="测试租户",
        code="test_tenant"
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session: Session, test_tenant: Tenant) -> User:
    """测试用户夹具"""
    user = User(
        username="test_user",
        email="test@example.com",
        tenant_id=test_tenant.id
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_student(db_session: Session, test_tenant: Tenant) -> User:
    """测试学员夹具"""
    student = User(
        username="test_student",
        email="student@example.com",
        tenant_id=test_tenant.id
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_reviewer(db_session: Session, test_tenant: Tenant) -> User:
    """测试审核者夹具"""
    reviewer = User(
        username="test_reviewer",
        email="reviewer@example.com",
        tenant_id=test_tenant.id
    )
    db_session.add(reviewer)
    db_session.commit()
    db_session.refresh(reviewer)
    return reviewer


@pytest.fixture
def test_task(db_session: Session, test_tenant: Tenant, test_user: User) -> Task:
    """测试任务夹具"""
    task = Task(
        title="测试任务",
        description="测试任务描述",
        task_type="homework",
        creator_id=test_user.id,
        tenant_id=test_tenant.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_assignment(db_session: Session, test_tenant: Tenant, 
                   test_user: User, test_task: Task, test_student: User) -> TaskAssignment:
    """测试任务分配夹具"""
    assignment = TaskAssignment(
        task_id=test_task.id,
        student_id=test_student.id,
        assigner_id=test_user.id,
        status="assigned",
        progress=0.0,
        tenant_id=test_tenant.id
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    return assignment