"""
测试常量定义。
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 直接导入常量模块，不依赖Django
import importlib.util

# 加载constants模块
spec = importlib.util.spec_from_file_location(
    "constants", 
    BASE_DIR / "core" / "constants.py"
)
constants_module = importlib.util.module_from_spec(spec)

# 执行模块代码（不触发Django依赖）
exec(open(BASE_DIR / "core" / "constants.py").read(), constants_module.__dict__)

# 现在可以访问常量
BusinessRules = constants_module.BusinessRules
FileTypes = constants_module.FileTypes
HomeworkStatus = constants_module.HomeworkStatus
QuestionType = constants_module.QuestionType

print("✅ 常量模块加载成功")

# 检查BusinessRules常量
print("\n🔍 BusinessRules常量检查:")
print(f"  HOMEWORK_TITLE_MAX_LENGTH: {BusinessRules.HOMEWORK_TITLE_MAX_LENGTH}")
print(f"  HOMEWORK_DESCRIPTION_MAX_LENGTH: {BusinessRules.HOMEWORK_DESCRIPTION_MAX_LENGTH}")
print(f"  SUBJECT_NAME_MAX_LENGTH: {BusinessRules.SUBJECT_NAME_MAX_LENGTH}")
print(f"  STATUS_MAX_LENGTH: {BusinessRules.STATUS_MAX_LENGTH}")

# 检查FileTypes常量
print("\n🔍 FileTypes常量检查:")
print(f"  IMAGE_EXTENSIONS: {FileTypes.IMAGE_EXTENSIONS}")
print(f"  PDF_EXTENSIONS: {FileTypes.PDF_EXTENSIONS}")

# 检查枚举
print("\n🔍 枚举检查:")
print(f"  HomeworkStatus值: {[status.value for status in HomeworkStatus]}")
print(f"  QuestionType值: {[qtype.value for qtype in QuestionType]}")

# 检查所有BusinessRules属性
print("\n🔍 BusinessRules所有属性:")
attrs = [attr for attr in dir(BusinessRules) if not attr.startswith('_')]
for attr in attrs:
    try:
        value = getattr(BusinessRules, attr)
        print(f"  {attr}: {value}")
    except:
        print(f"  {attr}: <无法获取>")