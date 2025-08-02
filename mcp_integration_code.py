
# Add this to your Django views.py or create a new mcp_views.py file

import json
import importlib
import inspect
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from rest_framework.viewsets import ModelViewSet

class MCPView(View):
    """MCP endpoint for Django DRF projects."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        """Handle MCP requests."""
        try:
            data = json.loads(request.body)
            method = data.get("method")
            
            if method == "initialize":
                return JsonResponse({
                    "jsonrpc": "2.0", "id": data.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "django-mcp", "version": "1.0.0"}
                    }
                })
            
            elif method == "tools/list":
                tools = self._discover_tools()
                return JsonResponse({
                    "jsonrpc": "2.0", "id": data.get("id"),
                    "result": {"tools": tools}
                })
            
            elif method == "tools/call":
                # Implement your tool execution logic here
                return JsonResponse({
                    "jsonrpc": "2.0", "id": data.get("id"),
                    "result": {"content": [{"type": "text", "text": "Tool executed"}]}
                })
            
            else:
                return JsonResponse({
                    "jsonrpc": "2.0", "id": data.get("id"),
                    "error": {"code": -32601, "message": "Method not found"}
                })
                
        except Exception as e:
            return JsonResponse({
                "jsonrpc": "2.0", "id": data.get("id", None),
                "error": {"code": -32603, "message": str(e)}
            })
    
    def _discover_tools(self):
        """Auto-discover ViewSets and create MCP tools."""
        tools = []
        for app_config in apps.get_app_configs():
            try:
                views_module = importlib.import_module(f"{app_config.name}.views")
                for attr_name in dir(views_module):
                    attr = getattr(views_module, attr_name)
                    if (inspect.isclass(attr) and 
                        issubclass(attr, ModelViewSet) and 
                        attr != ModelViewSet):
                        
                        model_name = attr.queryset.model.__name__ if hasattr(attr, 'queryset') and attr.queryset else attr_name.replace('ViewSet', '')
                        app_name = app_config.name
                        
                        for action in ["list", "create", "retrieve", "update", "destroy"]:
                            if hasattr(attr, action):
                                tools.append({
                                    "name": f"{action}_{app_name}_{model_name.lower()}",
                                    "description": f"{action.title()} {model_name} in {app_name}",
                                    "inputSchema": {"type": "object", "properties": {}}
                                })
            except (ImportError, AttributeError):
                continue
        return tools
