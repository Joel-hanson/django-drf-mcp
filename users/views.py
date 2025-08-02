import importlib
import inspect
import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserListSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    Provides create, read, update, delete functionality.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        """List all users"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new user"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        """Get a specific user by ID"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update a user"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        """Delete a user"""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get only active users"""
        active_users = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(active_users)

        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(active_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "user deactivated"})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "user activated"})


class MCPView(View):
    """MCP endpoint for Django DRF projects - integrated directly into Django."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        """Handle MCP requests."""
        try:
            data = json.loads(request.body)
            method = data.get("method")

            if method == "initialize":
                return JsonResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {
                                "name": "django-mcp-integrated",
                                "version": "1.0.0",
                            },
                        },
                    }
                )

            elif method == "tools/list":
                tools = self._discover_tools()
                return JsonResponse(
                    {"jsonrpc": "2.0", "id": data.get("id"), "result": {"tools": tools}}
                )

            elif method == "tools/call":
                # For demo purposes - you can implement actual tool execution here
                tool_name = data.get("params", {}).get("name", "unknown")
                return JsonResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "result": {
                            "content": [
                                {"type": "text", "text": f"Executed tool: {tool_name}"}
                            ]
                        },
                    }
                )

            else:
                return JsonResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": data.get("id"),
                        "error": {"code": -32601, "message": "Method not found"},
                    }
                )

        except Exception as e:
            return JsonResponse(
                {
                    "jsonrpc": "2.0",
                    "id": data.get("id", None),
                    "error": {"code": -32603, "message": str(e)},
                }
            )

    def _discover_tools(self):
        """Auto-discover ViewSets and create MCP tools."""
        tools = []
        for app_config in apps.get_app_configs():
            try:
                views_module = importlib.import_module(f"{app_config.name}.views")
                for attr_name in dir(views_module):
                    attr = getattr(views_module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, ModelViewSet)
                        and attr != ModelViewSet
                    ):

                        model_name = (
                            attr.queryset.model.__name__
                            if hasattr(attr, "queryset") and attr.queryset
                            else attr_name.replace("ViewSet", "")
                        )
                        app_name = app_config.name

                        for action in [
                            "list",
                            "create",
                            "retrieve",
                            "update",
                            "destroy",
                        ]:
                            if hasattr(attr, action):
                                tools.append(
                                    {
                                        "name": f"{action}_{app_name}_{model_name.lower()}",
                                        "description": f"{action.title()} {model_name} in {app_name}",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {},
                                        },
                                    }
                                )
            except (ImportError, AttributeError):
                continue
        return tools
