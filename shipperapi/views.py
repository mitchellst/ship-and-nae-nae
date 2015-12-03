from django.shortcuts import render
from django.http import HttpResponse
import json
from .uspsinterface import get_rates_in_dictionary

def get_quote(request):

    getrate_args = [request.GET['or_zip'], request.GET['ds_zip'], request.GET['weight']]
    getrate_kwargs = {}
    for x in ['width', 'height', 'depth', 'girth', 'container']:
        if x in request.GET:
            getrate_kwargs[x] = request.GET[x]
    responseDict = get_rates_in_dictionary(*getrate_args, **getrate_kwargs)
    response = HttpResponse(content_type="application/json", status=200)
    response.write(json.dumps(responseDict))
    return response
