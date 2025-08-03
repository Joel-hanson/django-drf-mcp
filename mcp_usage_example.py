"""
Example usage of the Universal MCP View

This file shows how to integrate the universal MCP view into your Django project.
"""

from django.urls import path

from django_mcp_project.mcp_view import MCPView

# The universal MCP view automatically discovers all ViewSets
# No need to register them manually!

# URL patterns
urlpatterns = [
    path("mcp/", MCPView.as_view(), name="mcp"),
]

# If you need custom tools, extend the CustomMCPView:
from typing import Any, Dict, List

from django_mcp_project.mcp_view import CustomMCPView


class MyCustomMCPView(CustomMCPView):
    """Example of extending the MCP view with custom tools."""

    def get_custom_tools(self) -> List[Dict[str, Any]]:
        """Add custom tools beyond auto-discovered ones."""
        return [
            {
                "name": "system_health",
                "description": "Check system health status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_database": {
                            "type": "boolean",
                            "description": "Include database connectivity check",
                            "default": True,
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "user_statistics",
                "description": "Get user statistics and metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["day", "week", "month", "year"],
                            "description": "Time period for statistics",
                            "default": "month",
                        }
                    },
                    "required": [],
                },
            },
        ]

    def handle_custom_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Handle custom tool execution."""
        if tool_name == "system_health":
            include_db = arguments.get("include_database", True)
            status = "System is healthy"
            if include_db:
                status += " (Database connection verified)"
            return status

        elif tool_name == "user_statistics":
            period = arguments.get("period", "month")
            from users.models import User

            total_users = User.objects.count()
            return f"User statistics for {period}: Total users: {total_users}"

        # If no custom tool matches, return an error
        raise ValueError(f"Unknown custom tool: {tool_name}")


# Alternative: Use the custom MCP view directly in URLs:
# custom_urlpatterns = [
#     path('mcp/', MyCustomMCPView.as_view(), name='mcp'),
# ]
