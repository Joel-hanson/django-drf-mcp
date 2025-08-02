"""
Django MCP Middleware
Adds MCP functionality to existing Django server without needing a separate process
"""

import asyncio
import json
from typing import Any, Dict

import mcp.types as types
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt

from users.models import User
from users.serializers import UserListSerializer, UserSerializer


class MCPMiddleware(MiddlewareMixin):
    """
    Middleware to handle MCP requests in Django
    Intercepts requests to /mcp/ and handles them as MCP protocol requests
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.mcp_tools = self._setup_mcp_tools()

    def process_request(self, request):
        """Process incoming requests and handle MCP protocol requests"""
        if request.path.startswith("/mcp/"):
            return self._handle_mcp_request(request)
        return None

    def _handle_mcp_request(self, request):
        """Handle MCP protocol requests"""
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                method = data.get("method")
                request_id = data.get("id")
                params = data.get("params", {})

                if method == "initialize":
                    # MCP initialization handshake
                    return JsonResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {},
                                    "resources": {},
                                    "prompts": {},
                                    "logging": {},
                                },
                                "serverInfo": {
                                    "name": "django-drf-mcp-integrated",
                                    "version": "1.0.0",
                                },
                            },
                        }
                    )

                elif method == "notifications/initialized":
                    # Client finished initialization - this is a notification, no response needed
                    return JsonResponse({"jsonrpc": "2.0"})

                elif method == "ping":
                    # Ping/pong for connection testing
                    return JsonResponse(
                        {"jsonrpc": "2.0", "id": request_id, "result": {}}
                    )

                elif method == "tools/list":
                    tools = [tool.dict() for tool in self._get_mcp_tools()]
                    return JsonResponse(
                        {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
                    )

                elif method == "tools/call":
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})

                    result = self._call_mcp_tool(tool_name, arguments)
                    return JsonResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {"content": result},
                        }
                    )

                elif method == "resources/list":
                    resources = [
                        resource.dict() for resource in self._get_mcp_resources()
                    ]
                    return JsonResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {"resources": resources},
                        }
                    )

                elif method == "prompts/list":
                    prompts = [prompt.dict() for prompt in self._get_mcp_prompts()]
                    return JsonResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {"prompts": prompts},
                        }
                    )

                else:
                    return JsonResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}",
                            },
                        }
                    )

            except json.JSONDecodeError:
                return JsonResponse(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                    }
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        },
                    }
                )

        elif request.method == "GET" and request.path == "/mcp/":
            # Provide MCP server info
            return JsonResponse(
                {
                    "name": "django-drf-mcp-integrated",
                    "version": "1.0.0",
                    "description": "Django DRF with integrated MCP support",
                    "capabilities": {"tools": True, "resources": True, "prompts": True},
                    "endpoints": {"mcp_protocol": "/mcp/", "rest_api": "/api/"},
                }
            )

        return HttpResponse("MCP endpoint - use POST for protocol requests", status=200)

    def _setup_mcp_tools(self):
        """Setup MCP tools for Django operations"""
        return {
            "list_users": self._list_users_tool,
            "create_user": self._create_user_tool,
            "get_user": self._get_user_tool,
            "update_user": self._update_user_tool,
            "delete_user": self._delete_user_tool,
            "list_active_users": self._list_active_users_tool,
            "activate_user": self._activate_user_tool,
            "deactivate_user": self._deactivate_user_tool,
        }

    def _get_mcp_tools(self):
        """Return available MCP tools"""
        return [
            types.Tool(
                name="list_users",
                description="List all users with pagination",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Page number (optional)",
                        }
                    },
                },
            ),
            types.Tool(
                name="create_user",
                description="Create a new user in Django",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Unique username",
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "User's email address",
                        },
                        "first_name": {
                            "type": "string",
                            "description": "User's first name",
                        },
                        "last_name": {
                            "type": "string",
                            "description": "User's last name",
                        },
                        "password": {
                            "type": "string",
                            "description": "User's password",
                        },
                        "bio": {
                            "type": "string",
                            "description": "User's bio (optional)",
                        },
                        "birth_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Birth date (YYYY-MM-DD, optional)",
                        },
                    },
                    "required": [
                        "username",
                        "email",
                        "first_name",
                        "last_name",
                        "password",
                    ],
                },
            ),
            types.Tool(
                name="get_user",
                description="Get a specific user by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID",
                            "minimum": 1,
                        }
                    },
                    "required": ["user_id"],
                },
            ),
            types.Tool(
                name="update_user",
                description="Update an existing user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID",
                            "minimum": 1,
                        },
                        "username": {"type": "string", "description": "Username"},
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Email",
                        },
                        "first_name": {"type": "string", "description": "First name"},
                        "last_name": {"type": "string", "description": "Last name"},
                        "bio": {"type": "string", "description": "Bio"},
                        "birth_date": {
                            "type": "string",
                            "format": "date",
                            "description": "Birth date (YYYY-MM-DD)",
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Active status",
                        },
                    },
                    "required": ["user_id"],
                },
            ),
            types.Tool(
                name="delete_user",
                description="Delete a user by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID",
                            "minimum": 1,
                        }
                    },
                    "required": ["user_id"],
                },
            ),
            types.Tool(
                name="list_active_users",
                description="List only active users",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Page number (optional)",
                        }
                    },
                },
            ),
            types.Tool(
                name="activate_user",
                description="Activate a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID",
                            "minimum": 1,
                        }
                    },
                    "required": ["user_id"],
                },
            ),
            types.Tool(
                name="deactivate_user",
                description="Deactivate a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID",
                            "minimum": 1,
                        }
                    },
                    "required": ["user_id"],
                },
            ),
        ]

    def _get_mcp_resources(self):
        """Return available MCP resources"""
        # Resources removed due to URI type constraints
        # Django endpoints are available via tools instead
        return []

    def _get_mcp_prompts(self):
        """Return available MCP prompts"""
        return [
            types.Prompt(
                name="user-management-guide",
                description="Provides guidance on using the Django User management tools",
                arguments=[
                    types.PromptArgument(
                        name="operation",
                        description="Specific operation (create/read/update/delete/list)",
                        required=False,
                    )
                ],
            )
        ]

    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call an MCP tool and return the result"""
        if tool_name not in self.mcp_tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            return self.mcp_tools[tool_name](arguments)
        except Exception as e:
            return [
                {
                    "type": "text",
                    "text": f"Error executing tool '{tool_name}': {str(e)}",
                }
            ]

    # MCP Tool implementations
    def _list_users_tool(self, arguments):
        """List all users using Django ORM directly"""
        try:
            page_num = arguments.get("page", 1)
            queryset = User.objects.all().order_by("-created_at")

            paginator = Paginator(queryset, 20)
            page = paginator.get_page(page_num)

            serializer = UserListSerializer(page.object_list, many=True)

            result = {
                "count": paginator.count,
                "next": page.next_page_number() if page.has_next() else None,
                "previous": (
                    page.previous_page_number() if page.has_previous() else None
                ),
                "results": serializer.data,
            }

            return [
                {
                    "type": "text",
                    "text": f"Users list:\n\n{json.dumps(result, indent=2, default=str)}",
                }
            ]
        except Exception as e:
            return [{"type": "text", "text": f"Error listing users: {str(e)}"}]

    def _create_user_tool(self, arguments):
        """Create a user using Django ORM directly"""
        try:
            serializer = UserSerializer(data=arguments)
            if serializer.is_valid():
                user = serializer.save()
                result_serializer = UserSerializer(user)
                return [
                    {
                        "type": "text",
                        "text": f"User created successfully!\n\n{json.dumps(result_serializer.data, indent=2, default=str)}",
                    }
                ]
            else:
                return [
                    {
                        "type": "text",
                        "text": f"Failed to create user. Validation errors: {json.dumps(serializer.errors, indent=2)}",
                    }
                ]
        except Exception as e:
            return [{"type": "text", "text": f"Error creating user: {str(e)}"}]

    def _get_user_tool(self, arguments):
        """Get a specific user by ID using Django ORM"""
        try:
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")

            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)

            return [
                {
                    "type": "text",
                    "text": f"User details:\n\n{json.dumps(serializer.data, indent=2, default=str)}",
                }
            ]
        except User.DoesNotExist:
            return [{"type": "text", "text": f"User with ID {user_id} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error getting user: {str(e)}"}]

    def _update_user_tool(self, arguments):
        """Update a user using Django ORM directly"""
        try:
            user_id = arguments.pop("user_id", None)
            if not user_id:
                raise ValueError("user_id is required")

            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user, data=arguments, partial=True)

            if serializer.is_valid():
                updated_user = serializer.save()
                result_serializer = UserSerializer(updated_user)
                return [
                    {
                        "type": "text",
                        "text": f"User updated successfully!\n\n{json.dumps(result_serializer.data, indent=2, default=str)}",
                    }
                ]
            else:
                return [
                    {
                        "type": "text",
                        "text": f"Failed to update user. Validation errors: {json.dumps(serializer.errors, indent=2)}",
                    }
                ]
        except User.DoesNotExist:
            return [{"type": "text", "text": f"User with ID {user_id} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error updating user: {str(e)}"}]

    def _delete_user_tool(self, arguments):
        """Delete a user using Django ORM directly"""
        try:
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")

            user = User.objects.get(id=user_id)
            user.delete()

            return [{"type": "text", "text": f"User {user_id} deleted successfully!"}]
        except User.DoesNotExist:
            return [{"type": "text", "text": f"User with ID {user_id} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error deleting user: {str(e)}"}]

    def _list_active_users_tool(self, arguments):
        """List only active users using Django ORM directly"""
        try:
            page_num = arguments.get("page", 1)
            queryset = User.objects.filter(is_active=True).order_by("-created_at")

            paginator = Paginator(queryset, 20)
            page = paginator.get_page(page_num)

            serializer = UserListSerializer(page.object_list, many=True)

            result = {
                "count": paginator.count,
                "next": page.next_page_number() if page.has_next() else None,
                "previous": (
                    page.previous_page_number() if page.has_previous() else None
                ),
                "results": serializer.data,
            }

            return [
                {
                    "type": "text",
                    "text": f"Active users list:\n\n{json.dumps(result, indent=2, default=str)}",
                }
            ]
        except Exception as e:
            return [{"type": "text", "text": f"Error listing active users: {str(e)}"}]

    def _activate_user_tool(self, arguments):
        """Activate a user using Django ORM directly"""
        try:
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")

            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()

            return [{"type": "text", "text": f"User {user_id} activated successfully!"}]
        except User.DoesNotExist:
            return [{"type": "text", "text": f"User with ID {user_id} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error activating user: {str(e)}"}]

    def _deactivate_user_tool(self, arguments):
        """Deactivate a user using Django ORM directly"""
        try:
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")

            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()

            return [
                {"type": "text", "text": f"User {user_id} deactivated successfully!"}
            ]
        except User.DoesNotExist:
            return [{"type": "text", "text": f"User with ID {user_id} not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error deactivating user: {str(e)}"}]
