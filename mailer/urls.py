import asyncio

from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include

import mailer.check_urls

from proj.util import check_request


async def send_letter(request):
    await asyncio.sleep(0.5)
    return check_request(request)


urlpatterns = [
    path('check/', include(mailer.check_urls)),
    path('send/', send_letter),
]
