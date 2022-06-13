
from django.contrib import admin
from django.urls import path, include

import mailer.urls

api_patterns = [
    path('admin/', admin.site.urls),
    path('mail/', include(mailer.urls)),
]

#
# urlpatterns = [
#     path('api/', include(api_patterns)),
# ]

urlpatterns = api_patterns