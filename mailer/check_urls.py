import asyncio

from django.http import JsonResponse
from django.urls import path

from proj.util import check_request


def check_mail(request):
    return check_request(request)

async def notify_about_mail(request):
    await asyncio.sleep(0.5)
    return check_request(request)


urlpatterns = [
    path('all/', check_mail),
    path('notify/', notify_about_mail),
]