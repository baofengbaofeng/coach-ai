#!/usr/bin/env python3
"""
成就系统使用示例

展示如何使用成就系统的API接口
"""

import json
import requests
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8888/api/v1"


def print_response(response, description):
    """打印API响应"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"错误: {response.text}")
    print(f"{'='*60}")


def example_achievement_management():
    """示例：成就管理"""
    print("\n1. 成就管理示例")
    
    # 1.1 获取成就列表
    response = requests.get(f"{BASE_URL}/achievements")
    print_response(response, "获取成就列表")
    
    # 1.2 创建新成就
    achievement_data = {
        "name": "俯卧撑新手",
        "description": "完成10次俯卧撑",
        "achievement_type": "exercise",
        "difficulty": "easy",
        "trigger_type": "exercise_completed",
        "trigger_config": {
            "exercise_type": "pushup",
            "min_count": 10
        },
        "target_value": 10,
        "reward_points": 100,
        "category": "力量训练",
        "tags": ["俯卧撑", "新手", "力量"]
    }
    
    response = requests.post(
        f"{BASE_URL}/achievements",
        json=achievement_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "创建成就")
    
    if response.status_code == 201:
        achievement_id = response.json()["data"]["achievement"]["id"]
        
        # 1.3 获取成就详情
        response = requests.get(f"{BASE_URL}/achievements/{achievement_id}")
        print_response(response, "获取成就详情")
        
        # 1.4 更新成就
        update_data = {
            "reward_points": 150,
            "description": "完成10次标准俯卧撑"
        }
        
        response = requests.put(
            f"{BASE_URL}/achievements/{achievement_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "更新成就")
    
    return achievement_id if 'achievement_id' in locals() else None


def example_user_achievement_progress():
    """示例：用户成就进度"""
    print("\n2. 用户成就进度示例")
    
    # 假设的用户ID和成就ID
    user_id = "test_user_123"
    achievement_id = "test_achievement_456"
    
    # 2.1 更新成就进度
    progress_data = {
        "user_id": user_id,
        "achievement_id": achievement_id,
        "progress_delta": 3,
        "event_type": "exercise_completed",
        "event_data": {
            "exercise_type": "pushup",
            "count": 3,
            "duration": 300,
            "calories": 50
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-progress",
        json=progress_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "更新成就进度")
    
    # 2.2 获取用户成就列表
    response = requests.get(f"{BASE_URL}/users/{user_id}/achievements")
    print_response(response, "获取用户成就列表")
    
    # 2.3 获取用户成就统计
    response = requests.get(f"{BASE_URL}/users/{user_id}/achievement-stats")
    print_response(response, "获取用户成就统计")


def example_achievement_trigger():
    """示例：成就触发"""
    print("\n3. 成就触发示例")
    
    user_id = "test_user_123"
    
    # 3.1 触发运动完成事件
    event_data = {
        "event_type": "exercise_completed",
        "user_id": user_id,
        "event_data": {
            "exercise_type": "pushup",
            "count": 15,
            "duration": 450,
            "calories": 75,
            "equipment": ["mat"],
            "location": "home",
            "time_of_day": "morning"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-trigger",
        json=event_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "触发成就事件")


def example_badge_system():
    """示例：徽章系统"""
    print("\n4. 徽章系统示例")
    
    user_id = "test_user_123"
    
    # 4.1 创建徽章
    badge_data = {
        "name": "力量训练者",
        "description": "完成100次力量训练",
        "icon_url": "/badges/strength_trainer.png",
        "badge_type": "achievement",
        "rarity": "uncommon",
        "grant_condition": "完成100次力量训练",
        "category": "训练",
        "tags": ["力量", "训练", "成就"]
    }
    
    response = requests.post(
        f"{BASE_URL}/badges",
        json=badge_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "创建徽章")
    
    if response.status_code == 201:
        badge_id = response.json()["data"]["badge"]["id"]
        
        # 4.2 授予徽章给用户
        grant_data = {
            "user_id": user_id,
            "badge_id": badge_id,
            "grant_reason": "完成力量训练成就",
            "granted_by": "system"
        }
        
        response = requests.post(
            f"{BASE_URL}/badge-grant",
            json=grant_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "授予徽章")
        
        # 4.3 获取用户徽章列表
        response = requests.get(f"{BASE_URL}/users/{user_id}/badges")
        print_response(response, "获取用户徽章列表")


def example_reward_system():
    """示例：奖励系统"""
    print("\n5. 奖励系统示例")
    
    user_id = "test_user_123"
    
    # 5.1 创建奖励
    reward_data = {
        "name": "新手大礼包",
        "description": "新用户专属奖励",
        "icon_url": "/rewards/newbie_package.png",
        "reward_type": "points",
        "reward_config": {
            "points": 500,
            "items": ["训练计划模板", "营养指南"]
        },
        "value": 500,
        "grant_condition": "新用户注册",
        "is_auto_grant": True,
        "max_claims": 1000,
        "per_user_limit": 1,
        "available_from": datetime.now().isoformat(),
        "available_until": (datetime.now().replace(year=datetime.now().year + 1)).isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/rewards",
        json=reward_data,
        headers={"Content-Type": "application/json"}
    )
    print_response(response, "创建奖励")
    
    if response.status_code == 201:
        reward_id = response.json()["data"]["reward"]["id"]
        
        # 5.2 用户领取奖励
        claim_data = {
            "user_id": user_id,
            "reward_id": reward_id,
            "claim_reason": "新用户注册"
        }
        
        response = requests.post(
            f"{BASE_URL}/reward-claim",
            json=claim_data,
            headers={"Content-Type": "application/json"}
        )
        print_response(response, "领取奖励")
        
        # 5.3 获取用户奖励记录
        response = requests.get(f"{BASE_URL}/users/{user_id}/rewards")
        print_response(response, "获取用户奖励记录")


def example_comprehensive_scenario():
    """示例：综合场景 - 用户完成运动训练"""
    print("\n6. 综合场景示例 - 用户完成运动训练")
    
    user_id = "athlete_001"
    
    print(f"\n场景：用户 {user_id} 完成一次完整的运动训练")
    
    # 6.1 用户开始训练
    print("\n步骤1: 用户开始训练")
    training_data = {
        "user_id": user_id,
        "training_type": "strength",
        "exercises": [
            {"type": "pushup", "target": 20},
            {"type": "squat", "target": 30},
            {"type": "plank", "target": 60}
        ],
        "start_time": datetime.now().isoformat()
    }
    print(f"训练数据: {json.dumps(training_data, indent=2, ensure_ascii=False)}")
    
    # 6.2 用户完成俯卧撑
    print("\n步骤2: 用户完成俯卧撑")
    pushup_event = {
        "event_type": "exercise_completed",
        "user_id": user_id,
        "event_data": {
            "exercise_type": "pushup",
            "count": 20,
            "duration": 300,
            "calories": 100,
            "form_rating": 4.5,
            "difficulty": "medium"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-trigger",
        json=pushup_event,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        notifications = response.json()["data"]["notifications"]
        if notifications:
            print("触发成就解锁:")
            for notification in notifications:
                achievement = notification["achievement"]
                print(f"  - {achievement['name']}: {achievement['description']}")
    
    # 6.3 用户完成深蹲
    print("\n步骤3: 用户完成深蹲")
    squat_event = {
        "event_type": "exercise_completed",
        "user_id": user_id,
        "event_data": {
            "exercise_type": "squat",
            "count": 30,
            "duration": 450,
            "calories": 150,
            "form_rating": 4.0,
            "difficulty": "medium"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-trigger",
        json=squat_event,
        headers={"Content-Type": "application/json"}
    )
    
    # 6.4 用户完成平板支撑
    print("\n步骤4: 用户完成平板支撑")
    plank_event = {
        "event_type": "exercise_completed",
        "user_id": user_id,
        "event_data": {
            "exercise_type": "plank",
            "count": 1,
            "duration": 60,
            "calories": 50,
            "form_rating": 4.8,
            "difficulty": "hard"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-trigger",
        json=plank_event,
        headers={"Content-Type": "application/json"}
    )
    
    # 6.5 训练完成，触发综合成就
    print("\n步骤5: 训练完成，检查综合成就")
    training_complete_event = {
        "event_type": "training_completed",
        "user_id": user_id,
        "event_data": {
            "training_type": "strength",
            "total_exercises": 3,
            "total_duration": 810,
            "total_calories": 300,
            "average_form_rating": 4.43,
            "completion_time": datetime.now().isoformat()
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/achievement-trigger",
        json=training_complete_event,
        headers={"Content-Type": "application/json"}
    )
    
    # 6.6 获取用户成就统计
    print("\n步骤6: 查看用户成就统计")
    response = requests.get(f"{BASE_URL}/users/{user_id}/achievement-stats")
    
    if response.status_code == 200:
        stats = response.json()["data"]["stats"]
        print(f"总成就数: {stats['total_achievements']}")
        print(f"已解锁成就: {stats['unlocked_achievements']}")
        print(f"进行中成就: {stats['in_progress_achievements']}")
        print(f"总积分: {stats['total_points']}")
        print(f"总徽章数: {stats['total_badges']}")
        print(f"完成率: {stats['completion_rate']:.1f}%")
    
    # 6.7 获取用户徽章
    print("\n步骤7: 查看用户徽章")
    response = requests.get(f"{BASE_URL}/users/{user_id}/badges")
    
    if response.status_code == 200:
        badges = response.json()["data"]["user_badges"]
        if badges:
            print("用户拥有的徽章:")
            for badge in badges[:5]:  # 显示前5个徽章
                badge_info = badge.get("badge", {})
                print(f"  - {badge_info.get('name', '未知徽章')} ({badge_info.get('rarity', 'common')})")


def main():
    """主函数"""
    print("CoachAI 成就系统使用示例")
    print("=" * 60)
    
    try:
        # 测试API连接
        response = requests.get(f"{BASE_URL}/achievements")
        if response.status_code != 200:
            print(f"警告: 无法连接到API服务器 ({BASE_URL})")
            print("请确保服务器正在运行，或修改BASE_URL配置")
            return
        
        # 运行示例
        example_achievement_management()
        example_user_achievement_progress()
        example_achievement_trigger()
        example_badge_system()
        example_reward_system()
        example_comprehensive_scenario()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print(f"\n错误: 无法连接到API服务器 ({BASE_URL})")
        print("请确保:")
        print("1. CoachAI服务器正在运行")
        print("2. 端口8888未被占用")
        print("3. 防火墙设置允许连接")
    except Exception as e:
        print(f"\n错误: {str(e)}")


if __name__ == "__main__":
    main()