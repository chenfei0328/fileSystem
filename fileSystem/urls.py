"""fileSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from app_fs import views as fs_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', fs_views.home, name = 'home'),
    url(r'^ajax/treeMenu', fs_views.ajax_treeMenu, name = 'ajax_treeMenu'),
    url(r'^ajax/readFile', fs_views.ajax_readFile, name = 'ajax_readFile'),
    url(r'^ajax/rename', fs_views.ajax_rename, name = 'ajax_rename'),
    url(r'^ajax/createFile', fs_views.ajax_createFile, name = 'createFile'),
    url(r'^ajax/deleteFile', fs_views.ajax_deleteFile, name = 'deleteFile'),
    url(r'^ajax/reviseFile', fs_views.ajax_reviseFile, name = 'reviseFile'),
    url(r'^ajax/readFCB', fs_views.ajax_readFCB, name = 'readFCB'),
    url(r'^ajax/about', fs_views.ajax_about, name = 'ajax_about'),
    url(r'^ajax/login', fs_views.ajax_readUserInfo, name = 'ajax_readUserInfo'),
]
