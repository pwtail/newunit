import asyncio

from django.http import JsonResponse
from django.urls import path


def check_mail(request):
    return JsonResponse({'result': True})

async def notify_about_mail(request):
    await asyncio.sleep(0.5)
    return JsonResponse({'success': True})


urlpatterns = [
    path('check/', check_mail),
    path('notify/', notify_about_mail),
]