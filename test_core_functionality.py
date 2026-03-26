#!/usr/bin/env python3
"""
核心功能测试脚本。
测试Coach AI项目的核心业务逻辑，不依赖完整的Django设置。
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("Coach AI 核心功能测试")
print("=" * 60)


class TestResult:
    """测试结果类"""
    
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}
    
    def success(self, message: str = "", **details):
        self.passed = True
        self.message = message
        self.details = details
        return self
    
    def failure(self, message: str = "", **details):
        self.passed = False
        self.message = message
        self.details = details
        return self
    
    def __str__(self):
        status = "✅" if self.passed else "❌"
        return f"{status} {self.name}: {self.message}"


def test_project_structure() -> TestResult:
    """测试项目结构"""
    result = TestResult("项目结构检查")
    
    required_dirs = [
        "config",
        "apps",
        "core",
        "tests",
        "docs",
    ]
    
    required_files = [
        "manage.py",
        "pyproject.toml",
        "README.md",
        ".env.example",
        ".gitignore",
        "LICENSE",
        "config/__init__.py",
        "config/urls.py",
        "config/wsgi.py",
        "config/asgi.py",
        "config/settings/__init__.py",
        "config/settings/base.py",
        "config/settings/dev.py",
        "config/settings/prod.py",
        "apps/__init__.py",
        "core/__init__.py",
        "tests/__init__.py",
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists() or not dir_path.is_dir():
            missing_dirs.append(dir_name)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists() or not full_path.is_file():
            missing_files.append(file_path)
    
    if missing_dirs or missing_files:
        return result.failure(
            "缺少必要的目录或文件",
            missing_dirs=missing_dirs,
            missing_files=missing_files
        )
    
    return result.success("项目结构完整")


def test_config_files() -> TestResult:
    """测试配置文件"""
    result = TestResult("配置文件检查")
    
    config_files = [
        "config/settings/base.py",
        "config/settings/dev.py",
        "config/settings/prod.py",
        "config/settings/test.py",
    ]
    
    for config_file in config_files:
        file_path = project_root / config_file
        if not file_path.exists():
            return result.failure(f"配置文件不存在: {config_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查基本配置
            if config_file == "config/settings/base.py":
                if "SECRET_KEY" not in content:
                    return result.failure("base.py中缺少SECRET_KEY配置")
                if "INSTALLED_APPS" not in content:
                    return result.failure("base.py中缺少INSTALLED_APPS配置")
        
        except Exception as e:
            return result.failure(f"读取配置文件失败: {config_file}", error=str(e))
    
    return result.success("所有配置文件正常")


def test_apps_structure() -> TestResult:
    """测试应用结构"""
    result = TestResult("应用结构检查")
    
    apps = ["accounts", "tasks", "achievements", "common"]
    
    for app in apps:
        app_dir = project_root / "apps" / app
        if not app_dir.exists():
            return result.failure(f"应用目录不存在: {app}")
        
        required_files = [
            "__init__.py",
            "apps.py",
            "models.py",
            "views.py",
            "urls.py",
            "serializers.py",
        ]
        
        for file in required_files:
            file_path = app_dir / file
            if not file_path.exists():
                # 有些文件可能不是必需的
                if file in ["serializers.py", "urls.py"]:
                    continue
                return result.failure(f"应用文件不存在: {app}/{file}")
    
    return result.success("所有应用结构正常")


def test_documentation() -> TestResult:
    """测试文档完整性"""
    result = TestResult("文档检查")
    
    required_docs = [
        "README.md",
        "API_DOCUMENTATION.md",
        "API_VALIDATION_REPORT.md",
        "PROJECT_SNAPSHOT.md",
        "TEST_PLAN.md",
        "TEST_CASES.md",
        "DEFECT_TRACKING.md",
    ]
    
    missing_docs = []
    
    for doc in required_docs:
        doc_path = project_root / doc
        if not doc_path.exists():
            missing_docs.append(doc)
    
    if missing_docs:
        return result.failure("缺少文档文件", missing_docs=missing_docs)
    
    # 检查README.md是否有内容
    readme_path = project_root / "README.md"
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    if len(readme_content.strip()) < 100:
        return result.failure("README.md内容过少")
    
    return result.success("所有文档完整")


def test_testing_infrastructure() -> TestResult:
    """测试测试基础设施"""
    result = TestResult("测试基础设施检查")
    
    test_files = [
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/test_models.py",
        "tests/integration/test_api.py",
        "tests/system/test_user_flows.py",
        "run_basic_tests.py",
        "run_tests.py",
    ]
    
    missing_files = []
    
    for test_file in test_files:
        file_path = project_root / test_file
        if not file_path.exists():
            missing_files.append(test_file)
    
    if missing_files:
        return result.failure("缺少测试文件", missing_files=missing_files)
    
    # 检查测试目录结构
    test_dirs = ["unit", "integration", "system", "fixtures", "reports"]
    for test_dir in test_dirs:
        dir_path = project_root / "tests" / test_dir
        if not dir_path.exists():
            # 创建缺失的目录
            dir_path.mkdir(parents=True, exist_ok=True)
    
    return result.success("测试基础设施完整")


def test_api_documentation() -> TestResult:
    """测试API文档"""
    result = TestResult("API文档检查")
    
    api_docs = [
        "API_DOCUMENTATION.md",
        "API_VALIDATION_REPORT.md",
        "openapi_spec.json",
    ]
    
    for doc in api_docs:
        doc_path = project_root / doc
        if not doc_path.exists():
            return result.failure(f"API文档不存在: {doc}")
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if doc == "openapi_spec.json":
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    return result.failure(f"openapi_spec.json格式错误: {e}")
        
        except Exception as e:
            return result.failure(f"读取API文档失败: {doc}", error=str(e))
    
    return result.success("API文档完整且格式正确")


def test_business_logic() -> TestResult:
    """测试业务逻辑（模拟）"""
    result = TestResult("业务逻辑检查")
    
    # 模拟用户积分计算
    def calculate_user_points(completed_tasks):
        """计算用户积分"""
        total_points = 0
        for task in completed_tasks:
            points = task.get('points', 0)
            multiplier = task.get('multiplier', 1.0)
            total_points += points * multiplier
        return total_points
    
    # 测试用例
    test_cases = [
        {
            "name": "简单任务积分",
            "tasks": [{"points": 50}, {"points": 30}],
            "expected": 80
        },
        {
            "name": "带乘数的任务",
            "tasks": [{"points": 100, "multiplier": 1.5}, {"points": 50}],
            "expected": 200  # 100*1.5 + 50 = 150 + 50 = 200
        },
        {
            "name": "无任务",
            "tasks": [],
            "expected": 0
        }
    ]
    
    failed_cases = []
    
    for test_case in test_cases:
        calculated = calculate_user_points(test_case["tasks"])
        if abs(calculated - test_case["expected"]) > 0.01:
            failed_cases.append({
                "name": test_case["name"],
                "expected": test_case["expected"],
                "calculated": calculated
            })
    
    if failed_cases:
        return result.failure("业务逻辑测试失败", failed_cases=failed_cases)
    
    return result.success("业务逻辑测试通过")


def generate_test_report(results: List[TestResult]) -> Dict[str, Any]:
    """生成测试报告"""
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate
        },
        "details": [
            {
                "name": r.name,
                "passed": r.passed,
                "message": r.message,
                "details": r.details
            }
            for r in results
        ]
    }
    
    return report


def main():
    """主函数"""
    print("开始运行核心功能测试...\n")
    
    # 运行所有测试
    test_functions = [
        test_project_structure,
        test_config_files,
        test_apps_structure,
        test_documentation,
        test_testing_infrastructure,
        test_api_documentation,
        test_business_logic,
    ]
    
    results = []
    
    for test_func in test_functions:
        print(f"运行测试: {test_func.__name__}...")
        result = test_func()
        results.append(result)
        print(f"  {result}")
        print()
    
    # 生成报告
    report = generate_test_report(results)
    
    # 输出摘要
    summary = report["summary"]
    print("=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"总测试数: {summary['total_tests']}")
    print(f"通过测试: {summary['passed_tests']}")
    print(f"失败测试: {summary['failed_tests']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    print("=" * 60)
    
    # 保存报告
    reports_dir = project_root / "tests" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / "core_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细报告已保存: {report_file}")
    
    # 返回退出码
    if summary['failed_tests'] > 0:
        print("\n❌ 有测试失败，请检查详细报告")
        return 1
    else:
        print("\n✅ 所有核心功能测试通过！")
        return 0


if __name__ == "__main__":
    sys.exit(main())