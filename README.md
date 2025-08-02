# Django REST Framework + MCP Integration

A professional Django REST Framework application with integrated Model Context Protocol (MCP) server capabilities.

## Overview

This project demonstrates how to integrate MCP (Model Context Protocol) with Django REST Framework, providing both traditional REST API endpoints and MCP tool interfaces for programmatic interaction.

## Features

- **Django REST Framework API** - Complete CRUD operations for User management
- **Integrated MCP Server** - HTTP-based MCP endpoint for tool interactions
- **Universal MCP Command** - Drop-in solution for any Django DRF project
- **Auto-discovery** - Automatically discovers DRF ViewSets and creates MCP tools
- **Professional Architecture** - Clean separation between Django API and MCP layers

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

- **REST API**: `http://localhost:8000/api/`
- **MCP Endpoint**: `http://localhost:8000/mcp/`
- **API Documentation**: `http://localhost:8000/api/docs/`

## API Endpoints

### User Management

- `GET/POST /api/users/` - List all users / Create new user
- `GET/PUT/PATCH/DELETE /api/users/{id}/` - User detail operations
- `POST /api/users/{id}/activate/` - Activate user
- `POST /api/users/{id}/deactivate/` - Deactivate user
- `GET /api/users/active/` - List active users only

### MCP Integration

- `POST /mcp/` - MCP JSON-RPC endpoint

## Universal MCP Solution

This project includes a **universal MCP command** that can be added to any Django DRF project:

### For Any Django DRF Project

1. **Copy the management command**:

   ```bash
   cp users/management/commands/start_mcp.py your_project/management/commands/
   ```

2. **Scan your project**:

   ```bash
   python manage.py start_mcp --scan
   ```

3. **Start MCP server**:
   ```bash
   python manage.py start_mcp
   ```

### Benefits

- ✅ **Zero code changes** to existing DRF projects
- ✅ **Auto-discovery** of all ViewSets
- ✅ **Separate process** (doesn't interfere with main Django app)
- ✅ **Works with any Django version**
- ✅ **Easy to test and debug**

## MCP Tools Available

For each Django DRF ViewSet, the following MCP tools are automatically created:

- `list_{app}_{model}` - List all instances
- `create_{app}_{model}` - Create new instance
- `retrieve_{app}_{model}` - Get instance by ID
- `update_{app}_{model}` - Update instance
- `destroy_{app}_{model}` - Delete instance

## VS Code Integration

Add to your `.vscode/mcp.json`:

```json
{
  "servers": {
    "django-drf-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

For standalone MCP server:

```json
{
  "servers": {
    "django-mcp-standalone": {
      "type": "http",
      "url": "http://127.0.0.1:8001/mcp/"
    }
  }
}
```

## Project Architecture

```
django_mcp_project/
├── django_mcp_project/      # Django project settings
├── users/                   # User management app
│   ├── management/
│   │   └── commands/
│   │       └── start_mcp.py # Universal MCP command
│   ├── models.py           # Extended User model
│   ├── serializers.py      # DRF serializers
│   └── views.py            # DRF ViewSets
├── core/                   # MCP integration
│   └── django_mcp_middleware.py
└── .vscode/                # VS Code configuration
    ├── mcp.json           # MCP server config
    └── tasks.json         # Development tasks
```

## Development

### Running Tests

```bash
python test_django_mcp_integration.py
```

### Available VS Code Tasks

- **Start Django + MCP Server (Integrated)** - Main development server
- **Run Django Migrations** - Apply database migrations
- **Create Django Migrations** - Generate new migrations
- **Test MCP Integration** - Run integration tests

### Testing MCP Endpoints

```bash
# Test tools list
curl -X POST http://127.0.0.1:8000/mcp/
  -H 'Content-Type: application/json'
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}

# Test initialization
curl -X POST http://127.0.0.1:8000/mcp/
  -H 'Content-Type: application/json'
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

## Technical Stack

- **Django 5.0.8** - Web framework
- **Django REST Framework 3.15.2** - API framework
- **Model Context Protocol 1.12.3** - Tool interaction protocol
- **drf-spectacular 0.28.0** - OpenAPI documentation
- **Python 3.12** - Runtime environment

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

For questions or support, please open an issue on GitHub.
