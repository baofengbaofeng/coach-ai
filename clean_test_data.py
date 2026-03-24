#!/usr/bin/env python
"""
清理测试数据
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.tasks.models import Task, TaskCategory, TaskComment, TaskReminder
from django.contrib.auth import get_user_model

User = get_user_model()

print("清理测试数据...")

# 清理任务相关数据
deleted_count = 0

# 清理测试任务
tasks = Task.objects.filter(title__icontains="测试").filter(title__icontains="验证")
deleted_count += tasks.count()
tasks.delete()
print(f"删除 {deleted_count} 个测试任务")

# 清理测试分类
categories = TaskCategory.objects.filter(name__icontains="测试").filter(name__icontains="验证")
cat_count = categories.count()
deleted_count += cat_count
categories.delete()
print(f"删除 {cat_count} 个测试分类")

# 清理测试用户
users = User.objects.filter(username__icontains="test").filter(username__icontains="validator")
user_count = users.count()
deleted_count += user_count
users.delete()
print(f"删除 {user_count} 个测试用户")

print(f"总计清理 {deleted_count} 条测试数据")
print("清理完成！")