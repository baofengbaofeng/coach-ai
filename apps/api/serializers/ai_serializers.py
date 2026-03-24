"""
AI服务API序列化器。
按照豆包AI助手最佳实践：提供类型安全的AI API序列化器。
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from rest_framework import serializers


# ==================== AI推荐请求序列化器 ====================
class AIRecommendationRequestSerializer(serializers.Serializer):
    """
    AI推荐请求序列化器。
    """
    
    recommendation_type = serializers.ChoiceField(
        choices=[
            ("all", "全部推荐"),
            ("exercise", "运动推荐"),
            ("task", "任务推荐"),
            ("achievement", "成就推荐"),
            ("category", "分类推荐"),
        ],
        default="all",
        help_text="推荐类型",
    )
    
    max_recommendations = serializers.IntegerField(
        min_value=1,
        max_value=50,
        default=10,
        help_text="最大推荐数量",
    )
    
    similarity_threshold = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        default=0.6,
        help_text="相似度阈值",
    )
    
    diversity_factor = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        default=0.3,
        help_text="多样性因子",
    )
    
    enable_content_based = serializers.BooleanField(
        default=True,
        help_text="启用基于内容的推荐",
    )
    
    enable_collaborative = serializers.BooleanField(
        default=True,
        help_text="启用协同过滤推荐",
    )
    
    enable_hybrid = serializers.BooleanField(
        default=True,
        help_text="启用混合推荐",
    )
    
    user_context = serializers.DictField(
        required=False,
        help_text="用户上下文信息",
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证数据。
        
        Args:
            attrs: 属性字典
            
        Returns:
            验证后的属性字典
        """
        # 确保至少启用一种推荐算法
        if not any([
            attrs.get("enable_content_based", True),
            attrs.get("enable_collaborative", True),
            attrs.get("enable_hybrid", True),
        ]):
            raise serializers.ValidationError("至少需要启用一种推荐算法")
        
        return attrs


# ==================== AI推荐响应序列化器 ====================
class RecommendationItemSerializer(serializers.Serializer):
    """
    推荐项序列化器。
    """
    
    id = serializers.CharField(help_text="推荐项ID")
    title = serializers.CharField(help_text="推荐项标题")
    description = serializers.CharField(help_text="推荐项描述")
    type = serializers.CharField(help_text="推荐项类型")
    score = serializers.FloatField(help_text="推荐分数")
    confidence = serializers.FloatField(help_text="置信度")
    metadata = serializers.DictField(help_text="元数据")


class AIRecommendationResponseSerializer(serializers.Serializer):
    """
    AI推荐响应序列化器。
    """
    
    success = serializers.BooleanField(help_text="是否成功")
    user_id = serializers.IntegerField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    recommendation_type = serializers.CharField(help_text="推荐类型")
    total_count = serializers.IntegerField(help_text="总推荐数")
    generated_at = serializers.DateTimeField(help_text="生成时间")
    recommendations = RecommendationItemSerializer(many=True, help_text="推荐列表")
    
    error = serializers.DictField(
        required=False,
        help_text="错误信息",
    )


# ==================== AI分析请求序列化器 ====================
class AIAnalysisRequestSerializer(serializers.Serializer):
    """
    AI分析请求序列化器。
    """
    
    analysis_type = serializers.ChoiceField(
        choices=[
            ("comprehensive", "综合分析"),
            ("exercise", "运动分析"),
            ("task", "任务分析"),
            ("achievement", "成就分析"),
            ("trend", "趋势分析"),
        ],
        default="comprehensive",
        help_text="分析类型",
    )
    
    period_days = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=30,
        help_text="分析周期（天）",
    )
    
    enable_basic_analysis = serializers.BooleanField(
        default=True,
        help_text="启用基础分析",
    )
    
    enable_trend_analysis = serializers.BooleanField(
        default=True,
        help_text="启用趋势分析",
    )
    
    enable_pattern_recognition = serializers.BooleanField(
        default=True,
        help_text="启用模式识别",
    )
    
    enable_insight_extraction = serializers.BooleanField(
        default=True,
        help_text="启用洞察提取",
    )
    
    user_context = serializers.DictField(
        required=False,
        help_text="用户上下文信息",
    )


# ==================== AI分析响应序列化器 ====================
class AnalysisSummarySerializer(serializers.Serializer):
    """
    分析摘要序列化器。
    """
    
    user_id = serializers.IntegerField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    analysis_period_days = serializers.IntegerField(help_text="分析周期（天）")
    analysis_date = serializers.DateTimeField(help_text="分析日期")
    overall_score = serializers.FloatField(help_text="总体分数")


class AnalysisItemSerializer(serializers.Serializer):
    """
    分析项序列化器。
    """
    
    type = serializers.CharField(help_text="分析类型")
    title = serializers.CharField(help_text="分析标题")
    description = serializers.CharField(help_text="分析描述")
    value = serializers.FloatField(help_text="分析值")
    unit = serializers.CharField(help_text="单位")
    trend = serializers.CharField(help_text="趋势")


class InsightSerializer(serializers.Serializer):
    """
    洞察序列化器。
    """
    
    type = serializers.CharField(help_text="洞察类型")
    title = serializers.CharField(help_text="洞察标题")
    description = serializers.CharField(help_text="洞察描述")
    priority = serializers.CharField(help_text="优先级")
    score = serializers.FloatField(help_text="分数")


class AIAnalysisResponseSerializer(serializers.Serializer):
    """
    AI分析响应序列化器。
    """
    
    success = serializers.BooleanField(help_text="是否成功")
    user_id = serializers.IntegerField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    analysis_type = serializers.CharField(help_text="分析类型")
    analysis_period_days = serializers.IntegerField(help_text="分析周期（天）")
    generated_at = serializers.DateTimeField(help_text="生成时间")
    summary = AnalysisSummarySerializer(help_text="分析摘要")
    analysis_items = AnalysisItemSerializer(many=True, help_text="分析项列表")
    insights = InsightSerializer(many=True, help_text="洞察列表")
    
    error = serializers.DictField(
        required=False,
        help_text="错误信息",
    )


# ==================== AI预测请求序列化器 ====================
class AIPredictionRequestSerializer(serializers.Serializer):
    """
    AI预测请求序列化器。
    """
    
    prediction_type = serializers.ChoiceField(
        choices=[
            ("all", "全部预测"),
            ("task", "任务预测"),
            ("exercise", "运动预测"),
            ("achievement", "成就预测"),
            ("trend", "趋势预测"),
        ],
        default="all",
        help_text="预测类型",
    )
    
    horizon_days = serializers.IntegerField(
        min_value=1,
        max_value=90,
        default=7,
        help_text="预测周期（天）",
    )
    
    confidence_threshold = serializers.FloatField(
        min_value=0.0,
        max_value=1.0,
        default=0.7,
        help_text="置信度阈值",
    )
    
    enable_task_completion_prediction = serializers.BooleanField(
        default=True,
        help_text="启用任务完成预测",
    )
    
    enable_exercise_habit_prediction = serializers.BooleanField(
        default=True,
        help_text="启用运动习惯预测",
    )
    
    enable_achievement_unlock_prediction = serializers.BooleanField(
        default=True,
        help_text="启用成就解锁预测",
    )
    
    enable_trend_prediction = serializers.BooleanField(
        default=True,
        help_text="启用趋势预测",
    )
    
    user_context = serializers.DictField(
        required=False,
        help_text="用户上下文信息",
    )


# ==================== AI预测响应序列化器 ====================
class PredictionItemSerializer(serializers.Serializer):
    """
    预测项序列化器。
    """
    
    type = serializers.CharField(help_text="预测类型")
    title = serializers.CharField(help_text="预测标题")
    predicted_value = serializers.FloatField(help_text="预测值")
    confidence = serializers.FloatField(help_text="置信度")
    lower_bound = serializers.FloatField(help_text="下限")
    upper_bound = serializers.FloatField(help_text="上限")
    unit = serializers.CharField(help_text="单位")


class PredictionSummarySerializer(serializers.Serializer):
    """
    预测摘要序列化器。
    """
    
    total_predictions = serializers.IntegerField(help_text="总预测数")
    high_confidence_predictions = serializers.IntegerField(help_text="高置信度预测数")
    overall_confidence = serializers.FloatField(help_text="总体置信度")
    key_takeaways = serializers.ListField(
        child=serializers.CharField(),
        help_text="关键要点",
    )
    action_items = serializers.ListField(
        child=serializers.CharField(),
        help_text="行动项",
    )


class AIPredictionResponseSerializer(serializers.Serializer):
    """
    AI预测响应序列化器。
    """
    
    success = serializers.BooleanField(help_text="是否成功")
    user_id = serializers.IntegerField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    prediction_type = serializers.CharField(help_text="预测类型")
    prediction_horizon = serializers.IntegerField(help_text="预测周期（天）")
    generated_at = serializers.DateTimeField(help_text="生成时间")
    predictions = PredictionItemSerializer(many=True, help_text="预测列表")
    summary = PredictionSummarySerializer(help_text="预测摘要")
    
    error = serializers.DictField(
        required=False,
        help_text="错误信息",
    )


# ==================== AI建议请求序列化器 ====================
class AIAdviceRequestSerializer(serializers.Serializer):
    """
    AI建议请求序列化器。
    """
    
    advice_type = serializers.ChoiceField(
        choices=[
            ("general", "通用建议"),
            ("exercise", "运动建议"),
            ("task", "任务建议"),
            ("achievement", "成就建议"),
            ("personalized", "个性化建议"),
        ],
        default="personalized",
        help_text="建议类型",
    )
    
    analysis_data = serializers.DictField(
        required=False,
        help_text="分析数据",
    )
    
    recommendations = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="推荐数据",
    )
    
    predictions = serializers.DictField(
        required=False,
        help_text="预测数据",
    )
    
    user_context = serializers.DictField(
        required=False,
        help_text="用户上下文信息",
    )


# ==================== AI建议响应序列化器 ====================
class AdviceItemSerializer(serializers.Serializer):
    """
    建议项序列化器。
    """
    
    type = serializers.CharField(help_text="建议类型")
    title = serializers.CharField(help_text="建议标题")
    description = serializers.CharField(help_text="建议描述")
    priority = serializers.CharField(help_text="优先级")
    action_items = serializers.ListField(
        child=serializers.CharField(),
        help_text="行动项",
    )
    expected_impact = serializers.FloatField(help_text="预期影响")


class AIAdviceResponseSerializer(serializers.Serializer):
    """
    AI建议响应序列化器。
    """
    
    success = serializers.BooleanField(help_text="是否成功")
    user_id = serializers.IntegerField(help_text="用户ID")
    username = serializers.CharField(help_text="用户名")
    advice_type = serializers.CharField(help_text="建议类型")
    generated_at = serializers.DateTimeField(help_text="生成时间")
    total_advice_items = serializers.IntegerField(help_text="总建议数")
    advice_items = AdviceItemSerializer(many=True, help_text="建议列表")
    summary = serializers.DictField(help_text="建议摘要")
    
    error = serializers.DictField(
        required=False,
        help_text="错误信息",
    )