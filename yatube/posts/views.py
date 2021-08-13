from django.shortcuts import render
from .models import Post


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request):
    context = {
        'text': 'Здесь будет информация о группах проекта Yatube'
    }
    return render(request, 'posts/group_list.html', context)