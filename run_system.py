#!/usr/bin/env python3
"""
AI法规合规辅助系统启动和测试脚本
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def install_dependencies():
    """安装项目依赖"""
    print("正在安装依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def start_server():
    """启动服务器"""
    print("正在启动服务器...")
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"])

def wait_for_server(max_attempts=30):
    """等待服务器启动"""
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("服务器启动成功!")
                return True
        except:
            pass
        time.sleep(1)
        print(f"等待服务器启动... ({i+1}/{max_attempts})")
    
    return False

def run_tests():
    """运行API测试"""
    print("开始运行API测试...")
    subprocess.run([sys.executable, "tests/test_api.py"])

def main():
    print("=" * 50)
    print("AI法规合规辅助系统")
    print("=" * 50)
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 检查环境变量
    api_key = os.getenv("ALIBABA_API_KEY")
    if api_key:
        print(f"✓ 检测到API密钥: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("警告: 未设置ALIBABA_API_KEY环境变量，某些功能可能无法正常工作")
    
    choice = input("\n请选择操作:\n1. 安装依赖\n2. 启动系统\n3. 运行测试\n4. 完整测试(安装+启动+测试)\n请输入选择 (1-4): ")
    
    if choice == "1":
        install_dependencies()
        
    elif choice == "2":
        server_process = start_server()
        print("服务器正在运行，按 Ctrl+C 停止")
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n正在停止服务器...")
            server_process.terminate()
    
    elif choice == "3":
        print("请确保服务器已在 http://localhost:8001 运行")
        input("按 Enter 继续...")
        run_tests()
    
    elif choice == "4":
        install_dependencies()
        server_process = start_server()
        
        if wait_for_server():
            run_tests()
        else:
            print("服务器启动失败!")
        
        print("正在停止服务器...")
        server_process.terminate()
    
    else:
        print("无效选择!")

if __name__ == "__main__":
    main()