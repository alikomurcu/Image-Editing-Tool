"""
URL configuration for d2023 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
import sys
sys.path.append("..")
from ceng import views as cengview

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', cengview.websocket),
    path('', cengview.auth),
    path('login', cengview.login),
    path('register', cengview.register),
    path('handle_register', cengview.handle_register),
    path('handle_login', cengview.handle_login),
    path('logout', cengview.logout),
    path('home', cengview.homepage),
    path('list', cengview.list),
    path('opengraph', cengview.opengraph),
    path('newgraph', cengview.newgraph),
    path('newnode', cengview.newnode),
    path('newnode/nodeparams', cengview.nodeparams),
    path('listnodes', cengview.listnodes),
    path('connectnodes', cengview.connect),
    path('execute', cengview.execute),
]
