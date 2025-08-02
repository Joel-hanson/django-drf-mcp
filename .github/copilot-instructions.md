<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Django DRF MCP Server Project Instructions

This is a Django REST Framework project integrated with Model Context Protocol (MCP) server.

## Project Structure

- Django API with User CRUD operations at `/api/users/`
- MCP server that provides tools to interact with the Django API
- Custom User model with extended fields (bio, birth_date, etc.)

## Key Components

- **Django App**: `users` - Contains User model, serializers, and ViewSets
- **MCP Server**: `src/django_drf_mcp/server.py` - Provides MCP tools for user management
- **API Endpoints**: Full CRUD operations for users with additional actions

## Development Guidelines

- Use Django REST Framework patterns for API development
- Follow MCP protocol standards for server implementation
- Maintain separation between Django API and MCP server layers
- Use proper error handling and validation

## Useful Commands

- Start Django server: `python manage.py runserver`
- Run MCP server: `python -m src.django_drf_mcp.server`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
