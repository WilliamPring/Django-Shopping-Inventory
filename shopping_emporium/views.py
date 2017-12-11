from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.template import loader

# Create your views here.
def MainView(request):
    template = loader.get_template('shopping_emporium/index.html')
    context = {
        '':'',
    }
    return HttpResponse(template.render(context, request))

def DetailView(request, type):
    template = loader.get_template('shopping_emporium/detail.html')
    context = {
        '':'',
    }
    return HttpResponse(template.render(context,request))

def ViewView(request):
    template = loader.get_template('shopping_emporium/view.html')
    context = {
        '':'',
    }
    return HttpResponse(template.render(context,request))
