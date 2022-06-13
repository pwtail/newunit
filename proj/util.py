from django.http import HttpResponse


def check_request(request):
    text = str(request).strip('<>')
    return HttpResponse(text)