from django.urls import path
from .import views

app_name='blog'
urlpatterns = [
    path('feed/', views.post_list, name='post_list' ),
    path('auto_search/', views.auto_search, name='auto_search'),
    path('like', views.like_post, name='like_post'),
    path('follow', views.follow, name='follow'),
    path('<int:id>/post-edit', views.post_edit, name='post_edit'),
    path('<int:id>/post-delete', views.post_delete, name="post_delete"),
    path('<int:id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/comment-delete/<int:id>', views.comment_delete, name="comment_delete"),
    path('<int:reply_id>/reply-delete/<int:post_id>/<int:comment_id>', views.reply_delete, name="reply_delete"),
    path('create-post/', views.post_create, name='create_post'),
    path('login/', views.user_login , name="user_login"),
    path('logout/', views.user_logout , name="user_logout"),
    path('registration/', views.user_registration, name="user_registration"),
    path('edit-profiles/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/<int:id>/', views.profile, name='profile'),
    path('cover-photo/', views.photo_list , name="photo_list"),
    path('avatar/', views.avatar_list , name="avatar"),
    path('profile/<str:username>.<int:id>/<int:photo_id>', views.coverUpdate, name="coverUpdate"),
    path('coverRemove/<str:username>.<int:id>', views.coverRemove, name="coverRemove"),
    path('coverDelete/<int:id>/', views.coverDelete, name="coverDelete"),
    path('profile/<str:username>/<int:id>', views.avatarUpdate, name="avatarUpdate"),
    path('avatarRemove/<str:username>/<int:id>', views.avatarRemove, name="avatarRemove"),
    path('avatarDelete/<int:id>', views.avatarDelete, name="avatarDelete"),
    path('settings/<str:username>/', views.settings, name="settings"),
    path('delete/', views.delete_profile, name="delete_profile"),
    path('gallery/<str:username>/', views.gallery, name="galley"),
    path('password_change/', views.change_password, name='change_password'),
    
] 