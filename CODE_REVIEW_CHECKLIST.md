# Coach AI 项目代码审查 Checklist

## 📋 使用说明

本Checklist用于指导代码审查过程，确保代码质量符合项目规范。每次代码审查都应使用此Checklist。

## 🎯 审查流程

### 1. 审查前准备
- [ ] 了解代码变更的背景和目的
- [ ] 查看相关需求文档
- [ ] 确认测试环境可用

### 2. 代码审查（按优先级）

## 🔴 高优先级（必须通过）

### 安全性
- [ ] 无硬编码敏感信息（密码、密钥、Token）
- [ ] 用户输入经过验证和转义
- [ ] 无SQL注入风险（使用ORM或参数化查询）
- [ ] 输出内容经过编码（防XSS）
- [ ] 权限检查完整（用户只能访问授权资源）
- [ ] 无高危函数调用（eval, exec, os.system等）

### 功能正确性
- [ ] 功能实现符合需求
- [ ] 边界条件处理完善
- [ ] 错误处理机制完整
- [ ] 接口设计合理易用
- [ ] 业务逻辑正确

### 代码规范
- [ ] 无语法错误
- [ ] 类型注解完整
- [ ] 文档字符串规范
- [ ] 命名符合规范
- [ ] 行长度不超过120字符
- [ ] 无魔法数字（使用常量定义）

## 🟡 中优先级（建议通过）

### 代码质量
- [ ] 函数职责单一（不超过50行）
- [ ] 代码结构清晰
- [ ] 无重复代码
- [ ] 复杂度合理（圈复杂度<10）
- [ ] 注释充分（复杂逻辑有解释）

### 性能
- [ ] 无N+1查询问题
- [ ] 循环内无数据库/IO操作
- [ ] 使用适当的缓存策略
- [ ] 内存使用合理
- [ ] 响应时间可接受

### 可维护性
- [ ] 模块划分合理
- [ ] 依赖关系清晰
- [ ] 配置可管理
- [ ] 日志记录完整
- [ ] 错误消息友好

## 🟢 低优先级（优化项）

### 最佳实践
- [ ] 使用设计模式（如适用）
- [ ] 代码可测试性高
- [ ] 遵循SOLID原则
- [ ] 异常处理使用异常链
- [ ] 资源自动释放（with语句）

### 文档
- [ ] API文档完整
- [ ] 使用示例清晰
- [ ] 变更记录更新
- [ ] 部署说明完整

## 📊 具体检查项

### Python代码检查
```python
# ✅ 正确示例
from typing import List, Optional
import logging

_LOGGER = logging.getLogger(__name__)

MAX_RETRY_COUNT = 3  # 常量使用大写

def process_data(
    data: List[str],
    max_items: Optional[int] = None
) -> List[str]:
    """
    处理数据函数，对输入的数据列表进行处理并返回结果。
    
    Args:
        data: 要处理的数据列表
        max_items: 最大处理项数，如果为None则处理所有项
        
    Returns:
        处理后的数据列表
        
    Raises:
        ValueError: 当数据为空或max_items为负数时
    """
    if not data:
        raise ValueError("数据不能为空")
    
    if max_items is not None and max_items < 0:
        raise ValueError("max_items不能为负数")
    
    # 业务逻辑
    return [item.upper() for item in data[:max_items]]

# ❌ 错误示例
def bad_func(data):  # 缺少类型注解
    result = []
    for d in data:
        # 魔法数字
        if len(d) > 50:  # 50应该定义为常量
            result.append(d)
    return result
```

### Django特定检查
```python
# ✅ 正确示例
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class ExerciseRecord(models.Model):
    """运动记录模型。"""
    
    title = models.CharField(
        max_length=200,
        verbose_name="标题",
        help_text="运动的标题"
    )
    
    duration = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        verbose_name="持续时间（分钟）",
        help_text="运动持续时间，单位分钟"
    )
    
    class Meta:
        verbose_name = "运动记录"
        verbose_name_plural = "运动记录"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

# ❌ 错误示例
class BadModel(models.Model):
    name = models.CharField(max_length=100)  # 缺少verbose_name和help_text
    # 缺少Meta配置
```

### API检查
```python
# ✅ 正确示例
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

class ExerciseViewSet(viewsets.ModelViewSet):
    """运动记录API视图集。"""
    
    queryset = ExerciseRecord.objects.all()
    serializer_class = ExerciseRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """获取运动统计信息。"""
        user = request.user
        stats = {
            "total_count": self.queryset.filter(user=user).count(),
            "total_duration": self.queryset.filter(user=user).aggregate(
                total=models.Sum("duration")
            )["total"] or 0,
        }
        return Response(stats)

# ❌ 错误示例
class BadViewSet(viewsets.ModelViewSet):
    # 缺少权限控制
    # 缺少文档字符串
    # 缺少错误处理
    pass
```

## 🛠️ 工具支持

### 自动化检查
```bash
# 语法检查
python -m py_compile your_file.py

# 类型检查（如使用mypy）
mypy your_file.py

# 代码风格检查（如使用flake8）
flake8 your_file.py

# 安全扫描（如使用bandit）
bandit -r your_directory/
```

### 手动检查命令
```bash
# 检查行长度
grep -n ".\{121,\}" *.py

# 检查魔法数字
grep -n "[0-9]\{2,\}" *.py | grep -v "0x" | grep -v "\.py:[0-9]*:[ ]*#"

# 检查裸except
grep -n "except:" *.py

# 检查print语句
grep -n "print(" *.py
```

## 📝 审查记录模板

### 审查记录
```markdown
## 审查信息
- **审查日期**: YYYY-MM-DD
- **审查人员**: [姓名]
- **代码作者**: [姓名]
- **PR/Commit**: [链接]

## 审查结果
- **总体评价**: [通过/有条件通过/不通过]
- **问题数量**: [数字]
- **测试状态**: [通过/失败]

## 发现的问题

### 高优先级问题
1. [ ] 问题描述
   - 文件: `path/to/file.py`
   - 行号: 123
   - 建议: 修复建议

### 中优先级问题
1. [ ] 问题描述
   - 文件: `path/to/file.py`
   - 行号: 456
   - 建议: 修复建议

### 低优先级问题
1. [ ] 问题描述
   - 文件: `path/to/file.py`
   - 行号: 789
   - 建议: 修复建议

## 审查结论
[通过/需要修改后重新审查/不通过]

## 后续行动
- [ ] 问题修复
- [ ] 重新测试
- [ ] 重新审查
```

## 🔄 审查流程

### 1. 提交代码
- 开发者提交PR或代码变更
- 关联需求文档和测试结果

### 2. 自动化检查
- 运行CI/CD流水线
- 执行自动化测试
- 代码质量扫描

### 3. 人工审查
- 使用本Checklist逐项检查
- 记录发现的问题
- 给出审查结论

### 4. 问题修复
- 开发者修复问题
- 更新测试用例
- 重新提交审查

### 5. 最终批准
- 确认所有问题已修复
- 运行完整测试套件
- 批准合并

## 📈 质量指标跟踪

### 每周质量报告
| 指标 | 本周 | 上周 | 趋势 | 目标 |
|------|------|------|------|------|
| 代码规范符合率 | 85% | 83% | ↗️ | 95% |
| 测试覆盖率 | 80% | 78% | ↗️ | 90% |
| 审查通过率 | 90% | 88% | ↗️ | 95% |
| 缺陷密度 | 0.5/千行 | 0.6/千行 | ↘️ | 0.2/千行 |

### 月度质量趋势
- 代码质量趋势图
- 缺陷分布分析
- 审查效率指标
- 团队改进建议

## 🎯 持续改进

### 团队培训
- [ ] 每月代码规范培训
- [ ] 安全开发培训
- [ ] 最佳实践分享
- [ ] 工具使用培训

### 流程优化
- [ ] 审查流程简化
- [ ] 工具链优化
- [ ] 自动化提升
- [ ] 反馈机制改进

### 知识库建设
- [ ] 常见问题解答
- [ ] 最佳实践案例
- [ ] 代码模板库
- [ ] 审查经验分享

---

**版本**: 1.0.0  
**更新日期**: 2026-03-25  
**维护者**: 代码审查工程师  
**适用范围**: Coach AI 项目所有代码审查