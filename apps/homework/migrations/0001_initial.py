"""
初始迁移文件，创建作业、题目、知识点等核心数据表。
按照豆包AI助手最佳实践：使用Django迁移系统管理数据库结构变更。
"""
from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    初始迁移类。
    """
    
    initial = True
    
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    
    operations = [
        migrations.CreateModel(
            name="Homework",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="作业的标题，用于快速识别作业内容", max_length=200, verbose_name="作业标题")),
                ("description", models.TextField(blank=True, help_text="作业的详细描述和要求", max_length=2000, verbose_name="作业描述")),
                ("subject", models.CharField(help_text="作业所属的学科，如：数学、语文、英语等", max_length=50, verbose_name="科目")),
                ("status", models.CharField(choices=[("draft", "DRAFT"), ("submitted", "SUBMITTED"), ("processing", "PROCESSING"), ("correcting", "CORRECTING"), ("completed", "COMPLETED"), ("error", "ERROR")], default="draft", help_text="作业的当前处理状态", max_length=20, verbose_name="作业状态")),
                ("submitted_at", models.DateTimeField(auto_now_add=True, help_text="学生提交作业的时间", verbose_name="提交时间")),
                ("deadline", models.DateTimeField(blank=True, help_text="作业的截止提交时间", null=True, verbose_name="截止时间")),
                ("corrected_at", models.DateTimeField(blank=True, help_text="作业被批改完成的时间", null=True, verbose_name="批改时间")),
                ("original_file", models.FileField(help_text="学生提交的原始作业文件（图片或PDF）", upload_to="homework/original/%Y/%m/%d/", verbose_name="原始作业文件")),
                ("processed_file", models.FileField(blank=True, help_text="经过预处理（如OCR识别）后的作业文件", null=True, upload_to="homework/processed/%Y/%m/%d/", verbose_name="处理后的作业文件")),
                ("total_score", models.DecimalField(decimal_places=2, default=0, help_text="作业的总得分", max_digits=5, verbose_name="总分")),
                ("accuracy_rate", models.DecimalField(decimal_places=2, default=0, help_text="作业的正确率（百分比）", max_digits=5, verbose_name="正确率")),
                ("created_at", models.DateTimeField(auto_now_add=True, help_text="记录创建时间", verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="记录最后更新时间", verbose_name="更新时间")),
                ("student_id", models.IntegerField(help_text="学生ID", verbose_name="学生ID")),
            ],
            options={
                "verbose_name": "作业",
                "verbose_name_plural": "作业列表",
                "ordering": ["-submitted_at"],
                "indexes": [models.Index(fields=["student", "status"], name="homework_homewo_student_6b5e5c_idx"), models.Index(fields=["subject", "submitted_at"], name="homework_homewo_subject_7c6d0e_idx"), models.Index(fields=["status", "corrected_at"], name="homework_homewo_status_5e3b1a_idx")],
            },
        ),
        migrations.CreateModel(
            name="KnowledgePoint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="知识点的唯一名称", max_length=100, unique=True, verbose_name="知识点名称")),
                ("description", models.TextField(blank=True, help_text="知识点的详细描述和说明", max_length=1000, verbose_name="知识点描述")),
                ("subject", models.CharField(help_text="知识点所属的学科", max_length=50, verbose_name="所属科目")),
                ("difficulty_level", models.PositiveIntegerField(choices=[(1, "非常简单"), (2, "简单"), (3, "中等"), (4, "困难"), (5, "非常困难")], default=3, help_text="知识点的难度等级（1-5，1最简单，5最难）", verbose_name="难度等级")),
                ("created_at", models.DateTimeField(auto_now_add=True, help_text="记录创建时间", verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="记录最后更新时间", verbose_name="更新时间")),
            ],
            options={
                "verbose_name": "知识点",
                "verbose_name_plural": "知识点列表",
                "ordering": ["subject", "difficulty_level", "name"],
                "indexes": [models.Index(fields=["subject", "difficulty_level"], name="homework_knowl_subject_5d7a9a_idx"), models.Index(fields=["name"], name="homework_knowl_name_4b8d7d_idx")],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_number", models.PositiveIntegerField(help_text="题目在作业中的序号", verbose_name="题号")),
                ("content", models.TextField(help_text="题目的具体内容，从OCR识别结果中提取", max_length=5000, verbose_name="题目内容")),
                ("question_type", models.CharField(choices=[("single_choice", "SINGLE_CHOICE"), ("multiple_choice", "MULTIPLE_CHOICE"), ("true_false", "TRUE_FALSE"), ("fill_blank", "FILL_BLANK"), ("short_answer", "SHORT_ANSWER"), ("essay", "ESSAY"), ("calculation", "CALCULATION")], default="single_choice", help_text="题目的类型，如选择题、填空题、解答题等", max_length=50, verbose_name="题目类型")),
                ("student_answer", models.TextField(blank=True, help_text="学生填写的答案", max_length=2000, verbose_name="学生答案")),
                ("correct_answer", models.TextField(blank=True, help_text="题目的标准正确答案", max_length=2000, verbose_name="正确答案")),
                ("max_score", models.DecimalField(decimal_places=2, default=10, help_text="该题目的满分值", max_digits=5, verbose_name="满分")),
                ("actual_score", models.DecimalField(decimal_places=2, default=0, help_text="学生在该题目上的实际得分", max_digits=5, verbose_name="实际得分")),
                ("correction_notes", models.TextField(blank=True, help_text="老师或AI对答案的批注和反馈", max_length=1000, verbose_name="批注")),
                ("is_correct", models.BooleanField(default=False, help_text="标记该题目答案是否正确", verbose_name="是否正确")),
                ("created_at", models.DateTimeField(auto_now_add=True, help_text="记录创建时间", verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="记录最后更新时间", verbose_name="更新时间")),
                ("homework", models.ForeignKey(help_text="题目所属的作业", on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="homework.homework", verbose_name="所属作业")),
                ("knowledge_points", models.ManyToManyField(blank=True, help_text="涉及该知识点的题目", related_name="questions", to="homework.knowledgepoint", verbose_name="关联知识点")),
            ],
            options={
                "verbose_name": "题目",
                "verbose_name_plural": "题目列表",
                "ordering": ["homework", "question_number"],
                "unique_together": {("homework", "question_number")},
                "indexes": [models.Index(fields=["homework", "question_type"], name="homework_quest_homewor_6f2a3a_idx"), models.Index(fields=["is_correct", "actual_score"], name="homework_quest_is_corr_4d9c8e_idx")],
            },
        ),
    ]