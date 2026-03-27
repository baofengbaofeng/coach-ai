#!/usr/bin/env python3
"""
测试服务器启动和基本功能
"""

import subprocess
import time
import sys
import requests

def test_server():
    """测试服务器"""
    
    print("启动CoachAI服务器...")
    
    # 启动服务器
    server_process = subprocess.Popen(
        [sys.executable, "-m", "coding.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(3)
    
    try:
        # 测试健康检查端点
        print("测试健康检查端点...")
        response = requests.get("http://localhost:8888/api/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            
            # 测试数据库健康检查
            print("测试数据库健康检查...")
            response = requests.get("http://localhost:8888/api/health/db", timeout=5)
            if response.status_code == 200:
                print(f"✅ 数据库健康检查成功: {response.json()}")
            else:
                print(f"❌ 数据库健康检查失败: {response.status_code}")
                
            # 测试Redis健康检查
            print("测试Redis健康检查...")
            response = requests.get("http://localhost:8888/api/health/redis", timeout=5)
            if response.status_code == 200:
                print(f"✅ Redis健康检查成功: {response.json()}")
            else:
                print(f"❌ Redis健康检查失败: {response.status_code}")
                
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    finally:
        # 停止服务器
        print("停止服务器...")
        server_process.terminate()
        server_process.wait()
        
        # 输出服务器日志
        print("\n服务器输出:")
        stdout, stderr = server_process.communicate()
        if stdout:
            print("标准输出:")
            print(stdout[:1000])  # 只显示前1000字符
        if stderr:
            print("错误输出:")
            print(stderr[:1000])  # 只显示前1000字符

if __name__ == "__main__":
    test_server()