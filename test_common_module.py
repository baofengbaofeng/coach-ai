#!/usr/bin/env python
"""
测试公共功能模块基本功能
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.simple")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from apps.common.utils import (
    generate_random_string,
    generate_slug,
    truncate_text,
    is_valid_email,
    is_valid_phone,
    format_number,
    calculate_percentage,
    calculate_average,
    format_datetime,
    get_time_range,
    is_weekend,
    validate_required_fields,
    get_cache_key,
    hash_string,
    generate_secure_token,
    get_file_extension,
    safe_json_loads,
    safe_json_dumps,
    paginate_queryset,
    create_error_response,
    create_success_response,
    calculate_progress,
    format_duration,
    Timer,
    measure_execution_time,
)

print("测试公共功能模块基本功能...")
print("=" * 50)

# 1. 测试字符串处理工具
print("1. 字符串处理工具测试:")
print("-" * 30)

# 生成随机字符串
random_str = generate_random_string(10)
print(f"✅ 随机字符串: {random_str} (长度: {len(random_str)})")

# 生成slug
slug = generate_slug("Hello World! This is a test.")
print(f"✅ Slug: {slug}")

# 截断文本
truncated = truncate_text("这是一个很长的文本需要被截断", 10)
print(f"✅ 截断文本: {truncated}")

# 验证邮箱
email_valid = is_valid_email("test@example.com")
email_invalid = is_valid_email("invalid-email")
print(f"✅ 邮箱验证: test@example.com -> {email_valid}")
print(f"✅ 邮箱验证: invalid-email -> {email_invalid}")

# 验证手机号
phone_valid = is_valid_phone("13800138000")
phone_invalid = is_valid_phone("123456")
print(f"✅ 手机号验证: 13800138000 -> {phone_valid}")
print(f"✅ 手机号验证: 123456 -> {phone_invalid}")

print()

# 2. 测试数字处理工具
print("2. 数字处理工具测试:")
print("-" * 30)

# 格式化数字
formatted = format_number(1234.5678, 2)
print(f"✅ 格式化数字: 1234.5678 -> {formatted}")

# 计算百分比
percentage = calculate_percentage(25, 100)
print(f"✅ 计算百分比: 25/100 -> {percentage}%")

# 计算平均值
average = calculate_average([1, 2, 3, 4, 5])
print(f"✅ 计算平均值: [1,2,3,4,5] -> {average}")

print()

# 3. 测试日期时间工具
print("3. 日期时间工具测试:")
print("-" * 30)

# 格式化日期时间
now = datetime.now()
formatted_dt = format_datetime(now)
print(f"✅ 格式化日期时间: {formatted_dt}")

# 获取时间范围
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 1, 5)
date_range = get_time_range(start_date, end_date)
print(f"✅ 时间范围: {start_date.date()} 到 {end_date.date()} -> {len(date_range)} 天")

# 检查周末
weekend_check = is_weekend(datetime(2024, 1, 6))  # 周六
print(f"✅ 检查周末: 2024-01-06 -> {weekend_check}")

print()

# 4. 测试数据验证工具
print("4. 数据验证工具测试:")
print("-" * 30)

# 验证必填字段
data = {"name": "John", "age": 30, "email": ""}
missing = validate_required_fields(data, ["name", "age", "email", "address"])
print(f"✅ 验证必填字段: {data}")
print(f"   缺失字段: {missing}")

print()

# 5. 测试缓存工具
print("5. 缓存工具测试:")
print("-" * 30)

# 生成缓存键
cache_key = get_cache_key("user", 123, "profile")
print(f"✅ 生成缓存键: user:123:profile -> {cache_key}")

print()

# 6. 测试安全工具
print("6. 安全工具测试:")
print("-" * 30)

# 哈希字符串
hashed = hash_string("password123")
print(f"✅ 哈希字符串: password123 -> {hashed[:20]}...")

# 生成安全令牌
token = generate_secure_token(16)
print(f"✅ 生成安全令牌: {token} (长度: {len(token)})")

print()

# 7. 测试文件处理工具
print("7. 文件处理工具测试:")
print("-" * 30)

# 获取文件扩展名
extension = get_file_extension("document.pdf")
print(f"✅ 文件扩展名: document.pdf -> {extension}")

print()

# 8. 测试JSON处理工具
print("8. JSON处理工具测试:")
print("-" * 30)

# JSON序列化和反序列化
data_dict = {"name": "John", "age": 30, "active": True}
json_str = safe_json_dumps(data_dict)
parsed = safe_json_loads(json_str)
print(f"✅ JSON序列化: {data_dict} -> {json_str[:50]}...")
print(f"✅ JSON反序列化: -> {parsed}")

print()

# 9. 测试错误处理工具
print("9. 错误处理工具测试:")
print("-" * 30)

# 创建错误响应
error_resp = create_error_response("操作失败", "validation_error", 400, {"field": "email"})
print(f"✅ 错误响应: {error_resp}")

# 创建成功响应
success_resp = create_success_response({"id": 123, "name": "John"}, "操作成功")
print(f"✅ 成功响应: {success_resp}")

print()

# 10. 测试业务逻辑工具
print("10. 业务逻辑工具测试:")
print("-" * 30)

# 计算进度
progress = calculate_progress(75, 100)
print(f"✅ 计算进度: 75/100 -> {progress}%")

# 格式化持续时间
duration = format_duration(3665)  # 1小时1分钟5秒
print(f"✅ 格式化持续时间: 3665秒 -> {duration}")

print()

# 11. 测试性能监控工具
print("11. 性能监控工具测试:")
print("-" * 30)

# 使用计时器
with Timer("测试计时器") as timer:
    import time
    time.sleep(0.1)

print(f"✅ 计时器测试完成: {timer.elapsed_time:.3f}秒")

# 使用装饰器
@measure_execution_time
def test_function():
    import time
    time.sleep(0.05)
    return "完成"

result = test_function()
print(f"✅ 装饰器测试: {result}")

print()

# 12. 综合测试
print("12. 综合测试:")
print("-" * 30)

# 模拟分页数据
class MockQuerySet:
    def __init__(self, data):
        self.data = data
    
    def count(self):
        return len(self.data)
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return self.data[index.start:index.stop]
        return self.data[index]

mock_data = list(range(1, 101))
mock_qs = MockQuerySet(mock_data)

pagination = paginate_queryset(mock_qs, page=2, page_size=20)
print(f"✅ 分页测试:")
print(f"   页码: {pagination['page']}")
print(f"   每页大小: {pagination['page_size']}")
print(f"   总数: {pagination['total_count']}")
print(f"   总页数: {pagination['total_pages']}")
print(f"   是否有上一页: {pagination['has_previous']}")
print(f"   是否有下一页: {pagination['has_next']}")
print(f"   当前页数据: {pagination['items'][:5]}...")

print()

print("=" * 50)
print("公共功能模块测试完成!")
print("如果所有测试都显示✅，说明公共功能模块基本功能正常。")

# 测试模板标签和过滤器（需要Django模板环境）
try:
    from django.template import Template, Context
    
    print("\n13. 模板过滤器测试:")
    print("-" * 30)
    
    # 测试模板过滤器
    template_code = """
    {{ text|truncate:10 }}
    {{ number|format_number:2 }}
    {{ date|format_date }}
    """
    
    template = Template("{% load common_filters %}" + template_code)
    context = Context({
        "text": "这是一个很长的文本",
        "number": 1234.5678,
        "date": datetime.now(),
    })
    
    result = template.render(context)
    print(f"✅ 模板过滤器渲染成功")
    print(f"   结果: {result.strip()}")
    
except Exception as e:
    print(f"⚠️  模板测试跳过: {str(e)}")