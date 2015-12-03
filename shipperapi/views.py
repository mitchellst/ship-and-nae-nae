from django.shortcuts import render
from django.http import HttpResponse
import json
from .uspsinterface import get_rate_from_usps, get_services_from_response

def get_quote(request):

    getrate_args = [request.GET['or_zip'], request.GET['ds_zip'], request.GET['weight'],
        request.GET['dim_w'], request.GET['dim_h'], request.GET['dim_d']]
    from_usps = get_rate_from_usps(*getrate_args)
    responseDict = get_services_from_response(from_usps.text)
    response = HttpResponse(content_type="application/json")
    response.write(json.dumps(responseDict))
    return response, 200
