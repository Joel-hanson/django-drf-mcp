"""
🚀 UNIVERSAL MCP VIEW FOR DJANGO DRF

Drop this into any Django DRF project to add MCP support instantly!

FEATURES:
✅ Auto-discovers all ModelViewSets in your project
✅ Generates MCP tools for CRUD operations (list, create, retrieve, update, destroy)
✅ Supports custom @action decorated methods
✅ Dynamic schema generation from DRF serializers
✅ Comprehensive error handling and validation
✅ Zero configuration required

USAGE:
1. Copy this file to your Django project
2. Add to urls.py: path('mcp/', MCPView.as_view(), name='mcp')
3. Test: curl -X POST http://127.0.0.1:8000/mcp/ -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

CUSTOMIZATION:
- Override server_info() to customize MCP server details
- Override get_viewset_classes() to filter which ViewSets are exposed
- Override get_tool_prefix() to customize tool naming
"""

import importlib
import inspect
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, JsonResponse
from django.test import RequestFactory
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

logger = logging.getLogger(__name__)


class MCPView(View):
    """
    Universal MCP endpoint for Django DRF projects.

    Automatically discovers ModelViewSets and creates MCP tools for:
    - Standard CRUD operations (list, create, retrieve, update, destroy)
    - Custom @action decorated methods
    - Dynamic schema generation from serializers
    """

    # Configuration - Override these in subclasses for customization
    MCP_PROTOCOL_VERSION = "2024-11-05"
    MCP_SERVER_NAME = "django-drf-mcp"
    MCP_SERVER_VERSION = "1.0.0"

    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Handle MCP JSON-RPC requests."""
        try:
            data = json.loads(request.body)
            method = data.get("method")
            request_id = data.get("id")

            # Route to appropriate handler
            handlers = {
                "initialize": self._handle_initialize,
                "tools/list": self._handle_tools_list,
                "tools/call": self._handle_tools_call,
            }

            if method in handlers:
                if method == "tools/call":
                    return handlers[method](request_id, data.get("params", {}))
                else:
                    return handlers[method](request_id)
            else:
                return self._error_response(request_id, -32601, "Method not found")

        except json.JSONDecodeError:
            return self._error_response(None, -32700, "Parse error")
        except Exception as e:
            logger.exception("Unexpected error in MCP request handling")
            return self._error_response(
                data.get("id") if "data" in locals() else None, -32603, str(e)
            )

    def _handle_initialize(self, request_id: Any) -> JsonResponse:
        """Handle MCP initialize request."""
        server_info = self.get_server_info()
        return JsonResponse(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": self.MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": server_info,
                },
            }
        )

    def _handle_tools_list(self, request_id: Any) -> JsonResponse:
        """Handle tools/list request."""
        tools = self.discover_tools()
        return JsonResponse(
            {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}
        )

    def _handle_tools_call(
        self, request_id: Any, params: Dict[str, Any]
    ) -> JsonResponse:
        """Handle tools/call request."""
        tool_name = params.get("name", "unknown")
        arguments = params.get("arguments", {})

        try:
            result = self.execute_tool(tool_name, arguments)
            return JsonResponse(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result,
                            }
                        ]
                    },
                }
            )
        except Exception as e:
            logger.exception(f"Tool execution failed: {tool_name}")
            return self._error_response(
                request_id, -32603, f"Tool execution error: {str(e)}"
            )

    def _error_response(self, request_id: Any, code: int, message: str) -> JsonResponse:
        """Return a JSON-RPC error response."""
        return JsonResponse(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": code, "message": message},
            }
        )

    # =================================================================
    # CONFIGURATION METHODS - Override these for customization
    # =================================================================

    def get_server_info(self) -> Dict[str, str]:
        """Get MCP server information. Override to customize."""
        return {
            "name": self.MCP_SERVER_NAME,
            "version": self.MCP_SERVER_VERSION,
            "description": "Auto-generated MCP tools from Django DRF ViewSets",
        }

    def get_viewset_classes(self) -> List[Tuple[Type[ModelViewSet], str]]:
        """
        Get all ViewSet classes to expose as MCP tools.
        Override to filter which ViewSets are included.
        """
        viewset_classes = []

        for app_config in apps.get_app_configs():
            # Skip Django built-in apps
            if app_config.name.startswith("django."):
                continue

            try:
                views_module = importlib.import_module(f"{app_config.name}.views")

                for attr_name in dir(views_module):
                    attr = getattr(views_module, attr_name)

                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, ModelViewSet)
                        and attr != ModelViewSet
                    ):
                        viewset_classes.append((attr, app_config.name))

            except (ImportError, AttributeError):
                continue

        return viewset_classes

    def get_tool_prefix(self, viewset_class: Type[ModelViewSet], app_name: str) -> str:
        """
        Get the prefix for tool names.
        Override to customize tool naming convention.
        """
        model_name = self._extract_model_name(viewset_class)
        return f"{app_name}_{model_name.lower()}"

    # =================================================================
    # TOOL DISCOVERY AND EXECUTION
    # =================================================================

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover all available MCP tools from ViewSets."""
        tools = []

        for viewset_class, app_name in self.get_viewset_classes():
            tool_prefix = self.get_tool_prefix(viewset_class, app_name)
            model_name = self._extract_model_name(viewset_class)

            # Standard CRUD operations
            crud_actions = ["list", "create", "retrieve", "update", "destroy"]
            for action in crud_actions:
                if hasattr(viewset_class, action):
                    tools.append(
                        self._create_crud_tool(
                            action, tool_prefix, model_name, app_name, viewset_class
                        )
                    )

            # Custom @action decorated methods
            custom_actions = self._discover_custom_actions(viewset_class)
            for custom_action in custom_actions:
                tools.append(
                    self._create_custom_tool(
                        custom_action, tool_prefix, model_name, app_name
                    )
                )

        return tools

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool by name with given arguments."""
        # Parse tool name: {action}_{app}_{model}
        parts = tool_name.split("_")
        if len(parts) < 3:
            raise ValueError(f"Invalid tool name format: {tool_name}")

        action = parts[0]
        app_name = parts[1]
        model_name = parts[2]

        # Find the ViewSet
        viewset_class = self._find_viewset(app_name, model_name)
        if not viewset_class:
            raise ValueError(f"ViewSet not found for {app_name}.{model_name}")

        # Execute the action
        return self._execute_viewset_action(viewset_class, action, arguments)

    # =================================================================
    # INTERNAL METHODS
    # =================================================================

    def _create_crud_tool(
        self,
        action: str,
        tool_prefix: str,
        model_name: str,
        app_name: str,
        viewset_class: Type[ModelViewSet],
    ) -> Dict[str, Any]:
        """Create a tool definition for a CRUD action."""
        return {
            "name": f"{action}_{tool_prefix}",
            "description": f"{action.title()} {model_name} in {app_name}",
            "inputSchema": self._generate_action_schema(viewset_class, action),
        }

    def _create_custom_tool(
        self,
        custom_action: Dict[str, Any],
        tool_prefix: str,
        model_name: str,
        app_name: str,
    ) -> Dict[str, Any]:
        """Create a tool definition for a custom action."""
        schema = {
            "type": "object",
            "properties": custom_action.get("properties", {}),
            "required": (
                ["id"]
                if custom_action.get("detail")
                and "id" in custom_action.get("properties", {})
                else []
            ),
        }

        return {
            "name": f"{custom_action['name']}_{tool_prefix}",
            "description": f"{custom_action['description']} {model_name} in {app_name}",
            "inputSchema": schema,
        }

    def _discover_custom_actions(
        self, viewset_class: Type[ModelViewSet]
    ) -> List[Dict[str, Any]]:
        """Discover custom @action decorated methods in a ViewSet."""
        custom_actions = []

        for method_name in dir(viewset_class):
            method = getattr(viewset_class, method_name)

            if (
                callable(method)
                and hasattr(method, "mapping")
                and hasattr(method, "detail")
            ):
                description = self._extract_method_description(method, method_name)
                properties = (
                    {
                        "id": {
                            "type": "string",
                            "description": "ID of the object to perform action on",
                        }
                    }
                    if getattr(method, "detail", False)
                    else {}
                )

                custom_actions.append(
                    {
                        "name": method_name,
                        "description": description,
                        "detail": getattr(method, "detail", False),
                        "methods": getattr(method, "mapping", {}),
                        "properties": properties,
                    }
                )

        return custom_actions

    def _generate_action_schema(
        self, viewset_class: Type[ModelViewSet], action: str
    ) -> Dict[str, Any]:
        """Generate JSON schema for a ViewSet action."""
        schema = {"type": "object", "properties": {}, "required": []}

        if action == "list":
            schema["properties"] = {
                "limit": {
                    "type": "integer",
                    "description": "Number of results to return per page",
                    "minimum": 1,
                },
                "offset": {
                    "type": "integer",
                    "description": "The initial index from which to return results",
                    "minimum": 0,
                },
            }
        elif action in ["retrieve", "destroy"]:
            model_name = self._extract_model_name(viewset_class).lower()
            schema["properties"]["id"] = {
                "type": "string",
                "description": f"ID of the {model_name} to {action}",
            }
            schema["required"] = ["id"]
        elif action in ["create", "update"]:
            schema = self._generate_serializer_schema(viewset_class, action)

        return schema

    def _generate_serializer_schema(
        self, viewset_class: Type[ModelViewSet], action: str
    ) -> Dict[str, Any]:
        """Generate schema from ViewSet's serializer."""
        schema = {"type": "object", "properties": {}, "required": []}

        serializer_class = self._get_serializer_class(viewset_class, action)
        if not serializer_class:
            return schema

        try:
            temp_serializer = serializer_class()

            # Handle ListSerializer case
            if hasattr(temp_serializer, "child"):
                temp_serializer = temp_serializer.child  # type: ignore

            if not hasattr(temp_serializer, "fields"):
                return schema

            # Type ignore for fields access - this works for serializer instances
            for field_name, field in temp_serializer.fields.items():  # type: ignore
                if field.read_only:
                    continue

                field_schema = self._convert_field_to_schema(field)
                if field_schema:
                    schema["properties"][field_name] = field_schema

                    if field.required and action == "create":
                        schema["required"].append(field_name)

            # For updates, add ID requirement
            if action == "update":
                model_name = self._extract_model_name(viewset_class).lower()
                schema["properties"]["id"] = {
                    "type": "string",
                    "description": f"ID of the {model_name} to update",
                }
                schema["required"] = ["id"]

        except Exception as e:
            logger.warning(f"Failed to generate schema from serializer: {e}")

        return schema

    def _convert_field_to_schema(self, field) -> Dict[str, Any]:
        """Convert a DRF serializer field to JSON schema format."""
        field_schema = {}

        # Map field types to JSON schema types
        type_mapping = {
            serializers.CharField: "string",
            serializers.EmailField: "string",
            serializers.IntegerField: "integer",
            serializers.FloatField: "number",
            serializers.BooleanField: "boolean",
            serializers.DateField: "string",
            serializers.DateTimeField: "string",
            serializers.ChoiceField: "string",
        }

        field_type = type(field)
        field_schema["type"] = type_mapping.get(field_type, "string")

        # Add format for special types
        if isinstance(field, serializers.EmailField):
            field_schema["format"] = "email"
        elif isinstance(field, serializers.DateField):
            field_schema["format"] = "date"
        elif isinstance(field, serializers.DateTimeField):
            field_schema["format"] = "date-time"

        # Add constraints (with proper type checking)
        if (
            hasattr(field, "max_length")
            and getattr(field, "max_length", None) is not None
        ):
            field_schema["maxLength"] = getattr(field, "max_length")
        if isinstance(field, serializers.ChoiceField) and hasattr(field, "choices"):
            field_schema["enum"] = [str(choice[0]) for choice in field.choices]

        # Add description
        field_schema["description"] = (
            getattr(field, "help_text", "")
            or getattr(field, "label", "")
            or f"The {field_type.__name__.replace('Field', '').lower()} value"
        )

        return field_schema

    def _execute_viewset_action(
        self, viewset_class: Type[ModelViewSet], action: str, arguments: Dict[str, Any]
    ) -> str:
        """Execute a ViewSet action with given arguments."""
        # Create mock request
        factory = RequestFactory()

        # Determine HTTP method and URL
        if action in ["list", "active"]:
            django_request = factory.get("/api/mock/")
        elif action == "create":
            django_request = factory.post("/api/mock/", data=arguments)
        elif action in ["retrieve", "update", "destroy", "activate", "deactivate"]:
            obj_id = arguments.get("id")
            if not obj_id:
                raise ValueError(
                    f"Missing required parameter 'id' for action '{action}'"
                )

            if action == "retrieve":
                django_request = factory.get(f"/api/mock/{obj_id}/")
            elif action == "update":
                django_request = factory.patch(f"/api/mock/{obj_id}/", data=arguments)
            elif action == "destroy":
                django_request = factory.delete(f"/api/mock/{obj_id}/")
            else:  # activate, deactivate
                django_request = factory.post(f"/api/mock/{obj_id}/{action}/")
        else:
            raise ValueError(f"Unsupported action: {action}")

        # Set up request
        django_request.user = AnonymousUser()
        request = Request(django_request)

        # For data-containing requests, manually set the data
        if action in ["create", "update"] and arguments:
            request._full_data = arguments

        # Initialize ViewSet
        viewset = viewset_class()
        # Type ignore for request assignment - this works at runtime
        viewset.request = request  # type: ignore
        viewset.format_kwarg = None
        viewset.action = action
        viewset.filter_backends = []

        # Execute action
        response = self._call_viewset_method(viewset, action, arguments)

        # Format response
        if response is not None and hasattr(response, "data"):
            return f"Action '{action}' completed successfully.\n\nResponse data:\n{json.dumps(response.data, indent=2, default=str)}"
        elif response is not None and hasattr(response, "status_code"):
            return f"Action '{action}' completed successfully.\n\nStatus: {response.status_code}"
        else:
            return f"Action '{action}' completed successfully."

    def _call_viewset_method(self, viewset, action: str, arguments: Dict[str, Any]):
        """Call the appropriate ViewSet method for the action."""
        if action == "list":
            return viewset.list(viewset.request)
        elif action == "create":
            return viewset.create(viewset.request)
        elif action in ["retrieve", "update", "destroy"]:
            obj_id = arguments.get("id")
            viewset.kwargs = {"pk": obj_id}

            if action == "retrieve":
                return viewset.retrieve(viewset.request, pk=obj_id)
            elif action == "update":
                return viewset.partial_update(viewset.request, pk=obj_id)
            elif action == "destroy":
                return viewset.destroy(viewset.request, pk=obj_id)
        else:
            # Custom action
            action_method = getattr(viewset, action, None)
            if not action_method:
                raise ValueError(f"Action method '{action}' not found in ViewSet")

            if action in ["activate", "deactivate"] or getattr(
                action_method, "detail", False
            ):
                obj_id = arguments.get("id")
                if not obj_id:
                    raise ValueError(
                        f"Missing required parameter 'id' for action '{action}'"
                    )
                viewset.kwargs = {"pk": obj_id}
                return action_method(viewset.request, pk=obj_id)
            else:
                return action_method(viewset.request)

    # =================================================================
    # UTILITY METHODS
    # =================================================================

    def _find_viewset(
        self, app_name: str, model_name: str
    ) -> Optional[Type[ModelViewSet]]:
        """Find ViewSet class by app and model name."""
        try:
            views_module = importlib.import_module(f"{app_name}.views")

            for attr_name in dir(views_module):
                attr = getattr(views_module, attr_name)
                if (
                    inspect.isclass(attr)
                    and issubclass(attr, ModelViewSet)
                    and attr != ModelViewSet
                ):
                    if hasattr(attr, "queryset") and attr.queryset is not None:
                        model_class = attr.queryset.model
                        if model_class._meta.model_name.lower() == model_name:
                            return attr
        except ImportError:
            pass

        return None

    def _get_serializer_class(
        self, viewset_class: Type[ModelViewSet], action: str
    ) -> Optional[Type[serializers.Serializer]]:
        """Get serializer class for a ViewSet and action."""
        if hasattr(viewset_class, "get_serializer_class"):
            try:
                temp_viewset = viewset_class()
                temp_viewset.action = action
                return temp_viewset.get_serializer_class()
            except:
                pass

        return getattr(viewset_class, "serializer_class", None)

    def _extract_model_name(self, viewset_class: Type[ModelViewSet]) -> str:
        """Extract model name from ViewSet."""
        # Try queryset first (most reliable)
        if hasattr(viewset_class, "queryset") and viewset_class.queryset is not None:
            return viewset_class.queryset.model.__name__

        # Try model attribute (if exists)
        if hasattr(viewset_class, "model") and getattr(viewset_class, "model", None):
            model = getattr(viewset_class, "model")
            return model.__name__

        # Try serializer Meta model
        if (
            hasattr(viewset_class, "serializer_class")
            and viewset_class.serializer_class
        ):
            serializer = viewset_class.serializer_class
            if hasattr(serializer, "Meta") and hasattr(serializer.Meta, "model"):
                return serializer.Meta.model.__name__

        # Fallback to class name
        return viewset_class.__name__.replace("ViewSet", "")

    def _extract_method_description(self, method, method_name: str) -> str:
        """Extract description from method docstring or generate default."""
        doc = getattr(method, "__doc__", "")
        if doc:
            return doc.strip().split("\n")[0]
        return f"Custom action: {method_name}"


# =================================================================
# EXAMPLE CUSTOMIZATION
# =================================================================


class CustomMCPView(MCPView):
    """
    Example of customizing the MCP view.
    Override methods to customize behavior.
    """

    MCP_SERVER_NAME = "my-custom-mcp-server"
    MCP_SERVER_VERSION = "2.0.0"

    def get_server_info(self):
        """Customize server information."""
        return {
            "name": self.MCP_SERVER_NAME,
            "version": self.MCP_SERVER_VERSION,
            "description": "Custom Django MCP server with enhanced features",
            "author": "Your Name",
            "homepage": "https://your-website.com",
        }

    def get_viewset_classes(self):
        """Only expose certain ViewSets."""
        viewset_classes = super().get_viewset_classes()

        # Filter to only include specific apps or models
        allowed_apps = ["users", "products"]  # Only these apps

        return [
            (viewset_class, app_name)
            for viewset_class, app_name in viewset_classes
            if app_name in allowed_apps
        ]

    def get_tool_prefix(self, viewset_class, app_name):
        """Customize tool naming."""
        model_name = self._extract_model_name(viewset_class)
        # Use a different naming convention
        return f"{model_name.lower()}_{app_name}"


# =================================================================
# USAGE EXAMPLES
# =================================================================

"""
# Basic usage in urls.py:
from django.urls import path
from mcp_view_universal import MCPView

urlpatterns = [
    path('mcp/', MCPView.as_view(), name='mcp'),
]

# Custom usage in urls.py:
from django.urls import path
from mcp_view_universal import CustomMCPView

urlpatterns = [
    path('mcp/', CustomMCPView.as_view(), name='mcp'),
]

# Claude Desktop config:
{
    "mcpServers": {
        "django-server": {
            "command": "npx",
            "args": ["-y", "mcp-remote", "http://127.0.0.1:8000/mcp/"]
        }
    }
}

# VSCode MCP extension config:
{
    "servers": {
        "django-server": {
            "type": "http",
            "url": "http://127.0.0.1:8000/mcp/"
        }
    }
}

# Warp MCP extension config:
{
    "Django Server": {
        "command": "npx",
        "args": [
            "-y",
            "mcp-remote",
            "http://127.0.0.1:8000/mcp/"
        ],
        "env": {},
        "working_directory": null
    }
}
"""
