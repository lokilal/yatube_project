from django.urls import path, include
from .views import index, group_posts

app_name = 'posts'

urlpatterns = [
    path('', index, name='index'),
    path('group/', group_posts, name='group_list')
]
