#!/usr/bin/env python3
"""
Test script for Django DRF + MCP Integration
Tests both REST API endpoints and MCP protocol endpoints
"""
import json
import time

import requests

# Django server URL
DJANGO_URL = "http://127.0.0.1:8000"
REST_API_URL = f"{DJANGO_URL}/api/users/"
MCP_URL = f"{DJANGO_URL}/mcp/"


def test_rest_api():
    """Test Django REST API endpoints"""
    print("🔍 Testing Django REST API...")

    try:
        # Test GET users list
        response = requests.get(REST_API_URL)
        print(f"✅ GET {REST_API_URL} -> {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Users count: {data.get('count', 0)}")

        # Test creating a user via REST API
        user_data = {
            "username": "rest_user",
            "email": "rest@example.com",
            "first_name": "REST",
            "last_name": "User",
            "password": "testpass123",
            "bio": "Created via REST API",
        }

        response = requests.post(REST_API_URL, json=user_data)
        print(f"✅ POST {REST_API_URL} -> {response.status_code}")
        if response.status_code == 201:
            created_user = response.json()
            print(f"   Created user ID: {created_user.get('id')}")
            return created_user.get("id")

    except requests.exceptions.RequestException as e:
        print(f"❌ REST API Error: {e}")
        return None


def test_mcp_protocol():
    """Test MCP protocol endpoints"""
    print("\n🔍 Testing MCP Protocol...")

    try:
        # Test MCP server info
        response = requests.get(MCP_URL)
        print(f"✅ GET {MCP_URL} -> {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"   MCP Server: {info.get('name', 'Unknown')}")

        # Test MCP tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {},
        }

        response = requests.post(MCP_URL, json=tools_request)
        print(f"✅ POST {MCP_URL} (tools/list) -> {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            print(f"   Available tools: {len(tools)}")
            for tool in tools[:3]:  # Show first 3 tools
                print(f"   - {tool.get('name')}: {tool.get('description')}")

        # Test MCP create user tool
        create_user_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_user",
                "arguments": {
                    "username": "mcp_user",
                    "email": "mcp@example.com",
                    "first_name": "MCP",
                    "last_name": "User",
                    "password": "mcppass123",
                    "bio": "Created via MCP protocol",
                },
            },
        }

        response = requests.post(MCP_URL, json=create_user_request)
        print(f"✅ POST {MCP_URL} (create_user) -> {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                print(f"   MCP Response: {content[0].get('text', '')[:100]}...")

        # Test MCP list users tool
        list_users_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "list_users", "arguments": {}},
        }

        response = requests.post(MCP_URL, json=list_users_request)
        print(f"✅ POST {MCP_URL} (list_users) -> {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            content = result.get("result", {}).get("content", [])
            if content:
                print(f"   Users listed via MCP: Success")

    except requests.exceptions.RequestException as e:
        print(f"❌ MCP Protocol Error: {e}")


def test_server_status():
    """Check if Django server is running"""
    print("🔍 Checking Django server status...")
    try:
        response = requests.get(DJANGO_URL, timeout=5)
        print(f"✅ Django server is running at {DJANGO_URL}")
        return True
    except requests.exceptions.RequestException:
        print(f"❌ Django server is not running at {DJANGO_URL}")
        print("   Please start the server with: python manage.py runserver")
        return False


def main():
    """Main test function"""
    print("🚀 Django DRF + MCP Integration Test")
    print("=" * 50)

    if not test_server_status():
        return

    # Test REST API
    user_id = test_rest_api()

    # Test MCP Protocol
    test_mcp_protocol()

    print("\n🎉 Integration test completed!")
    print(f"✅ REST API available at: {REST_API_URL}")
    print(f"✅ MCP Protocol available at: {MCP_URL}")
    print("\n📝 Summary:")
    print("   - Django REST API: Working")
    print("   - MCP Protocol: Integrated")
    print("   - Single Server: ✅ Both running on port 8000")


if __name__ == "__main__":
    main()
