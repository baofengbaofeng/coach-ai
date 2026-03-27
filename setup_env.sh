#!/bin/bash
# CoachAI 环境设置脚本
# 设置PYTHONPATH以便可以直接导入模块

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODING_DIR="$PROJECT_ROOT/coding"

echo "设置CoachAI项目环境"
echo "项目根目录: $PROJECT_ROOT"
echo "代码目录: $CODING_DIR"

# 检查目录是否存在
if [ ! -d "$CODING_DIR" ]; then
    echo "错误: coding目录不存在: $CODING_DIR"
    exit 1
fi

# 设置PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$CODING_DIR:"* ]]; then
    export PYTHONPATH="$CODING_DIR:$PYTHONPATH"
    echo "已添加 $CODING_DIR 到 PYTHONPATH"
else
    echo "$CODING_DIR 已在 PYTHONPATH 中"
fi

echo ""
echo "当前PYTHONPATH:"
echo "$PYTHONPATH" | tr ':' '\n'

echo ""
echo "测试导入:"
python3 -c "
import sys
print('Python路径:')
for p in sys.path[:3]:
    print(f'  {p}')

try:
    import config
    print('✅ import config 成功')
except ImportError as e:
    print(f'❌ import config 失败: {e}')

try:
    from tornado.core.application import create_application
    print('✅ from tornado.core.application import create_application 成功')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
"

echo ""
echo "环境设置完成！现在可以直接使用以下导入:"
echo "  from config import config"
echo "  from tornado.core.application import create_application"
echo "  from database.connection import get_db_session"