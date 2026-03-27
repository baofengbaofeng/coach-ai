#!/usr/bin/env python3
"""
CoachAI测试运行脚本
运行所有测试套件并生成测试报告

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import sys
import os
import subprocess
import json
import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.project_root = project_root
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # 测试配置
        self.test_config = {
            "unit_tests": {
                "path": "src/tests/unit",
                "pattern": "test_*.py",
                "marker": "unit"
            },
            "integration_tests": {
                "path": "src/tests/integration",
                "pattern": "test_*.py",
                "marker": "integration"
            },
            "ddd_unit_tests": {
                "path": "src/tests/ddd/unit",
                "pattern": "test_*.py",
                "marker": "ddd_unit"
            },
            "ddd_integration_tests": {
                "path": "src/tests/ddd/integration",
                "pattern": "test_*.py",
                "marker": "ddd_integration"
            },
            "api_tests": {
                "path": "src/tests/integration",
                "pattern": "test_api_*.py",
                "marker": "api"
            }
        }
    
    def run_all_tests(self) -> bool:
        """
        运行所有测试
        
        返回:
            bool: 所有测试是否通过
        """
        print("=" * 80)
        print("CoachAI Test Suite Runner")
        print("=" * 80)
        print(f"Project Root: {self.project_root}")
        print(f"Start Time: {datetime.datetime.now()}")
        print()
        
        self.start_time = datetime.datetime.now()
        
        # 运行各类型测试
        test_suites = [
            ("DDD Domain Unit Tests", self.run_ddd_domain_tests),
            ("DDD Application Unit Tests", self.run_ddd_application_tests),
            ("DDD API Integration Tests", self.run_ddd_api_tests),
            ("Legacy Unit Tests", self.run_legacy_unit_tests),
            ("Legacy Integration Tests", self.run_legacy_integration_tests),
            ("Legacy API Tests", self.run_legacy_api_tests)
        ]
        
        all_passed = True
        
        for suite_name, test_function in test_suites:
            print(f"\n{'=' * 40}")
            print(f"Running: {suite_name}")
            print(f"{'=' * 40}")
            
            try:
                passed = test_function()
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ Error running {suite_name}: {e}")
                all_passed = False
        
        self.end_time = datetime.datetime.now()
        
        # 生成测试报告
        self.generate_test_report(all_passed)
        
        return all_passed
    
    def run_ddd_domain_tests(self) -> bool:
        """
        运行DDD领域层测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running DDD Domain Layer Tests...")
        
        test_file = self.project_root / "tests" / "ddd" / "unit" / "test_ddd_domain.py"
        
        if not test_file.exists():
            print("⚠️  DDD domain tests not found, skipping...")
            return True
        
        try:
            # 直接运行测试文件
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print("✅ DDD Domain Tests PASSED")
                self.test_results["ddd_domain"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ DDD Domain Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["ddd_domain"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ DDD Domain Tests TIMEOUT")
            self.test_results["ddd_domain"] = {
                "status": "timeout",
                "error": "Test execution timeout (5 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ DDD Domain Tests ERROR: {e}")
            self.test_results["ddd_domain"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def run_ddd_application_tests(self) -> bool:
        """
        运行DDD应用层测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running DDD Application Layer Tests...")
        
        test_file = self.project_root / "tests" / "ddd" / "unit" / "test_ddd_application.py"
        
        if not test_file.exists():
            print("⚠️  DDD application tests not found, skipping...")
            return True
        
        try:
            # 直接运行测试文件
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print("✅ DDD Application Tests PASSED")
                self.test_results["ddd_application"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ DDD Application Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["ddd_application"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ DDD Application Tests TIMEOUT")
            self.test_results["ddd_application"] = {
                "status": "timeout",
                "error": "Test execution timeout (5 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ DDD Application Tests ERROR: {e}")
            self.test_results["ddd_application"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def run_ddd_api_tests(self) -> bool:
        """
        运行DDD API集成测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running DDD API Integration Tests...")
        
        test_file = self.project_root / "tests" / "ddd" / "integration" / "test_ddd_api.py"
        
        if not test_file.exists():
            print("⚠️  DDD API tests not found, skipping...")
            return True
        
        try:
            # 直接运行测试文件
            result = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print("✅ DDD API Tests PASSED")
                self.test_results["ddd_api"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ DDD API Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["ddd_api"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ DDD API Tests TIMEOUT")
            self.test_results["ddd_api"] = {
                "status": "timeout",
                "error": "Test execution timeout (5 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ DDD API Tests ERROR: {e}")
            self.test_results["ddd_api"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def run_legacy_unit_tests(self) -> bool:
        """
        运行传统单元测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running Legacy Unit Tests...")
        
        test_path = self.project_root / "tests" / "unit"
        
        if not test_path.exists():
            print("⚠️  Legacy unit tests not found, skipping...")
            return True
        
        try:
            # 使用pytest运行测试
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    str(test_path),
                    "-v",
                    "--tb=short",
                    "-m", "unit",
                    "--junitxml=test-reports/unit-tests.xml"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Legacy Unit Tests PASSED")
                self.test_results["legacy_unit"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ Legacy Unit Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["legacy_unit"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Legacy Unit Tests TIMEOUT")
            self.test_results["legacy_unit"] = {
                "status": "timeout",
                "error": "Test execution timeout (10 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ Legacy Unit Tests ERROR: {e}")
            self.test_results["legacy_unit"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def run_legacy_integration_tests(self) -> bool:
        """
        运行传统集成测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running Legacy Integration Tests...")
        
        test_path = self.project_root / "tests" / "integration"
        
        if not test_path.exists():
            print("⚠️  Legacy integration tests not found, skipping...")
            return True
        
        try:
            # 使用pytest运行测试
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    str(test_path),
                    "-v",
                    "--tb=short",
                    "-m", "integration",
                    "--junitxml=test-reports/integration-tests.xml"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Legacy Integration Tests PASSED")
                self.test_results["legacy_integration"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ Legacy Integration Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["legacy_integration"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Legacy Integration Tests TIMEOUT")
            self.test_results["legacy_integration"] = {
                "status": "timeout",
                "error": "Test execution timeout (10 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ Legacy Integration Tests ERROR: {e}")
            self.test_results["legacy_integration"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def run_legacy_api_tests(self) -> bool:
        """
        运行传统API测试
        
        返回:
            bool: 测试是否通过
        """
        print("Running Legacy API Tests...")
        
        test_path = self.project_root / "tests" / "integration"
        
        if not test_path.exists():
            print("⚠️  Legacy API tests not found, skipping...")
            return True
        
        try:
            # 使用pytest运行测试
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    str(test_path),
                    "-v",
                    "--tb=short",
                    "-m", "api",
                    "--junitxml=test-reports/api-tests.xml"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print("✅ Legacy API Tests PASSED")
                self.test_results["legacy_api"] = {
                    "status": "passed",
                    "output": result.stdout
                }
                return True
            else:
                print("❌ Legacy API Tests FAILED")
                print(f"Error output:\n{result.stderr}")
                self.test_results["legacy_api"] = {
                    "status": "failed",
                    "output": result.stdout,
                    "error": result.stderr
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Legacy API Tests TIMEOUT")
            self.test_results["legacy_api"] = {
                "status": "timeout",
                "error": "Test execution timeout (10 minutes)"
            }
            return False
        except Exception as e:
            print(f"❌ Legacy API Tests ERROR: {e}")
            self.test_results["legacy_api"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def generate_test_report(self, all_passed: bool) -> None:
        """
        生成测试报告
        
        参数:
            all_passed: 所有测试是否通过
        """
        print("\n" + "=" * 80)
        print("TEST REPORT")
        print("=" * 80)
        
        duration = self.end_time - self.start_time if self.end_time and self.start_time else None
        
        # 统计测试结果
        passed_count = sum(1 for result in self.test_results.values() if result.get("status") == "passed")
        failed_count = sum(1 for result in self.test_results.values() if result.get("status") in ["failed", "error", "timeout"])
        total_count = len(self.test_results)
        
        print(f"\nTest Summary:")
        print(f"  Total Test Suites: {total_count}")
        print(f"  Passed: {passed_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Duration: {duration}")
        
        print(f"\nDetailed Results:")
        for suite_name, result in self.test_results.items():
            status = result.get("status", "unknown")
            status_icon = "✅" if status == "passed" else "❌"
            print(f"  {status_icon} {suite_name}: {status.upper()}")
        
        print(f"\nOverall Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        # 生成JSON报告
        report_data = {
            "project": "CoachAI",
            "timestamp": datetime.datetime.now().isoformat(),
            "duration_seconds": duration.total_seconds() if duration else None,
            "overall_status": "passed" if all_passed else "failed",
            "test_suites": self.test_results,
            "summary": {
                "total": total_count,
                "passed": passed_count,
                "failed": failed_count
            }
        }
        
        # 保存报告
        reports_dir = self.project_root / "test-reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"test-report-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nTest report saved to: {report_file}")
        
        # 生成简化的Markdown报告
        markdown_file = reports_dir / "TEST-REPORT.md"
        self.generate_markdown_report(markdown_file, report_data)
        
        print(f"Markdown report saved to: {markdown_file}")
    
    def generate_markdown_report(self, filepath: Path, report_data: Dict) -> None:
        """
        生成Markdown格式的测试报告
        
        参数:
            filepath: 报告文件路径
            report_data: 报告数据
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# CoachAI Test Report\n\n")
            f.write(f"**Generated:** {report_data['timestamp']}\n")
            f.write(f"**Duration:** {report_data['duration_seconds']:.2f} seconds\n")
            f.write(f"**Overall Status:** {report_data['overall_status'].upper()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Test Suites:** {report_data['summary']['total']}\n")
            f.write(f"- **Passed:** {report_data['summary']['passed']}\n")
            f.write(f"- **Failed:** {report_data['summary']['failed']}\n\n")
            
            f.write("## Test Suite Results\n\n")
            for suite_name, result in report_data['test_suites'].items():
                status = result.get('status', 'unknown')
                status_icon = "✅" if status == "passed" else "❌"
                f.write(f"### {status_icon} {suite_name.replace('_', ' ').title()}\n")
                f.write(f"- **Status:** {status.upper()}\n")
                
                if 'error' in result:
                    f.write(f"- **Error:** {result['error'][:200]}...\n")
                
                f.write("\n")
            
            f.write("## Next Steps\n\n")
            if report_data['overall_status'] == 'passed':
                f.write("✅ All tests passed! The application is ready for deployment.\n")
            else:
                f.write("❌ Some tests failed. Please review the failed test suites and fix the issues.\n")
                f.write("\nRecommended actions:\n")
                f.write("1. Review the error messages in the detailed test output\n")
                f.write("2. Check the test configuration and environment setup\n")
                f.write("3. Run individual test suites to isolate the issues\n")
                f.write("4. Fix the failing tests and run the full test suite again\n")


def main():
    """主函数"""
    try:
        runner = TestRunner()
        all_passed = runner.run_all_tests()
        
        if all_passed:
            print("\n🎉 All tests passed! CoachAI is ready for deployment.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please review the test report.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()