from django.shortcuts import render
from django.http import HttpResponse
import json
from .uspsinterface import get_rates_in_dictionary, get_label_image

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

def get_label(request):

    AVAILABLE_LABEL_KWARGS = ("width", "height", "depth", "container", "girth")

    from_dict = {key[5:]: value for key, value in request.GET.items() if key[:5]=="from_"}
    to_dict = {key[3:]: value for key, value in request.GET.items() if key[:3]=="to_"}
    label_kwargs = {key: value  for key, value in request.GET.items() if key in AVAILABLE_LABEL_KWARGS}
    label = get_label_image(from_dict, to_dict, request.GET['weight'], **label_kwargs)

    response = HttpResponse(status=200, content_type="image/tiff")
    response.write(label)
    return response
