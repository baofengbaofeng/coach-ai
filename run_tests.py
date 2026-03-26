#!/usr/bin/env python3
"""
测试运行脚本。
用于运行所有测试并生成测试报告。
"""
import os
import sys
import json
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "apps"))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django
django.setup()

from django.conf import settings


class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # 创建报告目录
        self.reports_dir = project_root / "tests" / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # 创建覆盖率目录
        self.coverage_dir = self.reports_dir / "coverage"
        self.coverage_dir.mkdir(exist_ok=True)
        
        # 创建性能测试目录
        self.performance_dir = self.reports_dir / "performance"
        self.performance_dir.mkdir(exist_ok=True)
        
        # 创建安全测试目录
        self.security_dir = self.reports_dir / "security"
        self.security_dir.mkdir(exist_ok=True)
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """运行单元测试"""
        print("\n" + "="*60)
        print("运行单元测试")
        print("="*60)
        
        test_files = [
            "tests/unit/test_models.py",
        ]
        
        results = {}
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                print(f"\n运行: {test_file}")
                result = self._run_pytest_test(file_path)
                results[test_file] = result
            else:
                print(f"⚠️  测试文件不存在: {test_file}")
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """运行集成测试"""
        print("\n" + "="*60)
        print("运行集成测试")
        print("="*60)
        
        test_files = [
            "tests/integration/test_api.py",
        ]
        
        results = {}
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                print(f"\n运行: {test_file}")
                result = self._run_pytest_test(file_path)
                results[test_file] = result
            else:
                print(f"⚠️  测试文件不存在: {test_file}")
        
        return results
    
    def run_system_tests(self) -> Dict[str, Any]:
        """运行系统测试"""
        print("\n" + "="*60)
        print("运行系统测试")
        print("="*60)
        
        test_files = [
            "tests/system/test_user_flows.py",
        ]
        
        results = {}
        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                print(f"\n运行: {test_file}")
                result = self._run_pytest_test(file_path)
                results[test_file] = result
            else:
                print(f"⚠️  测试文件不存在: {test_file}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("\n" + "="*60)
        print("开始运行所有测试")
        print("="*60)
        
        self.start_time = datetime.datetime.now()
        
        # 运行不同层次的测试
        unit_results = self.run_unit_tests()
        integration_results = self.run_integration_tests()
        system_results = self.run_system_tests()
        
        self.end_time = datetime.datetime.now()
        
        # 汇总结果
        all_results = {
            "unit_tests": unit_results,
            "integration_tests": integration_results,
            "system_tests": system_results,
            "summary": self._generate_summary(unit_results, integration_results, system_results)
        }
        
        self.test_results = all_results
        
        # 生成报告
        self._generate_test_report(all_results)
        
        return all_results
    
    def _run_pytest_test(self, test_file: Path) -> Dict[str, Any]:
        """运行单个pytest测试文件"""
        try:
            # 使用pytest运行测试
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_file),
                "-v",
                "--tb=short",
                f"--html={self.reports_dir}/pytest_report.html",
                f"--cov={self.project_root}/apps",
                f"--cov={self.project_root}/services",
                f"--cov={self.project_root}/core",
                f"--cov-report=html:{self.coverage_dir}",
                f"--cov-report=term"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
        except Exception as e:
            return {
                "exit_code": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    def _generate_summary(self, unit_results: Dict, integration_results: Dict, system_results: Dict) -> Dict[str, Any]:
        """生成测试摘要"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        # 统计单元测试
        for result in unit_results.values():
            if result.get("success"):
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1
        
        # 统计集成测试
        for result in integration_results.values():
            if result.get("success"):
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1
        
        # 统计系统测试
        for result in system_results.values():
            if result.get("success"):
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1
        
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "duration_seconds": duration,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _generate_test_report(self, results: Dict[str, Any]):
        """生成测试报告"""
        print("\n" + "="*60)
        print("生成测试报告")
        print("="*60)
        
        # 生成JSON报告
        report_file = self.reports_dir / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 生成HTML报告
        html_report = self._generate_html_report(results)
        html_file = self.reports_dir / "test_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # 生成Markdown报告
        md_report = self._generate_markdown_report(results)
        md_file = self.reports_dir / "test_report.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        print(f"✅ JSON报告已生成: {report_file}")
        print(f"✅ HTML报告已生成: {html_file}")
        print(f"✅ Markdown报告已生成: {md_file}")
        
        # 打印摘要
        summary = results["summary"]
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"耗时: {summary['duration_seconds']:.1f}秒")
        print("="*60)
        
        if summary['failed_tests'] > 0:
            print("❌ 有测试失败，请检查详细报告")
            return False
        else:
            print("✅ 所有测试通过！")
            return True
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """生成HTML测试报告"""
        summary = results["summary"]
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coach AI 测试报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-item {{
            text-align: center;
            padding: 15px;
            border-radius: 6px;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .summary-item.total {{
            border-top: 4px solid #007bff;
        }}
        .summary-item.passed {{
            border-top: 4px solid #28a745;
        }}
        .summary-item.failed {{
            border-top: 4px solid #dc3545;
        }}
        .summary-item.duration {{
            border-top: 4px solid #ffc107;
        }}
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .test-section {{
            margin-bottom: 30px;
        }}
        .test-section h3 {{
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
        }}
        .test-results {{
            margin-top: 15px;
        }}
        .test-result {{
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 4px solid #ccc;
        }}
        .test-result.success {{
            background-color: #d4edda;
            border-left-color: #28a745;
        }}
        .test-result.failure {{
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Coach AI 测试报告</h1>
            <p>智能教练系统 - 质量保证报告</p>
        </div>
        
        <div class="summary">
            <h2>测试摘要</h2>
            <div class="summary-grid">
                <div class="summary-item total">
                    <div class="summary-label">总测试数</div>
                    <div class="summary-value">{summary['total_tests']}</div>
                </div>
                <div class="summary-item passed">
                    <div class="summary-label">通过测试</div>
                    <div class="summary-value">{summary['passed_tests']}</div>
                </div>
                <div class="summary-item failed">
                    <div class="summary-label">失败测试</div>
                    <div class="summary-value">{summary['failed_tests']}</div>
                </div>
                <div class="summary-item duration">
                    <div class="summary-label">成功率</div>
                    <div class="summary-value">{summary['success_rate']:.1f}%</div>
                </div>
            </div>
            <p style="margin-top: 20px; text-align: center;">
                测试耗时: {summary['duration_seconds']:.1f}秒
            </p>
        </div>
        
        <div class="test-section">
            <h3>单元测试结果</h3>
            <div class="test-results">
"""
        
        # 添加单元测试结果
        for test_file, result in results.get("unit_tests", {}).items():
            status_class = "success" if result.get("success") else "failure"
            status_text = "✅ 通过" if result.get("success") else "❌ 失败"
            html += f"""
                <div class="test-result {status_class}">
                    <strong>{test_file}</strong> - {status_text}
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <div class="test-section">
            <h3>集成测试结果</h3>
            <div class="test-results">
"""
        
        # 添加集成测试结果
        for test_file, result in results.get("integration_tests", {}).items():
            status_class = "success" if result.get("success") else "failure"
            status_text = "✅ 通过" if result.get("success") else "❌ 失败"
            html += f"""
                <div class="test-result {status_class}">
                    <strong>{test_file}</strong> - {status_text}
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <div class="test-section">
            <h3>系统测试结果</h3>
            <div class="test-results">
"""
        
        # 添加系统测试结果
        for test_file, result in results.get("system_tests", {}).items():
            status_class = "success" if result.get("success") else "failure"
            status_text = "✅ 通过" if result.get("success") else "❌ 失败"
            html += f"""
                <div class="test-result {status_class}">
                    <strong>{test_file}</strong> - {status_text}
                </div>
"""
        
        html += f"""
            </div>
        </div>
        
        <div class="timestamp">
            报告生成时间: {summary['timestamp']}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """生成Markdown测试报告"""
        summary = results["summary"]
        
        md = f"""# Coach AI 测试报告

## 报告概述

- **生成时间**: {summary['timestamp']}
- **测试耗时**: {summary['duration_seconds']:.1f}秒
- **测试环境**: {settings.ENVIRONMENT}

## 测试摘要

| 指标 | 结果 |
|------|------|
| 总测试数 | {summary['total_tests']} |
| 通过测试 | {summary['passed_tests']} |
| 失败测试 | {summary['failed_tests']} |
| 成功率 | {summary['success_rate']:.1f}% |

## 详细结果

### 单元测试

"""
        
        # 添加单元测试结果
        for test_file, result in results.get("unit_tests", {}).items():
            status = "✅ 通过" if result.get("success") else "❌ 失败"
            md += f"- **{test_file}**: {status}\n"
        
        md += "\n### 集成测试\n\n"
        
        # 添加集成测试结果
        for test_file, result in results.get("integration_tests", {}).items():
            status = "✅ 通过" if result.get("success") else "❌ 失败"
            md += f"- **{test_file}**: {status}\n"
        
        md += "\n### 系统测试\n\n"
        
        # 添加系统测试结果
        for test_file, result in results.get("system_tests", {}).items():
            status = "✅ 通过" if result.get("success") else "❌ 失败"
            md += f"- **{test_file}**: {status}\n"
        
        md += f"""
## 结论

{self._generate_conclusion(summary)}

## 建议

1. 查看详细覆盖率报告: `tests/reports/coverage/index.html`
2. 查看pytest详细报告: `tests/reports/pytest_report.html`
3. 对于失败的测试，请检查对应的测试文件

---

*报告由 Coach AI 测试框架自动生成*
"""
        
        return md
    
    def _generate_conclusion(self, summary: Dict[str, Any]) -> str:
        """生成结论"""
        if summary['total_tests'] == 0:
            return "⚠️ 未运行任何测试。"
        elif summary['failed_tests'] == 0:
            return "✅ 所有测试通过！系统质量良好，可以继续进行前端开发。"
        elif summary['success_rate'] >= 80:
            return f"⚠️ 测试通过率 {summary['success_rate']:.1f}%，大部分功能正常，但需要修复失败的测试。"
        else:
            return f"❌ 测试通过率 {summary['success_rate']:.1f}%，需要重点关注并修复失败的测试。"


def main():
    """主函数"""
    print("Coach AI 测试框架")
    print("=" * 60)
    
    runner = TestRunner()
    
    try:
        # 运行所有测试
        results = runner.run_all_tests()
        
        # 根据测试结果返回适当的退出码
        summary = results["summary"]
        if summary['failed_tests'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()