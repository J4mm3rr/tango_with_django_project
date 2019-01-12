from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Create key/value pairs for passing to template.
    # in this case, boldmessage corresponds to a {{ boldmessage }} in index.html.
    context_dict = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}

    # Now return a rendered response, with the intial request,
    # the template, and the context dict above
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'boldmessage': "This tutorial has been put together by James"}
    return render(request, 'rango/about.html', context=context_dict)
