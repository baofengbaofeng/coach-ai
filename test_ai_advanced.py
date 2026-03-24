#!/usr/bin/env python
"""
高级AI服务测试：测试更复杂的AI算法和功能。
"""
import os
import sys
import django
from datetime import datetime, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

print("高级AI服务测试开始...")
print("=" * 50)

User = get_user_model()

# 1. 创建测试用户
print("1. 创建测试用户:")
print("-" * 30)

try:
    user, created = User.objects.get_or_create(
        username="ai_advanced_test_user",
        defaults={
            "email": "ai_advanced@example.com",
            "password": "test123",
        }
    )
    
    if created:
        print(f"✅ 创建测试用户: {user.username} (ID: {user.id})")
    else:
        print(f"✅ 使用现有测试用户: {user.username} (ID: {user.id})")
        
except Exception as e:
    print(f"❌ 创建测试用户失败: {e}")
    sys.exit(1)

# 2. 测试AI服务管理器
print("\n2. 测试AI服务管理器:")
print("-" * 30)

try:
    from services.manager import get_ai_service_manager
    
    manager = get_ai_service_manager()
    
    print(f"✅ AI服务管理器初始化成功")
    print(f"   可用服务: {list(manager.get_available_services())}")
    print(f"   服务状态: {manager.get_service_status()}")
    
    # 测试服务配置
    config = manager.get_service_config("recommendation")
    print(f"✅ 推荐服务配置获取成功")
    print(f"   最大推荐数: {config.get('max_recommendations', 'N/A')}")
    print(f"   缓存时间: {config.get('cache_ttl_minutes', 'N/A')}分钟")
    
except Exception as e:
    print(f"❌ AI服务管理器测试失败: {e}")

# 3. 测试推荐服务的智能算法
print("\n3. 测试推荐服务智能算法:")
print("-" * 30)

try:
    from services.recommendation import RecommendationService
    
    # 创建推荐服务实例
    rec_service = RecommendationService({
        "max_recommendations": 10,
        "similarity_threshold": 0.6,
        "diversity_factor": 0.3,
        "enable_content_based": True,
        "enable_collaborative": True,
        "enable_hybrid": True,
    })
    
    print(f"✅ 推荐服务创建成功")
    
    # 测试用户行为分析
    print(f"\n  测试用户行为分析:")
    
    # 模拟用户行为数据
    user_behavior = {
        "exercise_history": [
            {"type": "running", "duration": 30, "date": "2026-03-20"},
            {"type": "yoga", "duration": 45, "date": "2026-03-21"},
            {"type": "running", "duration": 40, "date": "2026-03-22"},
        ],
        "task_history": [
            {"category": "work", "priority": "high", "completed": True},
            {"category": "personal", "priority": "medium", "completed": True},
            {"category": "health", "priority": "low", "completed": False},
        ],
        "achievement_history": [
            {"type": "exercise", "unlocked": True},
            {"type": "task", "unlocked": False},
        ],
    }
    
    # 分析用户偏好
    preferences = rec_service._analyze_user_preferences(user_behavior)
    print(f"   ✅ 用户偏好分析完成")
    print(f"      运动偏好: {preferences.get('exercise_preferences', [])}")
    print(f"      任务偏好: {preferences.get('task_preferences', [])}")
    print(f"      成就偏好: {preferences.get('achievement_preferences', [])}")
    
    # 测试相似度计算
    print(f"\n  测试相似度计算:")
    
    item1 = {"type": "running", "difficulty": "medium", "duration": 30}
    item2 = {"type": "running", "difficulty": "easy", "duration": 25}
    item3 = {"type": "yoga", "difficulty": "medium", "duration": 45}
    
    similarity_12 = rec_service._calculate_similarity(item1, item2)
    similarity_13 = rec_service._calculate_similarity(item1, item3)
    
    print(f"   ✅ 相似度计算完成")
    print(f"      跑步(中) vs 跑步(易): {similarity_12:.2f}")
    print(f"      跑步(中) vs 瑜伽(中): {similarity_13:.2f}")
    
    # 测试多样性推荐
    print(f"\n  测试多样性推荐:")
    
    items = [
        {"id": 1, "type": "running", "score": 0.9},
        {"id": 2, "type": "running", "score": 0.85},
        {"id": 3, "type": "yoga", "score": 0.8},
        {"id": 4, "type": "swimming", "score": 0.75},
        {"id": 5, "type": "cycling", "score": 0.7},
    ]
    
    diverse_items = rec_service._apply_diversity(items, diversity_factor=0.3)
    print(f"   ✅ 多样性推荐完成")
    print(f"      原始项目数: {len(items)}")
    print(f"      多样性项目数: {len(diverse_items)}")
    print(f"      类型分布: {[item['type'] for item in diverse_items]}")
    
except Exception as e:
    print(f"❌ 推荐服务智能算法测试失败: {e}")

# 4. 测试分析服务的智能算法
print("\n4. 测试分析服务智能算法:")
print("-" * 30)

try:
    from services.analytics_simple import SimpleAnalyticsService
    
    # 创建分析服务实例
    analytics_service = SimpleAnalyticsService({
        "analysis_period_days": 30,
        "enable_basic_analysis": True,
    })
    
    print(f"✅ 分析服务创建成功")
    
    # 测试数据聚合
    print(f"\n  测试数据聚合:")
    
    # 模拟用户数据
    user_data = {
        "exercise_records": [
            {"date": "2026-03-01", "duration": 30, "calories": 300},
            {"date": "2026-03-05", "duration": 45, "calories": 450},
            {"date": "2026-03-10", "duration": 60, "calories": 600},
            {"date": "2026-03-15", "duration": 30, "calories": 300},
            {"date": "2026-03-20", "duration": 45, "calories": 450},
        ],
        "task_records": [
            {"date": "2026-03-02", "completed": True, "priority": "high"},
            {"date": "2026-03-07", "completed": True, "priority": "medium"},
            {"date": "2026-03-12", "completed": False, "priority": "low"},
            {"date": "2026-03-17", "completed": True, "priority": "high"},
            {"date": "2026-03-22", "completed": True, "priority": "medium"},
        ],
    }
    
    # 分析数据趋势
    trend_analysis = analytics_service._analyze_trends(user_data)
    print(f"   ✅ 趋势分析完成")
    print(f"      运动频率趋势: {trend_analysis.get('exercise_frequency_trend', 'N/A')}")
    print(f"      任务完成率趋势: {trend_analysis.get('task_completion_trend', 'N/A')}")
    
    # 测试模式识别
    print(f"\n  测试模式识别:")
    
    patterns = analytics_service._identify_patterns(user_data)
    print(f"   ✅ 模式识别完成")
    
    if patterns.get("exercise_patterns"):
        print(f"      运动模式: {patterns['exercise_patterns']}")
    
    if patterns.get("task_patterns"):
        print(f"      任务模式: {patterns['task_patterns']}")
    
    # 测试洞察提取
    print(f"\n  测试洞察提取:")
    
    insights = analytics_service._extract_insights(user_data)
    print(f"   ✅ 洞察提取完成")
    
    for i, insight in enumerate(insights[:3], 1):
        print(f"      洞察{i}: {insight.get('title')}")
        print(f"          描述: {insight.get('description')}")
    
except Exception as e:
    print(f"❌ 分析服务智能算法测试失败: {e}")

# 5. 测试预测服务的智能算法
print("\n5. 测试预测服务智能算法:")
print("-" * 30)

try:
    from services.prediction import PredictionService
    
    # 创建预测服务实例
    prediction_service = PredictionService({
        "prediction_horizon_days": 14,
        "confidence_threshold": 0.75,
        "enable_task_completion_prediction": True,
        "enable_exercise_habit_prediction": True,
        "enable_achievement_unlock_prediction": True,
        "enable_trend_prediction": True,
        "cache_ttl_minutes": 60,
    })
    
    print(f"✅ 预测服务创建成功")
    
    # 测试时间序列预测
    print(f"\n  测试时间序列预测:")
    
    # 模拟时间序列数据
    time_series = [
        {"date": "2026-02-01", "value": 10},
        {"date": "2026-02-08", "value": 12},
        {"date": "2026-02-15", "value": 15},
        {"date": "2026-02-22", "value": 18},
        {"date": "2026-03-01", "value": 20},
    ]
    
    forecast = prediction_service._forecast_time_series(time_series, horizon=7)
    print(f"   ✅ 时间序列预测完成")
    print(f"      预测周期: {forecast.get('horizon', 'N/A')}天")
    print(f"      预测值: {forecast.get('forecast_values', [])}")
    print(f"      置信区间: {forecast.get('confidence_interval', 'N/A')}")
    
    # 测试概率预测
    print(f"\n  测试概率预测:")
    
    probability_pred = prediction_service._calculate_probabilities({
        "historical_success_rate": 0.85,
        "recent_trend": 0.1,
        "external_factors": 0.05,
    })
    
    print(f"   ✅ 概率预测完成")
    print(f"      成功概率: {probability_pred.get('success_probability', 0):.2%}")
    print(f"      置信度: {probability_pred.get('confidence', 0):.2%}")
    
    # 测试风险评估
    print(f"\n  测试风险评估:")
    
    risk_assessment = prediction_service._assess_risks({
        "volatility": 0.2,
        "uncertainty": 0.3,
        "dependencies": 0.1,
    })
    
    print(f"   ✅ 风险评估完成")
    print(f"      总体风险等级: {risk_assessment.get('overall_risk_level', 'N/A')}")
    print(f"      风险因素: {risk_assessment.get('risk_factors', [])}")
    
except Exception as e:
    print(f"❌ 预测服务智能算法测试失败: {e}")

# 6. 测试AI服务集成
print("\n6. 测试AI服务集成:")
print("-" * 30)

try:
    # 测试端到端AI工作流
    print(f"测试端到端AI工作流:")
    
    # 1. 分析用户数据
    analysis_result = manager.process_analysis(
        user,
        type="comprehensive",
        period_days=30
    )
    
    if analysis_result.get("success"):
        print(f"  ✅ 用户数据分析完成")
        analysis_data = analysis_result.get("data", {})
        
        # 2. 基于分析结果生成推荐
        recommendation_result = manager.process_recommendation(
            user,
            type="personalized",
            max_recommendations=5,
            analysis_data=analysis_data
        )
        
        if recommendation_result.get("success"):
            print(f"  ✅ 个性化推荐生成完成")
            recommendations = recommendation_result.get("recommendations", [])
            print(f"      推荐数量: {len(recommendations)}")
            
            # 3. 基于推荐生成预测
            prediction_result = manager.process_prediction(
                user,
                type="all",
                horizon_days=7,
                recommendations=recommendations
            )
            
            if prediction_result.get("success"):
                print(f"  ✅ 综合预测生成完成")
                predictions = prediction_result.get("predictions", {})
                summary = predictions.get("summary", {})
                print(f"      总体置信度: {summary.get('overall_confidence', 0):.2%}")
                
                # 4. 生成AI建议
                ai_advice = manager.generate_ai_advice(
                    user,
                    analysis_data=analysis_data,
                    recommendations=recommendations,
                    predictions=predictions
                )
                
                if ai_advice.get("success"):
                    print(f"  ✅ AI建议生成完成")
                    advice = ai_advice.get("advice", {})
                    print(f"      建议数量: {len(advice.get('action_items', []))}")
                    print(f"      优先级: {advice.get('priority', 'N/A')}")
                else:
                    print(f"  ⚠️  AI建议生成失败: {ai_advice.get('error', {}).get('message')}")
            else:
                print(f"  ⚠️  预测生成失败: {prediction_result.get('error', {}).get('message')}")
        else:
            print(f"  ⚠️  推荐生成失败: {recommendation_result.get('error', {}).get('message')}")
    else:
        print(f"  ⚠️  分析失败: {analysis_result.get('error', {}).get('message')}")
    
    print(f"\n  ✅ 端到端AI工作流测试完成")
    
except Exception as e:
    print(f"❌ AI服务集成测试失败: {e}")

# 7. 测试性能优化
print("\n7. 测试性能优化:")
print("-" * 30)

import time

try:
    print(f"测试AI服务性能:")
    
    # 测试缓存效果
    start_time = time.time()
    
    # 第一次调用（无缓存）
    result1 = manager.process_recommendation(user, type="all", max_recommendations=5)
    time1 = time.time() - start_time
    
    # 第二次调用（有缓存）
    start_time = time.time()
    result2 = manager.process_recommendation(user, type="all", max_recommendations=5)
    time2 = time.time() - start_time
    
    print(f"  ✅ 缓存性能测试完成")
    print(f"      第一次调用时间: {time1:.3f}秒")
    print(f"      第二次调用时间: {time2:.3f}秒")
    print(f"      性能提升: {(time1 - time2) / time1 * 100:.1f}%")
    
    # 测试并发处理
    print(f"\n  测试并发处理:")
    
    import threading
    
    results = []
    errors = []
    
    def test_concurrent(user_id, service_type):
        try:
            if service_type == "recommendation":
                result = manager.process_recommendation(user_id, type="all")
            elif service_type == "analysis":
                result = manager.process_analysis(user_id, type="basic")
            elif service_type == "prediction":
                result = manager.process_prediction(user_id, type="all")
            results.append((service_type, "success"))
        except Exception as e:
            errors.append((service_type, str(e)))
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=test_concurrent, args=(user.id, "recommendation"))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"  ✅ 并发处理测试完成")
    print(f"      成功调用: {len(results)}")
    print(f"      失败调用: {len(errors)}")
    
except Exception as e:
    print(f"❌ 性能优化测试失败: {e}")

# 8. 清理测试数据
print("\n8. 清理测试数据:")
print("-" * 30)

try:
    # 删除测试用户
    deleted, _ = User.objects.filter(username="ai_advanced_test_user").delete()
    
    print(f"✅ 清理测试数据完成")
    print(f"   删除记录数: {deleted}")
    
except Exception as e:
    print(f"❌ 清理测试数据失败: {e}")

print("\n" + "=" * 50)
print("高级AI服务测试完成!")

# 9. 测试总结
print("\n9. 测试总结:")
print("-" * 30)

print("✅ 测试覆盖的AI功能:")
print("   - 用户行为分析和偏好识别")
print("   - 项目相似度计算和多样性推荐")
print("   - 数据趋势分析和模式识别")
print("   - 时间序列预测和概率计算")
print("   - 风险评估和置信度评估")
print("