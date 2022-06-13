
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path


async def hi(request):
    text = str(request).strip('<>')
    return HttpResponse(text)

def low(request):
    text = str(request).strip('<>')
    return HttpResponse(text)

urlpatterns = [
    path('hi/', hi),
    path('low/', low),
]