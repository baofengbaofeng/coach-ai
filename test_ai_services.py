#!/usr/bin/env python
"""
测试AI服务层基本功能
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from services.manager import get_ai_service_manager, initialize_ai_services, cleanup_ai_services

User = get_user_model()

print("测试AI服务层基本功能...")
print("=" * 50)

# 1. 获取AI服务管理器
print("1. 获取AI服务管理器:")
print("-" * 30)

try:
    manager = get_ai_service_manager()
    print(f"✅ AI服务管理器获取成功: {manager.__class__.__name__}")
except Exception as e:
    print(f"❌ 获取AI服务管理器失败: {e}")
    sys.exit(1)

# 2. 初始化AI服务
print("\n2. 初始化AI服务:")
print("-" * 30)

try:
    success = initialize_ai_services()
    if success:
        print("✅ AI服务初始化成功")
    else:
        print("❌ AI服务初始化失败")
        sys.exit(1)
except Exception as e:
    print(f"❌ AI服务初始化异常: {e}")
    sys.exit(1)

# 3. 获取服务状态
print("\n3. 获取服务状态:")
print("-" * 30)

try:
    status = manager.get_service_status()
    print(f"✅ 服务状态获取成功")
    print(f"   初始化状态: {status.get('initialized', False)}")
    print(f"   总服务数: {status.get('total_services', 0)}")
    print(f"   服务类型: {list(status.get('services', {}).keys())}")
    print(f"   管理器: {list(status.get('managers', {}).keys())}")
except Exception as e:
    print(f"❌ 获取服务状态失败: {e}")

# 4. 测试推荐服务
print("\n4. 测试推荐服务:")
print("-" * 30)

try:
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username="ai_test_user",
        defaults={
            "email": "ai_test@example.com",
            "password": "test123",
        }
    )
    
    print(f"✅ 测试用户: {user.username} (ID: {user.id})")
    
    # 获取推荐结果
    result = manager.process_recommendation(user, type="all", max_recommendations=5)
    
    if result.get("success"):
        print(f"✅ 推荐服务测试成功")
        print(f"   用户: {result.get('username')}")
        print(f"   推荐类型: {result.get('recommendation_type')}")
        print(f"   推荐数量: {result.get('total_count', 0)}")
        
        recommendations = result.get("recommendations", [])
        if recommendations:
            print(f"   示例推荐:")
            for i, rec in enumerate(recommendations[:2], 1):
                print(f"     {i}. {rec.get('type')} - {rec.get('reason', '')[:50]}...")
    else:
        print(f"❌ 推荐服务测试失败: {result.get('error', {}).get('message', '未知错误')}")
        
except Exception as e:
    print(f"❌ 推荐服务测试异常: {e}")

# 5. 测试分析服务
print("\n5. 测试分析服务:")
print("-" * 30)

try:
    result = manager.process_analysis(user, type="comprehensive", period_days=30)
    
    if result.get("success"):
        print(f"✅ 分析服务测试成功")
        print(f"   分析类型: {result.get('analysis_type')}")
        print(f"   分析周期: {result.get('analysis_period')}天")
        
        data = result.get("data", {})
        if data:
            summary = data.get("summary", {})
            if summary:
                print(f"   分析摘要:")
                print(f"     总体分数: {summary.get('overall_score', 0)}")
                print(f"     优势: {', '.join(summary.get('strengths', [])[:2])}")
                print(f"     改进领域: {', '.join(summary.get('areas_for_improvement', [])[:2])}")
            
            insights = data.get("insights", [])
            if insights:
                print(f"   关键洞察 ({len(insights)}个):")
                for i, insight in enumerate(insights[:2], 1):
                    print(f"     {i}. {insight.get('title')}")
    else:
        print(f"❌ 分析服务测试失败: {result.get('error', {}).get('message', '未知错误')}")
        
except Exception as e:
    print(f"❌ 分析服务测试异常: {e}")

# 6. 测试预测服务
print("\n6. 测试预测服务:")
print("-" * 30)

try:
    result = manager.process_prediction(user, type="all", horizon_days=7)
    
    if result.get("success"):
        print(f"✅ 预测服务测试成功")
        print(f"   预测类型: {result.get('prediction_type')}")
        print(f"   预测周期: {result.get('prediction_horizon')}天")
        
        predictions = result.get("predictions", {})
        if predictions:
            summary = predictions.get("summary", {})
            if summary:
                print(f"   预测摘要:")
                print(f"     总体置信度: {summary.get('overall_confidence', 0)}")
                print(f"     高置信度预测: {summary.get('high_confidence_predictions', 0)}/{summary.get('total_predictions', 0)}")
                
                takeaways = summary.get("key_takeaways", [])
                if takeaways:
                    print(f"     关键要点:")
                    for i, takeaway in enumerate(takeaways[:2], 1):
                        print(f"     {i}. {takeaway}")
    else:
        print(f"❌ 预测服务测试失败: {result.get('error', {}).get('message', '未知错误')}")
        
except Exception as e:
    print(f"❌ 预测服务测试异常: {e}")

# 7. 清理测试数据
print("\n7. 清理测试数据:")
print("-" * 30)

try:
    # 删除测试用户
    if 'user' in locals():
        user.delete()
        print(f"✅ 测试用户已删除")
    
    # 清理AI服务
    cleanup_ai_services()
    print(f"✅ AI服务已清理")
    
except Exception as e:
    print(f"❌ 清理测试数据失败: {e}")

print("\n" + "=" * 50)
print("AI服务层基本功能测试完成!")
print("如果所有步骤都显示✅，说明AI服务层基本功能正常。")

# 8. 性能测试（可选）
print("\n8. 性能测试（简单计时）:")
print("-" * 30)

import time

try:
    # 重新初始化服务
    manager = get_ai_service_manager()
    manager.initialize()
    
    # 测试推荐服务性能
    start_time = time.time()
    result = manager.process_recommendation(1, type="all", max_recommendations=3)
    end_time = time.time()
    
    if result.get("success"):
        print(f"✅ 推荐服务响应时间: {(end_time - start_time)*1000:.1f}毫秒")
    else:
        print(f"⚠️  推荐服务性能测试失败")
    
    # 清理
    cleanup_ai_services()
    
except Exception as e:
    print(f"❌ 性能测试异常: {e}")