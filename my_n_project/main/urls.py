from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.about, name='about'),
    path('cur/', views.cur, name='cur'),
    path('done/', views.done, name='done'),
    path('friends/', views.friends, name='friends'),
    path('create_chall/', views.create, name='create'),
    path('chall/', views.chall, name='chall'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('searching_friends/', views.searching_friends, name='search_fr'),
    path('new_applays/', views.new_applays, name='new_applays'),
    path('save_comment/<int:chall_id>/', views.save_comment, name='save_comment'),
    path('get_comments/<int:chall_id>/', views.get_comments, name='get_comments'),
    path('chall_is_done', views.chall_is_done, name='chall_is_done'),
    path('chall_to_delete', views.delete_chall, name='chall_to_delete'),
]