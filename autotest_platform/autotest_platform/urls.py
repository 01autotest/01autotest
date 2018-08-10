"""autotest_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from apps import views as app1_views
from apps.app_interface import views as app_interface_views
from django.contrib.auth.views import auth_login, auth_logout
from django.urls import path,re_path

urlpatterns = [
    path('admin/', admin.site.urls),

    #==登录
    # path('', app1_views.login, name='login'),
    # path('register/',app1_views.register,name = 'register'),
    path('accounts/login/', app1_views.login,name = 'login'),
    path('accounts/logout/', auth_logout),
    path('login/',app1_views.login,name = 'login'),
    path('logout/',app1_views.logout,name = 'logout'),
    path('update_captcha/<str:num>/', app1_views.update_captcha),
    path('', app1_views.login),
    path('index/', app1_views.index),

    #==接口测试
    path('interface_page/<str:modules>/', app_interface_views.interface_page),
    # 公共参数
    path('show_public_para/', app_interface_views.show_public_para),
    path('add_public_para/', app_interface_views.add_public_para),
    path('del_public_para/', app_interface_views.del_public_para),
    path('save_public_para/', app_interface_views.save_public_para),
    # 单接口
    path('show_add_window/<str:module>/', app_interface_views.show_add_window),
    path('add_interfaces/<str:modules>/', app_interface_views.add_interfaces),
    path('format_body/', app_interface_views.format_body),

    path('show_edit_interface/<str:edit_id>/<str:module>/', app_interface_views.show_edit_interface),
    path('save_edit_interface/<str:edit_id>/<str:modules>/', app_interface_views.save_edit_interface),

    path('show_assert/<str:edit_id>/', app_interface_views.show_assert),
    path('save_assert/<str:edit_id>/', app_interface_views.save_assert),

    path('show_assert_AI/<str:edit_id>/', app_interface_views.show_assert_AI),
    path('save_assert_AI/<str:edit_id>/', app_interface_views.save_assert_AI),

    path('del_interfaces/', app_interface_views.del_interface),

    path('start_interface_test/', app_interface_views.start_interface_test),
    path('start_interface_test_AI/', app_interface_views.start_interface_test_AI),
    # 接口测试套
    path('add_suit/', app_interface_views.add_suit),
    path('show_edit_suit/', app_interface_views.show_edit_suit),
    path('save_edit_suit/', app_interface_views.save_edit_suit),
    path('del_row1/', app_interface_views.del_row1),
    path('del_row_edit/', app_interface_views.del_row_edit),
    path('del_suit/', app_interface_views.del_suit),
    path('show_edit_para_suit/', app_interface_views.show_edit_para_suit),
    path('show_edit_suit_interface/<str:para>/', app_interface_views.show_edit_suit_interface),
    path('save_edit_para_suit/', app_interface_views.save_edit_para_suit),
    path('show_assert_suit/<str:id1>/', app_interface_views.show_assert_suit),
    path('save_assert_suit/<str:id1>/', app_interface_views.save_assert_suit),
    path('start_interface_suit/', app_interface_views.start_interface_suit),
    path('start_interface_suit1/', app_interface_views.start_interface_suit1),
    path('task_apis/', app_interface_views.task_apis),
  #  path('start_interface_suit1/', app_interface_views.task_interface_suit1),

    #周期任务
    path('settask/', app_interface_views.settask),
    path('periodic_task/', app_interface_views.periodic_task),


    # 接口测试报告 author:zh  ;date:2018-08-01
    path('apitestreport/', app_interface_views.apitestreport),
    path('reportsearch/', app_interface_views.reportsearch),
    path('testreport_to_email/', app_interface_views.testreport_to_email),
]
