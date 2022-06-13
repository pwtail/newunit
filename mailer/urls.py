import asyncio

from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

import mailer.check_urls

from django.http import JsonResponse


async def send_letter(request):
    await asyncio.sleep(0.5)
    return JsonResponse({'sent': True})


urlpatterns = [
    path('check/', include(mailer.check_urls)),
    path('send/', send_letter),
]
