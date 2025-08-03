# Django REST Framework + MCP Integration

A simple Django REST Framework application with integrated Model Context Protocol (MCP) server.

## Overview

This project demonstrates the simplest way to add MCP (Model Context Protocol) support to any Django REST Framework project. Just copy one file (`mcp_view.py`) and add one URL pattern - that's it!

## Features

- **Django REST Framework API** - Complete CRUD operations for User management
- **Simple MCP Integration** - Single file MCP view with auto-discovery
- **Zero Dependencies** - Only uses Django, DRF, and Python standard library
- **Auto-discovery** - Automatically finds DRF ViewSets and creates MCP tools

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python manage.py migrate
```

### 3. Start the Server

```bash
python manage.py runserver
```

The server provides:

- **REST API**: `http://localhost:8000/api/users/`
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **Admin**: `http://localhost:8000/admin/`

## Adding MCP to Your Django Project

Want to add MCP support to your existing Django DRF project? It's incredibly simple:

### 1. Copy the MCP View

Copy `django_mcp_project/mcp_view.py` to your Django project.

### 2. Add URL Pattern

In your `urls.py`:

```python
from your_project.mcp_view import MCPView

urlpatterns = [
    # your existing patterns...
    path("mcp/", MCPView.as_view(), name="mcp"),
]
```

### 3. That's it!

Your Django project now has MCP support. The view automatically discovers all your DRF ViewSets and creates MCP tools for them.

## Testing MCP Integration

Test that your MCP endpoint is working:

```bash
curl -X POST http://127.0.0.1:8000/mcp/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'
```

## API Endpoints

### User Management

- `GET/POST /api/users/` - List all users / Create new user
- `GET/PUT/PATCH/DELETE /api/users/{id}/` - User detail operations
- `POST /api/users/{id}/activate/` - Activate user
- `POST /api/users/{id}/deactivate/` - Deactivate user

### MCP Integration

- `POST /mcp/` - MCP JSON-RPC endpoint with auto-discovered tools

## Project Structure

```
django-drf-mcp/
├── django_mcp_project/
│   ├── mcp_view.py          # 🌟 The magic file - copy this to any DRF project
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL configuration with MCP endpoint
│   └── wsgi.py              # WSGI configuration
├── users/                   # Example Django app with User model
│   ├── models.py            # Extended User model
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # DRF ViewSets
│   └── urls.py              # User API endpoints
├── manage.py                # Django management script
├── requirements.txt         # Dependencies
└── .vscode/                 # VS Code MCP client configuration
```

## How It Works

The `MCPView` class in `mcp_view.py`:

1. **Auto-discovers** all Django apps and their ViewSets
2. **Creates MCP tools** for each CRUD operation (list, create, retrieve, update, destroy)
3. **Provides JSON-RPC interface** compatible with MCP clients
4. **Requires zero configuration** - just works out of the box

## VS Code Integration

Add to your `.vscode/mcp.json`:

```json
{
  "servers": {
    "django-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

## License

MIT License - feel free to use this in your projects!
