# 🚀 Django DRF + MCP Integration

**Add MCP (Model Context Protocol) to any Django REST Framework project in 2 minutes!**

## ⚡ Quick Start

### 1. Download & Install

```bash
# Download the universal MCP command
curl -O https://raw.githubusercontent.com/your-repo/django-drf-mcp/main/start_mcp.py

# Create commands directory (if it doesn't exist)
mkdir -p your_project/management/commands/

# Copy the file
cp start_mcp.py your_project/management/commands/
```

### 2. Try It Out

```bash
# See what ViewSets it finds in your project
python manage.py start_mcp --scan

# Start MCP server (runs on port 8001, won't interfere with your Django app)
python manage.py start_mcp
```

### 3. Test It

```bash
# Test the MCP endpoint
curl -X POST http://127.0.0.1:8001/mcp/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## 🎯 What You Get

✅ **Automatic discovery** of all your DRF ViewSets  
✅ **MCP tools** for every CRUD operation  
✅ **Zero code changes** to your existing project  
✅ **Multiple integration options** (standalone, integrated, middleware)  
✅ **VS Code integration** ready

## 🛠️ Example Output

```bash
$ python manage.py start_mcp --scan

🔍 Scanning Django DRF project for ViewSets...

✅ Found 2 apps with DRF ViewSets:

📦 users:
  🔧 UserViewSet (User)
     Actions: list, create, retrieve, update, destroy

📦 products:
  🔧 ProductViewSet (Product)
     Actions: list, create, retrieve, update, destroy

🛠️ Total MCP tools that would be created: 10

🚀 To start MCP server: python manage.py start_mcp
```

## 🔧 Advanced Options

```bash
# Scan project (safe preview)
python manage.py start_mcp --scan

# Generate integration code for direct Django integration
python manage.py start_mcp --integrate

# Start with Django server (same port)
python manage.py start_mcp --runserver

# Standalone server (different port)
python manage.py start_mcp --port 8002
```

## 🎉 Why This Approach?

- **🚀 2-minute setup** - Copy one file, run one command
- **🔒 Zero risk** - Doesn't modify your existing code
- **🌍 Universal** - Works with any Django DRF project
- **📱 Multiple modes** - Choose what works best for you
- **🛠️ Auto-discovery** - Finds all your ViewSets automatically

## 📋 Requirements

- Django (any version)
- Django REST Framework
- Python 3.8+

## 🤝 Share With Your Team

This approach is perfect for:

- **Open source projects** - Add MCP support without breaking changes
- **Enterprise teams** - Safe to test on existing projects
- **Learning** - See MCP in action with your real data
- **Prototyping** - Quick integration for demos

---

**Ready to try it?** Just copy `start_mcp.py` to your project and run `python manage.py start_mcp --scan`! 🚀
