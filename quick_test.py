#!/usr/bin/env python3
"""
简单的API测试脚本
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8001"
    
    print("🧪 测试 AI法规合规辅助系统 API")
    print("=" * 50)
    
    # 1. 健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查错误: {e}")
    
    # 2. API文档
    print("\n2. 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档访问错误: {e}")
    
    # 3. 前端页面
    print("\n3. 测试前端页面...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端页面访问错误: {e}")
    
    # 4. 文档列表API
    print("\n4. 测试文档列表API...")
    try:
        response = requests.get(f"{base_url}/api/documents", timeout=5)
        if response.status_code == 200:
            docs = response.json()
            print(f"✅ 文档列表API正常，当前有 {len(docs)} 个文档")
        else:
            print(f"❌ 文档列表API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 文档列表API错误: {e}")
    
    # 5. 系统统计API
    print("\n5. 测试系统统计API...")
    try:
        response = requests.get(f"{base_url}/api/statistics", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 系统统计API正常")
            print(f"   - 文档总数: {stats.get('documents', {}).get('total_count', 0)}")
            print(f"   - 向量总数: {stats.get('vectors', {}).get('total_segments', 0)}")
        else:
            print(f"❌ 系统统计API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 系统统计API错误: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 系统已成功启动在 http://localhost:8001")
    print("📖 API文档: http://localhost:8001/docs")
    print("🌐 前端界面: http://localhost:8001")

if __name__ == "__main__":
    test_api()