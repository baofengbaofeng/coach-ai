#!/usr/bin/env python3
"""
基础测试运行脚本。
用于运行基本的模型测试，不依赖外部服务。
"""
import os
import sys
import django
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps"))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

# 初始化Django
try:
    django.setup()
    print("✅ Django设置成功")
except Exception as e:
    print(f"❌ Django设置失败: {e}")
    sys.exit(1)

import pytest


def run_model_tests():
    """运行模型测试"""
    print("\n" + "="*60)
    print("运行模型单元测试")
    print("="*60)
    
    test_file = project_root / "tests" / "unit" / "test_models.py"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    # 运行pytest测试
    result = pytest.main([
        str(test_file),
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])
    
    return result == 0


def run_api_tests():
    """运行API测试"""
    print("\n" + "="*60)
    print("运行API集成测试")
    print("="*60)
    
    test_file = project_root / "tests" / "integration" / "test_api.py"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    # 运行pytest测试
    result = pytest.main([
        str(test_file),
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])
    
    return result == 0


def run_system_tests():
    """运行系统测试"""
    print("\n" + "="*60)
    print("运行系统测试")
    print("="*60)
    
    test_file = project_root / "tests" / "system" / "test_user_flows.py"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    # 运行pytest测试
    result = pytest.main([
        str(test_file),
        "-v",
        "--tb=short",
        "--disable-warnings"
    ])
    
    return result == 0


def main():
    """主函数"""
    print("Coach AI 基础测试框架")
    print("="*60)
    
    # 创建测试报告目录
    reports_dir = project_root / "tests" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    success = True
    
    try:
        # 运行模型测试
        if not run_model_tests():
            success = False
        
        # 运行API测试
        if not run_api_tests():
            success = False
        
        # 运行系统测试
        if not run_system_tests():
            success = False
        
        # 输出结果
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        
        if success:
            print("✅ 所有测试通过！")
            return 0
        else:
            print("❌ 有测试失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())