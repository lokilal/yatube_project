from django.shortcuts import render, HttpResponse


def index(request):
    return HttpResponse("Hello World")


def group_posts(request, slug):
    return HttpResponse('This is the ' + slug)
