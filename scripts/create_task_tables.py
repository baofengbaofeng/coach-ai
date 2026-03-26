#!/usr/bin/env python3
"""
创建任务相关表的脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from coachai_code.config import config
from coachai_code.database.models import Base, Task, TaskAssignment, TaskSubmission, TaskEvaluation


def create_task_tables():
    """创建任务相关表"""
    # 创建数据库引擎
    engine = create_engine(config.DATABASE_URL)
    
    print("正在创建任务相关表...")
    
    try:
        # 创建所有表
        Base.metadata.create_all(engine, tables=[
            Task.__table__,
            TaskAssignment.__table__,
            TaskSubmission.__table__,
            TaskEvaluation.__table__
        ])
        
        print("✅ 任务相关表创建成功！")
        print("创建的表：")
        print("  - tasks (任务表)")
        print("  - task_assignments (任务分配表)")
        print("  - task_submissions (任务提交表)")
        print("  - task_evaluations (任务评价表)")
        
        # 验证表是否创建成功
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES LIKE 'tasks'"))
            if result.fetchone():
                print("✅ tasks表验证成功")
            
            result = conn.execute(text("SHOW TABLES LIKE 'task_assignments'"))
            if result.fetchone():
                print("✅ task_assignments表验证成功")
            
            result = conn.execute(text("SHOW TABLES LIKE 'task_submissions'"))
            if result.fetchone():
                print("✅ task_submissions表验证成功")
            
            result = conn.execute(text("SHOW TABLES LIKE 'task_evaluations'"))
            if result.fetchone():
                print("✅ task_evaluations表验证成功")
                
    except Exception as e:
        print(f"❌ 创建表时出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    create_task_tables()