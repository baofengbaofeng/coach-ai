#!/usr/bin/env python3
"""
CoachAI迁移最终清理脚本
验证迁移完成状态并安全清理旧代码

注意：所有注释必须使用中文（规范要求）
所有日志和异常消息必须使用英文（规范要求）
"""

import os
import sys
import shutil
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class MigrationCleanup:
    """迁移清理器"""
    
    def __init__(self):
        """初始化清理器"""
        self.project_root = project_root
        self.migration_report = {}
        self.start_time = datetime.now()
        
        # 需要检查的目录
        self.directories_to_check = [
            "coding",
            "coding_backup"
        ]
        
        # 需要保留的文件模式
        self.patterns_to_keep = [
            "*.py.migrated",
            "*.sh.migrated",
            "README*",
            ".gitignore",
            ".env*"
        ]
        
        # 需要检查的迁移状态
        self.migration_status = {
            "domain_layer": False,
            "application_layer": False,
            "interface_layer": False,
            "infrastructure_layer": False,
            "web_layer": False,
            "database_config": False,
            "deployment_config": False,
            "testing_config": False,
            "documentation": False
        }
    
    def check_migration_status(self) -> bool:
        """
        检查迁移状态
        
        返回:
            bool: 迁移是否完成
        """
        print("=" * 80)
        print("CoachAI Migration Status Check")
        print("=" * 80)
        print(f"Project Root: {self.project_root}")
        print(f"Check Time: {self.start_time}")
        print()
        
        all_passed = True
        
        # 检查DDD架构完整性
        print("1. Checking DDD Architecture Integrity...")
        ddd_checks = [
            ("Domain Layer", self.check_domain_layer),
            ("Application Layer", self.check_application_layer),
            ("Interface Layer", self.check_interface_layer),
            ("Infrastructure Layer", self.check_infrastructure_layer),
            ("Web Layer", self.check_web_layer)
        ]
        
        for check_name, check_func in ddd_checks:
            try:
                passed = check_func()
                status_icon = "✅" if passed else "❌"
                print(f"   {status_icon} {check_name}: {'PASSED' if passed else 'FAILED'}")
                
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: ERROR - {e}")
                all_passed = False
        
        # 检查配置迁移
        print("\n2. Checking Configuration Migration...")
        config_checks = [
            ("Database Configuration", self.check_database_config),
            ("Deployment Configuration", self.check_deployment_config),
            ("Testing Configuration", self.check_testing_config)
        ]
        
        for check_name, check_func in config_checks:
            try:
                passed = check_func()
                status_icon = "✅" if passed else "❌"
                print(f"   {status_icon} {check_name}: {'PASSED' if passed else 'FAILED'}")
                
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: ERROR - {e}")
                all_passed = False
        
        # 检查文档完整性
        print("\n3. Checking Documentation...")
        try:
            doc_passed = self.check_documentation()
            status_icon = "✅" if doc_passed else "❌"
            print(f"   {status_icon} Documentation: {'PASSED' if doc_passed else 'FAILED'}")
            
            if not doc_passed:
                all_passed = False
        except Exception as e:
            print(f"   ❌ Documentation: ERROR - {e}")
            all_passed = False
        
        # 检查旧代码目录
        print("\n4. Checking Legacy Code Directories...")
        legacy_checks = [
            ("coding/ Directory", self.check_coding_directory),
            ("coding_backup/ Directory", self.check_coding_backup_directory)
        ]
        
        for check_name, check_func in legacy_checks:
            try:
                status = check_func()
                if status == "ready_for_cleanup":
                    print(f"   ✅ {check_name}: READY FOR CLEANUP")
                elif status == "already_cleaned":
                    print(f"   ✅ {check_name}: ALREADY CLEANED")
                elif status == "not_ready":
                    print(f"   ⚠️  {check_name}: NOT READY - Contains non-migrated files")
                    all_passed = False
                elif status == "not_found":
                    print(f"   ✅ {check_name}: NOT FOUND (already cleaned)")
                else:
                    print(f"   ❓ {check_name}: UNKNOWN STATUS")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: ERROR - {e}")
                all_passed = False
        
        # 生成迁移报告
        self.generate_migration_report(all_passed)
        
        return all_passed
    
    def check_domain_layer(self) -> bool:
        """检查领域层完整性"""
        domain_dir = self.project_root / "src" / "domain"
        
        if not domain_dir.exists():
            return False
        
        # 检查核心领域
        required_domains = ["user", "task", "exercise", "achievement"]
        for domain in required_domains:
            domain_path = domain_dir / domain
            if not domain_path.exists():
                return False
            
            # 检查领域文件
            required_files = ["__init__.py", "entities.py", "value_objects.py", "services.py", "events.py"]
            for file in required_files:
                file_path = domain_path / file
                simplified_file = domain_path / file.replace(".py", "_simple.py")
                if not file_path.exists() and not simplified_file.exists():
                    return False
        
        self.migration_status["domain_layer"] = True
        return True
    
    def check_application_layer(self) -> bool:
        """检查应用层完整性"""
        app_dir = self.project_root / "src" / "application"
        
        if not app_dir.exists():
            return False
        
        # 检查应用服务
        services_dir = app_dir / "services"
        if not services_dir.exists():
            return False
        
        # 检查核心服务
        required_services = ["auth_service.py", "task_service_simple.py", 
                           "exercise_service_simple.py", "achievement_service_simple.py",
                           "tenant_service.py"]
        
        for service in required_services:
            service_path = services_dir / service
            if not service_path.exists():
                return False
        
        # 检查事件总线
        events_dir = app_dir / "events"
        if not events_dir.exists():
            return False
        
        bus_file = events_dir / "bus.py"
        if not bus_file.exists():
            return False
        
        self.migration_status["application_layer"] = True
        return True
    
    def check_interface_layer(self) -> bool:
        """检查接口层完整性"""
        interfaces_dir = self.project_root / "src" / "interfaces"
        
        if not interfaces_dir.exists():
            return False
        
        # 检查API接口
        api_dir = interfaces_dir / "api"
        if not api_dir.exists():
            return False
        
        # 检查API版本
        v1_dir = api_dir / "v1"
        if not v1_dir.exists():
            return False
        
        # 检查核心API模块
        required_modules = ["auth", "task", "exercise", "achievement", "user"]
        for module in required_modules:
            module_path = v1_dir / module
            if not module_path.exists():
                return False
            
            # 检查处理器和路由
            handlers_file = module_path / "handlers.py"
            routes_file = module_path / "routes.py"
            
            if not handlers_file.exists() and module != "user":
                return False
            if not routes_file.exists() and module != "user":
                return False
        
        self.migration_status["interface_layer"] = True
        return True
    
    def check_infrastructure_layer(self) -> bool:
        """检查基础设施层完整性"""
        infra_dir = self.project_root / "src" / "infrastructure"
        
        if not infra_dir.exists():
            return False
        
        # 检查数据库
        db_dir = infra_dir / "db"
        if not db_dir.exists():
            return False
        
        connection_file = db_dir / "connection.py"
        if not connection_file.exists():
            return False
        
        # 检查缓存
        cache_dir = infra_dir / "cache"
        if not cache_dir.exists():
            return False
        
        redis_file = cache_dir / "redis_client.py"
        if not redis_file.exists():
            return False
        
        # 检查安全
        security_dir = infra_dir / "security"
        if not security_dir.exists():
            return False
        
        required_security_files = ["jwt_utils.py", "password_utils.py"]
        for file in required_security_files:
            file_path = security_dir / file
            if not file_path.exists():
                return False
        
        self.migration_status["infrastructure_layer"] = True
        return True
    
    def check_web_layer(self) -> bool:
        """检查Web层完整性"""
        web_dir = self.project_root / "src" / "interfaces" / "web"
        
        if not web_dir.exists():
            return False
        
        # 检查核心Web文件
        required_files = ["application.py", "base_handler.py", "error_handler.py", "middleware.py"]
        for file in required_files:
            file_path = web_dir / file
            if not file_path.exists():
                return False
        
        self.migration_status["web_layer"] = True
        return True
    
    def check_database_config(self) -> bool:
        """检查数据库配置"""
        # 检查数据库连接文件
        db_connection = self.project_root / "src" / "infrastructure" / "db" / "connection.py"
        if not db_connection.exists():
            return False
        
        # 检查主入口文件
        main_file = self.project_root / "src" / "main.py"
        if not main_file.exists():
            return False
        
        self.migration_status["database_config"] = True
        return True
    
    def check_deployment_config(self) -> bool:
        """检查部署配置"""
        # 检查Docker配置
        docker_files = ["Dockerfile", "docker-compose.yml"]
        for file in docker_files:
            file_path = self.project_root / file
            if not file_path.exists():
                return False
        
        # 检查部署脚本
        deploy_script = self.project_root / "scripts" / "deploy.sh"
        if not deploy_script.exists():
            return False
        
        # 检查环境配置
        env_example = self.project_root / ".env.example"
        if not env_example.exists():
            return False
        
        self.migration_status["deployment_config"] = True
        return True
    
    def check_testing_config(self) -> bool:
        """检查测试配置"""
        # 检查测试目录
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return False
        
        # 检查DDD测试配置
        ddd_conftest = tests_dir / "ddd_conftest.py"
        if not ddd_conftest.exists():
            return False
        
        # 检查测试运行器
        test_runner = self.project_root / "scripts" / "run_tests.py"
        if not test_runner.exists():
            return False
        
        self.migration_status["testing_config"] = True
        return True
    
    def check_documentation(self) -> bool:
        """检查文档完整性"""
        docs_dir = self.project_root / "docs"
        
        if not docs_dir.exists():
            return False
        
        # 检查核心文档
        required_docs = ["API_DOCUMENTATION.md", "DEPLOYMENT_GUIDE.md", "MIGRATION_SUMMARY.md"]
        for doc in required_docs:
            doc_path = docs_dir / doc
            if not doc_path.exists():
                return False
        
        self.migration_status["documentation"] = True
        return True
    
    def check_coding_directory(self) -> str:
        """
        检查coding目录状态
        
        返回:
            str: 目录状态
        """
        coding_dir = self.project_root / "coding"
        
        if not coding_dir.exists():
            return "not_found"
        
        # 检查目录内容
        items = list(coding_dir.rglob("*"))
        
        if not items:
            return "already_cleaned"
        
        # 检查文件状态
        non_migrated_files = []
        for item in items:
            if item.is_file():
                # 检查是否为已迁移文件
                if not any(item.name.endswith(pattern.replace("*", "")) for pattern in self.patterns_to_keep):
                    # 检查是否为Python文件
                    if item.suffix == ".py" and not item.name.endswith(".migrated"):
                        non_migrated_files.append(str(item.relative_to(self.project_root)))
        
        if non_migrated_files:
            print(f"     Non-migrated files found: {len(non_migrated_files)}")
            for file in non_migrated_files[:5]:  # 只显示前5个
                print(f"       - {file}")
            if len(non_migrated_files) > 5:
                print(f"       ... and {len(non_migrated_files) - 5} more")
            return "not_ready"
        
        return "ready_for_cleanup"
    
    def check_coding_backup_directory(self) -> str:
        """
        检查coding_backup目录状态
        
        返回:
            str: 目录状态
        """
        backup_dir = self.project_root / "coding_backup"
        
        if not backup_dir.exists():
            return "not_found"
        
        # 检查目录内容
        items = list(backup_dir.rglob("*"))
        
        if not items:
            return "already_cleaned"
        
        # 对于备份目录，只要存在就可以清理
        return "ready_for_cleanup"
    
    def generate_migration_report(self, all_passed: bool) -> None:
        """生成迁移报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        report_data = {
            "project": "CoachAI",
            "check_time": self.start_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "overall_status": "passed" if all_passed else "failed",
            "migration_status": self.migration_status,
            "summary": {
                "total_checks": len(self.migration_status),
                "passed_checks": sum(1 for status in self.migration_status.values() if status),
                "failed_checks": sum(1 for status in self.migration_status.values() if not status)
            },
            "recommendations": []
        }
        
        # 添加建议
        if all_passed:
            report_data["recommendations"].append("All checks passed. Ready for final cleanup.")
        else:
            report_data["recommendations"].append("Some checks failed. Please fix issues before cleanup.")
        
        # 保存报告
        reports_dir = self.project_root / "migration-reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"migration-check-{self.start_time.strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nMigration check report saved to: {report_file}")
    
    def perform_cleanup(self, dry_run: bool = True) -> bool:
        """
        执行清理操作
        
        参数:
            dry_run: 是否为干运行（只显示，不实际执行）
            
        返回:
            bool: 清理是否成功
        """
        print("\n" + "=" * 80)
        print("CoachAI Migration Cleanup")
        print("=" * 80)
        
        if dry_run:
            print("DRY RUN MODE: No files will be deleted")
        else:
            print("LIVE MODE: Files will be deleted")
        
        print()
        
        # 检查迁移状态
        migration_passed = self.check_migration_status()
        
        if not migration_passed:
            print("\n❌ Migration not complete. Cannot proceed with cleanup.")
            print("Please fix the migration issues first.")
            return False
        
        # 确认清理
        if not dry_run:
            confirmation = input("\n⚠️  WARNING: This will DELETE legacy code directories. Continue? (yes/no): ")
            if confirmation.lower() != "yes":
                print("Cleanup cancelled.")
                return False
        
        # 执行清理
        directories_to_clean = []
        
        # 检查coding目录
        coding_status = self.check_coding_directory()
        if coding_status == "ready_for_cleanup":
            directories_to_clean.append(("coding", self.project_root / "coding"))
        elif coding_status == "not_ready":
            print("❌ coding/ directory not ready for cleanup.")
            return False
        
        # 检查coding_backup目录
        backup_status = self.check_coding_backup_directory()
        if backup_status == "ready_for_cleanup":
            directories_to_clean.append(("coding_backup", self.project_root / "coding_backup"))
        
        if not directories_to_clean:
            print("✅ No directories need cleanup.")
            return True
        
        # 执行清理
        print(f"\nDirectories to clean: {len(directories_to_clean)}")
        
        for dir_name, dir_path in directories_to_clean:
            print(f"\nCleaning {dir_name}/...")
            
            if dry_run:
                # 干运行：显示将要删除的内容
                items = list(dir_path.rglob("*"))
                print(f"  Would delete: {len(items)} items")
                
                # 显示前10个文件/目录
                for i, item in enumerate(items[:10]):
                    item_type = "DIR" if item.is_dir() else "FILE"
                    print(f"    {item_type}: {item.relative_to(self.project_root)}")
                
                if len(items) > 10:
                    print(f"    ... and {len(items) - 10} more items")
            else:
                # 实际执行：删除目录
                try:
                    shutil.rmtree(dir_path)
                    print(f"  ✅ Deleted: {dir_path}")
                except Exception as e:
                    print(f"  ❌ Failed to delete {dir_path}: {e}")
                    return False
        
        if dry_run:
            print("\n✅ Dry run completed. No files were deleted.")
            print("To actually delete files, run with --execute flag.")
        else:
            print("\n✅ Cleanup completed successfully!")
            print("Legacy code directories have been removed.")
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CoachAI Migration Cleanup Tool")
    parser.add_argument("--execute", action="store_true", help="Actually delete files (dry run by default)")
    parser.add_argument("--check-only", action="store_true", help="Only check migration status, don't clean")
    
    args = parser.parse_args()
    
    try:
        cleanup = MigrationCleanup()
        
        if args.check_only:
            # 只检查状态
            passed = cleanup.check_migration_status()
            
            if passed:
                print("\n✅ Migration check PASSED. Ready for cleanup.")
                print("Run with --execute to perform cleanup.")
            else:
                print("\n❌ Migration check FAILED. Please fix issues before cleanup.")
            
            sys.exit(0 if passed else 1)
        else:
            # 执行清理（干运行或实际运行）
            dry_run = not args.execute
            success = cleanup.perform_cleanup(dry_run=dry_run)
            
            if success and not dry_run:
                print("\n🎉 Migration cleanup COMPLETED!")
                print("CoachAI project is now fully migrated to DDD architecture.")
                print("Legacy code directories have been removed.")
            
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleanup interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()