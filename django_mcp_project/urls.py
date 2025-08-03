"""
URL configuration for django_mcp_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

# Import the universal MCP view (auto-discovers all ViewSets)
from django_mcp_project.mcp_view import CustomMCPView, MCPView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("mcp/", MCPView.as_view(), name="mcp"),
    path("", include("users.urls")),
]
