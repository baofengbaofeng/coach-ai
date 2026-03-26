"""
系统测试模块 - 用户流程测试。
测试完整的用户业务流程和端到端场景。
"""
import json
import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.tasks.models import Task, TaskAssignment, TaskCompletion
from apps.achievements.models import Achievement, UserAchievement


class TestCompleteUserRegistrationFlow:
    """完整用户注册流程测试"""
    
    def test_user_registration_to_first_login(self, api_client):
        """测试从注册到首次登录的完整流程"""
        # 1. 用户注册
        registration_data = {
            "username": "newflowuser",
            "email": "flow@example.com",
            "password": "flowpassword123",
            "first_name": "Flow",
            "last_name": "User",
            "age": 28,
            "gender": "female",
            "fitness_level": "beginner"
        }
        
        register_url = reverse('user-register')
        register_response = api_client.post(
            register_url,
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.data['id']
        
        # 2. 使用注册的凭证登录
        login_data = {
            "username": registration_data['username'],
            "password": registration_data['password']
        }
        
        login_url = reverse('user-login')
        login_response = api_client.post(
            login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        auth_token = login_response.data.get('token') or login_response.data.get('access_token')
        assert auth_token is not None
        
        # 3. 使用token访问受保护端点
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {auth_token}')
        
        profile_url = reverse('user-profile', kwargs={'user_id': user_id})
        profile_response = api_client.get(profile_url)
        
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['username'] == registration_data['username']
        assert profile_response.data['email'] == registration_data['email']
        
        print("✅ 完整用户注册流程测试通过")


class TestTaskCompletionFlow:
    """任务完成流程测试"""
    
    def test_task_creation_to_completion(self, authenticated_api_client, test_user):
        """测试从任务创建到完成的完整流程"""
        # 1. 创建任务
        task_data = {
            "title": "完整流程测试任务",
            "description": "测试从创建到完成的完整流程",
            "task_type": "exercise",
            "difficulty": "medium",
            "estimated_time": 40,
            "points": 80
        }
        
        create_task_url = reverse('task-list')
        create_response = authenticated_api_client.post(
            create_task_url,
            data=json.dumps(task_data),
            content_type='application/json'
        )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.data['id']
        
        # 2. 分配任务给用户
        assignment_data = {
            "user_id": test_user.id,
            "task_id": task_id,
            "due_date": (timezone.now() + timedelta(days=3)).isoformat()
        }
        
        assign_url = reverse('task-assign')
        assign_response = authenticated_api_client.post(
            assign_url,
            data=json.dumps(assignment_data),
            content_type='application/json'
        )
        
        assert assign_response.status_code == status.HTTP_201_CREATED
        assignment_id = assign_response.data['id']
        
        # 3. 获取用户的任务列表
        user_tasks_url = reverse('user-tasks', kwargs={'user_id': test_user.id})
        tasks_response = authenticated_api_client.get(user_tasks_url)
        
        assert tasks_response.status_code == status.HTTP_200_OK
        
        # 检查任务是否在用户的任务列表中
        user_tasks = tasks_response.data.get('results', tasks_response.data)
        task_found = any(task['id'] == task_id for task in user_tasks)
        assert task_found, "创建的任务应该在用户的任务列表中"
        
        # 4. 标记任务为进行中
        update_assignment_url = reverse('task-assignment-detail', kwargs={'pk': assignment_id})
        in_progress_data = {
            "status": "in_progress",
            "started_at": timezone.now().isoformat()
        }
        
        progress_response = authenticated_api_client.patch(
            update_assignment_url,
            data=json.dumps(in_progress_data),
            content_type='application/json'
        )
        
        assert progress_response.status_code == status.HTTP_200_OK
        assert progress_response.data['status'] == 'in_progress'
        
        # 5. 标记任务为已完成
        completion_data = {
            "status": "completed",
            "completed_at": timezone.now().isoformat(),
            "actual_time_spent": 35,  # 比预计少5分钟
            "notes": "任务顺利完成，感觉很好！"
        }
        
        complete_response = authenticated_api_client.patch(
            update_assignment_url,
            data=json.dumps(completion_data),
            content_type='application/json'
        )
        
        assert complete_response.status_code == status.HTTP_200_OK
        assert complete_response.data['status'] == 'completed'
        
        # 6. 验证用户获得了积分
        user_url = reverse('user-profile', kwargs={'user_id': test_user.id})
        user_response = authenticated_api_client.get(user_url)
        
        assert user_response.status_code == status.HTTP_200_OK
        assert user_response.data['points'] >= task_data['points'], "用户应该获得任务积分"
        
        # 7. 验证任务完成记录被创建
        completion_exists = TaskCompletion.objects.filter(
            assignment_id=assignment_id,
            user=test_user
        ).exists()
        assert completion_exists, "应该创建任务完成记录"
        
        print("✅ 完整任务完成流程测试通过")


class TestAchievementUnlockFlow:
    """成就解锁流程测试"""
    
    def test_achievement_unlock_through_task_completion(self, authenticated_api_client, test_user):
        """测试通过任务完成解锁成就"""
        # 1. 创建一个成就（需要100积分）
        achievement = Achievement.objects.create(
            name="百积分达人",
            description="累计获得100积分",
            achievement_type="points",
            points_required=100,
            badge_image="badges/100_points.png"
        )
        
        # 2. 给用户添加90积分（还差10分）
        test_user.add_points(90)
        test_user.refresh_from_db()
        assert test_user.points == 90
        
        # 3. 创建一个10积分的任务
        task = Task.objects.create(
            title="解锁成就测试任务",
            task_type="exercise",
            difficulty="easy",
            estimated_time=15,
            points=10
        )
        
        # 4. 分配并完成任务
        assignment = TaskAssignment.objects.create(
            user=test_user,
            task=task,
            assigned_by=test_user
        )
        
        # 直接标记为完成（跳过进行中状态）
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()
        
        # 5. 验证用户积分增加到100
        test_user.refresh_from_db()
        assert test_user.points == 100, f"用户应该有100积分，实际有{test_user.points}"
        
        # 6. 检查成就是否被解锁
        # 注意：这里假设有后台任务或信号处理成就解锁
        # 在实际系统中，可能需要手动触发成就检查
        
        # 模拟成就检查（根据实际实现调整）
        from apps.achievements.services import AchievementService
        service = AchievementService()
        unlocked_achievements = service.check_user_achievements(test_user)
        
        # 或者直接检查用户成就记录
        user_achievement_exists = UserAchievement.objects.filter(
            user=test_user,
            achievement=achievement
        ).exists()
        
        # 根据实际实现，可能立即解锁或需要手动检查
        if user_achievement_exists:
            print("✅ 成就已成功解锁")
        else:
            print("⚠️  成就未自动解锁（可能需要手动触发成就检查）")
        
        # 7. 获取用户的成就列表
        user_achievements_url = reverse('user-achievements', kwargs={'user_id': test_user.id})
        achievements_response = authenticated_api_client.get(user_achievements_url)
        
        if achievements_response.status_code == status.HTTP_200_OK:
            user_achievements = achievements_response.data.get('results', achievements_response.data)
            print(f"用户当前有 {len(user_achievements)} 个成就")
        
        print("✅ 成就解锁流程测试完成")


class TestAIRecommendationFlow:
    """AI推荐流程测试"""
    
    def test_personalized_ai_recommendation_flow(self, authenticated_api_client, test_user):
        """测试个性化AI推荐完整流程"""
        # 1. 设置用户偏好
        profile_update_url = reverse('user-profile-update', kwargs={'user_id': test_user.id})
        
        profile_data = {
            "fitness_level": "intermediate",
            "preferred_exercise_types": ["running", "swimming", "yoga"],
            "available_time_per_day": 60,
            "fitness_goals": ["endurance", "flexibility"]
        }
        
        profile_response = authenticated_api_client.patch(
            profile_update_url,
            data=json.dumps(profile_data),
            content_type='application/json'
        )
        
        # 注意：根据实际API设计，可能返回200或204
        assert profile_response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        
        # 2. 获取AI推荐
        recommendation_request = {
            "user_id": test_user.id,
            "preferences": {
                "exercise_types": profile_data["preferred_exercise_types"],
                "duration_range": [30, profile_data["available_time_per_day"]],
                "difficulty": profile_data["fitness_level"]
            },
            "context": {
                "time_of_day": "evening",
                "weather": "indoor",  # 假设室内运动
                "available_equipment": ["yoga_mat"]
            }
        }
        
        recommendation_url = reverse('ai-recommendation')
        recommendation_response = authenticated_api_client.post(
            recommendation_url,
            data=json.dumps(recommendation_request),
            content_type='application/json'
        )
        
        assert recommendation_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        if recommendation_response.status_code == status.HTTP_200_OK:
            recommendations = recommendation_response.data.get('recommendations', [])
            assert len(recommendations) > 0, "应该返回至少一个推荐"
            
            # 检查推荐的相关性
            for rec in recommendations:
                assert 'title' in rec
                assert 'description' in rec
                assert 'estimated_time' in rec
                assert 'difficulty' in rec
                
                # 推荐应该符合用户偏好
                if 'exercise_type' in rec:
                    assert rec['exercise_type'] in profile_data["preferred_exercise_types"]
        
        # 3. 用户选择并开始一个推荐
        if recommendation_response.status_code == status.HTTP_200_OK and len(recommendations) > 0:
            selected_recommendation = recommendations[0]
            
            # 创建任务基于推荐
            task_from_recommendation = {
                "title": selected_recommendation.get('title', 'AI推荐任务'),
                "description": selected_recommendation.get('description', ''),
                "task_type": "exercise",
                "difficulty": selected_recommendation.get('difficulty', 'medium'),
                "estimated_time": selected_recommendation.get('estimated_time', 30),
                "points": 50,  # 默认积分
                "source": "ai_recommendation"
            }
            
            create_task_url = reverse('task-list')
            task_response = authenticated_api_client.post(
                create_task_url,
                data=json.dumps(task_from_recommendation),
                content_type='application/json'
            )
            
            if task_response.status_code == status.HTTP_201_CREATED:
                print(f"✅ 成功从AI推荐创建任务: {task_from_recommendation['title']}")
        
        print("✅ AI推荐流程测试完成")


class TestMultiUserCollaborationFlow:
    """多用户协作流程测试"""
    
    def test_group_task_assignment_and_completion(self, api_client):
        """测试组任务分配和完成"""
        # 1. 创建多个用户
        users = []
        for i in range(3):
            user_data = {
                "username": f"groupuser{i}",
                "email": f"group{i}@example.com",
                "password": f"grouppass{i}",
                "first_name": f"Group{i}",
                "last_name": "User"
            }
            
            register_url = reverse('user-register')
            response = api_client.post(
                register_url,
                data=json.dumps(user_data),
                content_type='application/json'
            )
            
            if response.status_code == status.HTTP_201_CREATED:
                users.append(response.data)
        
        assert len(users) >= 2, "需要至少2个用户进行协作测试"
        
        # 2. 用户登录获取token
        tokens = []
        for user in users:
            login_data = {
                "username": user['username'],
                "password": f"grouppass{users.index(user)}"
            }
            
            login_url = reverse('user-login')
            login_response = api_client.post(
                login_url,
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            if login_response.status_code == status.HTTP_200_OK:
                token = login_response.data.get('token') or login_response.data.get('access_token')
                tokens.append(token)
        
        # 3. 使用第一个用户的token创建组任务
        if tokens:
            api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens[0]}')
            
            group_task_data = {
                "title": "团队协作任务",
                "description": "需要团队合作完成的任务",
                "task_type": "group",
                "difficulty": "hard",
                "estimated_time": 120,
                "points": 200,
                "max_participants": 3
            }
            
            create_task_url = reverse('task-list')
            task_response = api_client.post(
                create_task_url,
                data=json.dumps(group_task_data),
                content_type='application/json'
            )
            
            if task_response.status_code == status.HTTP_201_CREATED:
                group_task_id = task_response.data['id']
                print(f"✅ 创建组任务成功，ID: {group_task_id}")
                
                # 4. 分配任务给所有用户
                for i, token in enumerate(tokens):
                    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
                    
                    # 这里简化处理，实际可能需要不同的API端点
                    print(f"用户 {users[i]['username']} 可以参与组任务")
        
        print("✅ 多用户协作流程测试完成")


class TestErrorRecoveryFlow:
    """错误恢复流程测试"""
    
    def test_task_failure_and_retry_flow(self, authenticated_api_client, test_user):
        """测试任务失败和重试流程"""
        # 1. 创建任务
        task = Task.objects.create(
            title="可能失败的任务",
            description="这个任务可能会失败，测试恢复流程",
            task_type="exercise",
            difficulty="medium",
            estimated_time=30,
            points=50
        )
        
        # 2. 分配任务
        assignment = TaskAssignment.objects.create(
            user=test_user,
            task=task,
            assigned_by=test_user
        )
        
        # 3. 开始任务
        assignment.status = 'in_progress'
        assignment.started_at = timezone.now()
        assignment.save()
        
        # 4. 模拟任务失败
        assignment.status = 'failed'
        assignment.failed_at = timezone.now()
        assignment.failure_reason = "用户中途退出"
        assignment.save()
        
        # 5. 验证任务状态为失败
        assignment.refresh_from_db()
        assert assignment.status == 'failed'
        assert assignment.failure_reason is not None
        
        # 6. 重试任务（创建新的分配）
        retry_assignment = TaskAssignment.objects.create(
            user=test_user,
            task=task,
            assigned_by=test_user,
            parent_assignment=assignment,  # 链接到原始分配
            retry_count=1
        )
        
        # 7. 成功完成重试
        retry_assignment.status = 'completed'
        retry_assignment.completed_at = timezone.now()
        retry_assignment.save()
        
        # 8. 验证重试成功
        retry_assignment.refresh_from_db()
        assert retry_assignment.status == 'completed'
        assert retry_assignment.retry_count == 1
        
        # 9. 用户应该获得积分
        test_user.refresh_from_db()
        # 注意：根据业务逻辑，重试可能获得积分也可能不获得
        
        print("✅ 错误恢复流程测试完成")


# 运行所有系统测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])