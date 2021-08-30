from django.urls import path
from .views import index, group_posts

app_name = 'posts'

urlpatterns = [
    path('', index, name='index'),
    path('group/<slug:slug>/', group_posts, name='group_list')
]
