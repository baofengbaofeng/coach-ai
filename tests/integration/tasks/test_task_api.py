"""
任务API集成测试
测试任务相关的API接口
"""

import pytest
import json
from datetime import datetime, timedelta
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from coding.main import create_app
from coding.database.models import User, Tenant
from coding.database.session import get_db_session
from tests.integration.conftest import create_test_user, get_auth_headers


class TestTaskAPI(AsyncHTTPTestCase):
    """测试任务API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户",
            code="test_tenant_api"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_api")
        self.db.commit()
        
        # 创建测试学员
        self.student = create_test_user(self.db, self.tenant.id, "test_student_api", "student@example.com")
        self.db.commit()
        
        # 获取认证头
        self.headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_create_task(self):
        """测试创建任务"""
        task_data = {
            "title": "API测试任务",
            "description": "这是通过API创建的任务",
            "task_type": "homework",
            "priority": "medium",
            "difficulty": "beginner",
            "tags": ["测试", "API"],
            "estimated_duration": 60
        }
        
        response = self.fetch(
            "/api/v1/tasks",
            method="POST",
            headers=self.headers,
            body=json.dumps(task_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["title"] == "API测试任务"
        assert result["data"]["task_type"] == "homework"
        assert result["data"]["status"] == "draft"
        assert result["data"]["creator_id"] == self.user.id
        assert result["data"]["tenant_id"] == self.tenant.id
    
    def test_get_task(self):
        """测试获取任务"""
        # 首先创建任务
        task_data = {
            "title": "获取测试任务",
            "description": "用于测试获取的任务",
            "task_type": "exercise"
        }
        
        create_response = self.fetch(
            "/api/v1/tasks",
            method="POST",
            headers=self.headers,
            body=json.dumps(task_data)
        )
        
        assert create_response.code == 200
        created_task = json.loads(create_response.body)["data"]
        task_id = created_task["id"]
        
        # 然后获取任务
        response = self.fetch(
            f"/api/v1/tasks/{task_id}",
            method="GET",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["id"] == task_id
        assert result["data"]["title"] == "获取测试任务"
        assert result["data"]["task_type"] == "exercise"
    
    def test_list_tasks(self):
        """测试列出任务"""
        # 创建几个测试任务
        for i in range(3):
            task_data = {
                "title": f"测试任务{i+1}",
                "description": f"测试任务描述{i+1}",
                "task_type": "homework"
            }
            
            self.fetch(
                "/api/v1/tasks",
                method="POST",
                headers=self.headers,
                body=json.dumps(task_data)
            )
        
        # 获取任务列表
        response = self.fetch(
            "/api/v1/tasks",
            method="GET",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert "tasks" in result["data"]
        assert "pagination" in result["data"]
        assert len(result["data"]["tasks"]) > 0
    
    def test_update_task(self):
        """测试更新任务"""
        # 首先创建任务
        task_data = {
            "title": "原始任务",
            "description": "原始描述",
            "task_type": "homework"
        }
        
        create_response = self.fetch(
            "/api/v1/tasks",
            method="POST",
            headers=self.headers,
            body=json.dumps(task_data)
        )
        
        assert create_response.code == 200
        created_task = json.loads(create_response.body)["data"]
        task_id = created_task["id"]
        
        # 更新任务
        update_data = {
            "title": "更新后的任务",
            "description": "更新后的描述",
            "priority": "high",
            "status": "active"
        }
        
        response = self.fetch(
            f"/api/v1/tasks/{task_id}",
            method="PUT",
            headers=self.headers,
            body=json.dumps(update_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["title"] == "更新后的任务"
        assert result["data"]["description"] == "更新后的描述"
        assert result["data"]["priority"] == "high"
        assert result["data"]["status"] == "active"
    
    def test_delete_task(self):
        """测试删除任务"""
        # 首先创建任务
        task_data = {
            "title": "待删除任务",
            "description": "这个任务将被删除",
            "task_type": "homework"
        }
        
        create_response = self.fetch(
            "/api/v1/tasks",
            method="POST",
            headers=self.headers,
            body=json.dumps(task_data)
        )
        
        assert create_response.code == 200
        created_task = json.loads(create_response.body)["data"]
        task_id = created_task["id"]
        
        # 删除任务
        response = self.fetch(
            f"/api/v1/tasks/{task_id}",
            method="DELETE",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["message"] == "Task deleted successfully"
        
        # 验证任务已被删除
        get_response = self.fetch(
            f"/api/v1/tasks/{task_id}",
            method="GET",
            headers=self.headers
        )
        
        assert get_response.code == 404
    
    def test_activate_task(self):
        """测试激活任务"""
        # 首先创建任务（默认是draft状态）
        task_data = {
            "title": "待激活任务",
            "description": "这个任务将被激活",
            "task_type": "homework"
        }
        
        create_response = self.fetch(
            "/api/v1/tasks",
            method="POST",
            headers=self.headers,
            body=json.dumps(task_data)
        )
        
        assert create_response.code == 200
        created_task = json.loads(create_response.body)["data"]
        task_id = created_task["id"]
        
        # 激活任务
        response = self.fetch(
            f"/api/v1/tasks/{task_id}/activate",
            method="PATCH",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["status"] == "active"


class TestTaskAssignmentAPI(AsyncHTTPTestCase):
    """测试任务分配API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户分配",
            code="test_tenant_assignment"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_assignment")
        self.db.commit()
        
        # 创建测试学员
        self.student = create_test_user(self.db, self.tenant.id, "test_student_assignment", "student_assignment@example.com")
        self.db.commit()
        
        # 创建测试任务
        from coding.database.models import Task
        self.task = Task(
            title="分配测试任务",
            description="用于测试分配的任务",
            task_type="homework",
            status="active",
            creator_id=self.user.id,
            tenant_id=self.tenant.id
        )
        self.db.add(self.task)
        self.db.commit()
        self.db.refresh(self.task)
        
        # 获取认证头
        self.headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_assign_task(self):
        """测试分配任务"""
        assignment_data = {
            "task_id": self.task.id,
            "student_id": self.student.id,
            "assignment_notes": "请认真完成此任务",
            "expected_completion_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        response = self.fetch(
            "/api/v1/task-assignments",
            method="POST",
            headers=self.headers,
            body=json.dumps(assignment_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["task_id"] == self.task.id
        assert result["data"]["student_id"] == self.student.id
        assert result["data"]["assigner_id"] == self.user.id
        assert result["data"]["status"] == "assigned"
        assert result["data"]["progress"] == 0.0
    
    def test_get_assignment(self):
        """测试获取任务分配"""
        # 首先创建分配
        from coding.database.models import TaskAssignment
        assignment = TaskAssignment(
            task_id=self.task.id,
            student_id=self.student.id,
            assigner_id=self.user.id,
            status="assigned",
            progress=0.0,
            tenant_id=self.tenant.id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # 获取分配
        response = self.fetch(
            f"/api/v1/task-assignments/{assignment.id}",
            method="GET",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["id"] == assignment.id
        assert result["data"]["task_id"] == self.task.id
        assert result["data"]["student_id"] == self.student.id
    
    def test_update_assignment(self):
        """测试更新任务分配"""
        # 首先创建分配
        from coding.database.models import TaskAssignment
        assignment = TaskAssignment(
            task_id=self.task.id,
            student_id=self.student.id,
            assigner_id=self.user.id,
            status="assigned",
            progress=0.0,
            tenant_id=self.tenant.id
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        
        # 更新分配
        update_data = {
            "status": "in_progress",
            "progress": 50.0,
            "student_notes": "已完成一半"
        }
        
        response = self.fetch(
            f"/api/v1/task-assignments/{assignment.id}",
            method="PUT",
            headers=self.headers,
            body=json.dumps(update_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["status"] == "in_progress"
        assert result["data"]["progress"] == 50.0
    
    def test_get_student_assignments(self):
        """测试获取学员的任务分配"""
        # 创建几个分配
        from coding.database.models import TaskAssignment
        for i in range(3):
            assignment = TaskAssignment(
                task_id=self.task.id,
                student_id=self.student.id,
                assigner_id=self.user.id,
                status="assigned",
                progress=i * 25.0,
                tenant_id=self.tenant.id
            )
            self.db.add(assignment)
        self.db.commit()
        
        # 获取学员的分配
        response = self.fetch(
            f"/api/v1/students/{self.student.id}/task-assignments",
            method="GET",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert "assignments" in result["data"]
        assert len(result["data"]["assignments"]) == 3
        assert result["data"]["student_id"] == self.student.id


class TestTaskSubmissionAPI(AsyncHTTPTestCase):
    """测试任务提交API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户提交",
            code="test_tenant_submission"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_submission")
        self.db.commit()
        
        # 创建测试学员
        self.student = create_test_user(self.db, self.tenant.id, "test_student_submission", "student_submission@example.com")
        self.db.commit()
        
        # 创建测试任务
        from coding.database.models import Task
        self.task = Task(
            title="提交测试任务",
            description="用于测试提交的任务",
            task_type="homework",
            status="active",
            creator_id=self.user.id,
            tenant_id=self.tenant.id
        )
        self.db.add(self.task)
        self.db.commit()
        self.db.refresh(self.task)
        
        # 创建测试分配
        from coding.database.models import TaskAssignment
        self.assignment = TaskAssignment(
            task_id=self.task.id,
            student_id=self.student.id,
            assigner_id=self.user.id,
            status="assigned",
            progress=0.0,
            tenant_id=self.tenant.id
        )
        self.db.add(self.assignment)
        self.db.commit()
        self.db.refresh(self.assignment)
        
        # 获取学员的认证头
        self.student_headers = get_auth_headers(self.student.id)
        self.user_headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_submit_task(self):
        """测试提交任务"""
        submission_data = {
            "assignment_id": self.assignment.id,
            "content": {
                "type": "text",
                "text": "这是我的作业提交内容"
            },
            "submission_notes": "请查收我的作业",
            "is_final": True
        }
        
        response = self.fetch(
            "/api/v1/task-submissions",
            method="POST",
            headers=self.student_headers,
            body=json.dumps(submission_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["assignment_id"] == self.assignment.id
        assert result["data"]["submitter_id"] == self.student.id
        assert result["data"]["status"] == "submitted"
        assert result["data"]["content"]["type"] == "text"
        assert result["data"]["is_final"] is True
    
    def test_review_submission(self):
        """测试审核任务提交"""
        # 首先创建提交
        from coding.database.models import TaskSubmission
        submission = TaskSubmission(
            assignment_id=self.assignment.id,
            submitter_id=self.student.id,
            status="submitted",
            content={"type": "text", "text": "作业内容"},
            version=1,
            tenant_id=self.tenant.id
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        # 审核提交
        review_data = {
            "status": "accepted",
            "review_notes": "作业完成得很好"
        }
        
        response = self.fetch(
            f"/api/v1/task-submissions/{submission.id}/review",
            method="PATCH",
            headers=self.user_headers,
            body=json.dumps(review_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["status"] == "accepted"
        assert result["data"]["reviewer_id"] == self.user.id
        assert result["data"]["review_notes"] == "作业完成得很好"


class TestTaskEvaluationAPI(AsyncHTTPTestCase):
    """测试任务评价API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户评价",
            code="test_tenant_evaluation"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_evaluation")
        self.db.commit()
        
        # 创建测试学员
        self.student = create_test_user(self.db, self.tenant.id, "test_student_evaluation", "student_evaluation@example.com")
        self.db.commit()
        
        # 创建测试任务
        from coding.database.models import Task
        self.task = Task(
            title="评价测试任务",
            description="用于测试评价的任务",
            task_type="homework",
            status="active",
            creator_id=self.user.id,
            tenant_id=self.tenant.id
        )
        self.db.add(self.task)
        self.db.commit()
        self.db.refresh(self.task)
        
        # 创建测试分配
        from coding.database.models import TaskAssignment
        self.assignment = TaskAssignment(
            task_id=self.task.id,
            student_id=self.student.id,
            assigner_id=self.user.id,
            status="completed",
            progress=100.0,
            tenant_id=self.tenant.id
        )
        self.db.add(self.assignment)
        self.db.commit()
        self.db.refresh(self.assignment)
        
        # 获取认证头
        self.headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_create_evaluation(self):
        """测试创建任务评价"""
        evaluation_data = {
            "assignment_id": self.assignment.id,
            "overall_score": 85.5,
            "score_details": {
                "完成度": 90.0,
                "准确性": 85.0,
                "创新性": 80.0,
                "规范性": 87.0
            },
            "comments": "作业完成得很好，但可以更有创意",
            "strengths": "基础扎实，逻辑清晰",
            "areas_for_improvement": "需要更多创新思维",
            "improvement_suggestions": "多阅读相关文献，拓宽思路",
            "next_goals": "完成下一章的练习",
            "recommended_for_advancement": True
        }
        
        response = self.fetch(
            "/api/v1/task-evaluations",
            method="POST",
            headers=self.headers,
            body=json.dumps(evaluation_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["assignment_id"] == self.assignment.id
        assert result["data"]["evaluator_id"] == self.user.id
        assert result["data"]["student_id"] == self.student.id
        assert result["data"]["overall_score"] == 85.5
        assert result["data"]["score_grade"] == "B+"
        assert result["data"]["comments"] == "作业完成得很好，但可以更有创意"
        assert result["data"]["recommended_for_advancement"] is True
    
    def test_publish_evaluation(self):
        """测试发布任务评价"""
        # 首先创建评价
        from coding.database.models import TaskEvaluation
        evaluation = TaskEvaluation(
            assignment_id=self.assignment.id,
            evaluator_id=self.user.id,
            student_id=self.student.id,
            overall_score=90.0,
            comments="优秀作业",
            status="draft",
            tenant_id=self.tenant.id
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        
        # 发布评价
        response = self.fetch(
            f"/api/v1/task-evaluations/{evaluation.id}/publish",
            method="PATCH",
            headers=self.headers
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert result["data"]["status"] == "published"


class TestTaskSchedulerAPI(AsyncHTTPTestCase):
    """测试任务调度API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户调度",
            code="test_tenant_scheduler"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_scheduler")
        self.db.commit()
        
        # 创建测试学员
        self.student = create_test_user(self.db, self.tenant.id, "test_student_scheduler", "student_scheduler@example.com")
        self.db.commit()
        
        # 创建几个测试任务
        from coding.database.models import Task
        from datetime import datetime, timedelta
        
        for i in range(5):
            task = Task(
                title=f"调度测试任务{i+1}",
                description=f"用于调度测试的任务{i+1}",
                task_type="homework",
                status="active",
                priority=["low", "medium", "high", "urgent", "medium"][i],
                difficulty=["beginner", "beginner", "intermediate", "intermediate", "advanced"][i],
                creator_id=self.user.id,
                tenant_id=self.tenant.id,
                start_time=datetime.utcnow(),
                deadline=datetime.utcnow() + timedelta(days=[7, 5, 3, 2, 1][i])
            )
            self.db.add(task)
        self.db.commit()
        
        # 获取认证头
        self.headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_schedule_tasks(self):
        """测试智能调度任务"""
        scheduler_data = {
            "student_id": self.student.id,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "max_tasks_per_day": 3,
            "consider_difficulty": True,
            "consider_priority": True,
            "consider_dependencies": True
        }
        
        response = self.fetch(
            "/api/v1/task-scheduler/schedule",
            method="POST",
            headers=self.headers,
            body=json.dumps(scheduler_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert "schedule" in result["data"]
        assert result["data"]["student_id"] == self.student.id
        assert len(result["data"]["schedule"]) > 0


class TestTaskAnalyticsAPI(AsyncHTTPTestCase):
    """测试任务分析API"""
    
    def get_app(self) -> Application:
        """获取测试应用"""
        return create_app()
    
    def setUp(self):
        """测试前设置"""
        super().setUp()
        
        # 创建测试数据
        self.db = get_db_session()
        
        # 创建测试租户
        self.tenant = Tenant(
            name="测试租户分析",
            code="test_tenant_analytics"
        )
        self.db.add(self.tenant)
        self.db.commit()
        self.db.refresh(self.tenant)
        
        # 创建测试用户
        self.user = create_test_user(self.db, self.tenant.id, "test_user_analytics")
        self.db.commit()
        
        # 创建测试数据
        from coding.database.models import Task, TaskAssignment, TaskEvaluation
        from datetime import datetime, timedelta
        
        # 创建一些任务
        for i in range(10):
            task = Task(
                title=f"分析测试任务{i+1}",
                description=f"用于分析测试的任务{i+1}",
                task_type=["homework", "exercise", "custom"][i % 3],
                status="active",
                priority=["low", "medium", "high"][i % 3],
                difficulty=["beginner", "intermediate", "advanced"][i % 3],
                creator_id=self.user.id,
                tenant_id=self.tenant.id,
                created_at=datetime.utcnow() - timedelta(days=30 - i*3)
            )
            self.db.add(task)
        self.db.commit()
        
        # 获取认证头
        self.headers = get_auth_headers(self.user.id)
    
    def tearDown(self):
        """测试后清理"""
        # 清理数据库
        self.db.rollback()
        self.db.close()
        super().tearDown()
    
    def test_get_task_analytics(self):
        """测试获取任务分析数据"""
        analytics_data = {
            "start_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "group_by": "task_type"
        }
        
        response = self.fetch(
            "/api/v1/task-analytics",
            method="POST",
            headers=self.headers,
            body=json.dumps(analytics_data)
        )
        
        assert response.code == 200
        result = json.loads(response.body)
        
        assert result["success"] is True
        assert "summary" in result["data"]
        assert "distributions" in result["data"]
        assert "trends" in result["data"]
        assert "grouped_data" in result["data"]
        
        # 验证分析数据的基本结构
        summary = result["data"]["summary"]
        assert "total_tasks" in summary
        assert "completion_rate" in summary
        assert "average_score" in summary
        
        distributions = result["data"]["distributions"]
        assert "difficulty" in distributions
        assert "priority" in distributions
        assert "task_type" in distributions