# coding目录清理计划

## 当前状态分析

### ✅ 已迁移完成
1. **DDD基础架构** - 完整6层结构
2. **用户领域** - 实体、值对象、服务、事件、仓库
3. **运动领域** - 核心实体和值对象（刚刚完成）
4. **基础设施** - 数据库、Redis、仓库模式
5. **应用层** - 事件总线

### ⏳ 仍需迁移
1. **任务领域** - task.py等模型文件
2. **成就领域** - achievement.py等模型文件
3. **Web应用层** - webapp/目录中的所有文件
4. **数据库基础设施** - connection.py等
5. **测试文件** - test_*.py

## 清理策略

### 方案：分阶段清理，保持可回滚

#### 第一阶段：标记已迁移文件（立即执行）
1. 在coding目录中创建`MIGRATED.md`文件，记录已迁移内容
2. 将已迁移的模型文件重命名为`*.py.migrated`
3. 保持文件存在，但不再使用

#### 第二阶段：创建迁移映射（今天完成）
1. 创建`migration_map.json`，记录旧文件到新文件的映射
2. 更新导入路径的自动化脚本
3. 验证所有导入都能正常工作

#### 第三阶段：批量迁移剩余领域（明天）
1. 迁移任务领域（task/）
2. 迁移成就领域（achievement/）
3. 迁移Web应用层（webapp/）

#### 第四阶段：最终清理（后天）
1. 运行完整测试套件
2. 删除coding目录（或重命名为coding_legacy）
3. 更新所有文档和README

## 立即执行的操作

### 1. 标记用户领域相关文件
```bash
# 用户模型已迁移
mv coding/database/models/user.py coding/database/models/user.py.migrated
mv coding/database/models/tenant.py coding/database/models/tenant.py.migrated
mv coding/database/models/permission.py coding/database/models/permission.py.migrated

# 运动模型已迁移
mv coding/database/models/exercise_type.py coding/database/models/exercise_type.py.migrated
mv coding/database/models/exercise_record.py coding/database/models/exercise_record.py.migrated
mv coding/database/models/exercise_plan.py coding/database/models/exercise_plan.py.migrated
```

### 2. 创建迁移记录
```bash
# 创建迁移记录文件
cat > coding/MIGRATED.md << 'EOF'
# 已迁移文件记录

## 迁移时间
2026-03-27

## 已迁移领域

### 用户领域
- user.py -> src/domain/user/entities_simple.py
- tenant.py -> src/domain/user/entities_simple.py
- permission.py -> src/domain/user/entities_simple.py

### 运动领域
- exercise_type.py -> src/domain/exercise/entities.py
- exercise_record.py -> src/domain/exercise/entities.py
- exercise_plan.py -> src/domain/exercise/entities.py

## 新架构位置
所有新代码位于 `src/` 目录，采用DDD架构：
- domain/ - 领域层
- application/ - 应用层
- interfaces/ - 接口层
- infrastructure/ - 基础设施层
- utils/ - 工具层
- web/ - 前端层

## 注意事项
1. 已迁移文件已重命名为 *.py.migrated
2. 请使用新架构中的代码
3. 备份位于 coding_backup/ 目录
EOF
```

### 3. 创建导入辅助工具
```python
# migration_helper.py
"""
迁移导入辅助工具
帮助将旧导入路径转换为新路径
"""

IMPORT_MAP = {
    # 用户领域
    'coding.database.models.user': 'domain.user.entities_simple.User',
    'coding.database.models.tenant': 'domain.user.entities_simple.Tenant',
    'coding.database.models.permission': 'domain.user.entities_simple.Permission',
    
    # 运动领域
    'coding.database.models.exercise_type': 'domain.exercise.entities.ExerciseType',
    'coding.database.models.exercise_record': 'domain.exercise.entities.ExerciseRecord',
    'coding.database.models.exercise_plan': 'domain.exercise.entities.ExercisePlan',
    
    # 配置
    'coding.config.config': 'settings.config',
}

def update_imports(file_path):
    """更新文件中的导入路径"""
    # 实现导入路径更新逻辑
    pass
```

## 风险控制

### 备份策略
1. **完整备份**：`coding_backup/` 目录包含原始代码
2. **版本控制**：所有更改已提交到GitHub
3. **逐步验证**：每个阶段都进行测试验证

### 回滚计划
如果出现问题，可以：
1. 恢复 `coding_backup/` 中的文件
2. 使用git回滚到之前的提交
3. 暂时使用旧架构，逐步修复问题

## 时间计划

### 今天（2026-03-27）
- [x] 完成用户领域迁移
- [x] 完成运动领域核心迁移
- [ ] 标记已迁移文件
- [ ] 创建迁移记录
- [ ] 运行基本测试

### 明天（2026-03-28）
- [ ] 迁移任务领域
- [ ] 迁移成就领域
- [ ] 开始Web层迁移
- [ ] 创建集成测试

### 后天（2026-03-29）
- [ ] 完成所有迁移
- [ ] 运行完整测试
- [ ] 清理coding目录
- [ ] 更新文档

## 验证方法

### 自动化验证
```bash
# 运行领域层测试
python -m pytest src/domain/ -v

# 运行基础设施测试
python -m pytest src/infrastructure/ -v

# 检查导入路径
python -c "import sys; sys.path.insert(0, 'src'); import domain.user; print('✅ 导入成功')"
```

### 手动验证
1. 创建用户、运动记录等实体
2. 测试业务逻辑方法
3. 验证数据库操作
4. 检查事件发布

## 总结

`coding`目录中的文件没有迁移干净是因为采用了渐进式迁移策略。目前已完成用户领域和运动领域的核心迁移，其他领域仍在旧结构中。

**建议立即执行**：
1. 标记已迁移文件，避免混淆
2. 创建迁移记录，方便团队参考
3. 继续按计划迁移剩余领域

**关键原则**：
- 保持可工作状态
- 逐步迁移，降低风险
- 充分测试，确保质量
- 完整文档，便于协作

迁移工作正在稳步推进，预计2-3天内完成所有迁移工作。