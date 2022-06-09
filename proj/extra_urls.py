
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path


async def hi(request):
    return HttpResponse(str(request))

urlpatterns = [
    path('hi/', hi),
]