from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.renderers import BrowsableAPIRenderer

from .serializers import RateForm
from .uspsinterface import get_rates_in_dictionary, get_label_image, flip_address_1_and_2

class get_quote(GenericAPIView):
    """
    Use this endpoint to get quotes for shipping a package on various services. You can issue a GET
    request with percent-encoded data, or POST JSON or form-encoded data. Parameters are listed below.

        REQUIRED PARAMETERS
        from_zip: 5-digit "from" zip code.
        to_zip: 5-digit "to" zip code.
        weight: Weight of the package, in ounces. (int or float)

        OPTIONAL PARAMETERS:
        The following three are required if their sum exceeds 12 and container is not specified NONRECTANGULAR:
            width: of package, in inches, float or int.
            height: of package, in inches, float or int.
            depth: of package, in inches, float or int.
            container: RECTANGULAR or NONRECTANGULAR if sum of preceding three exceeds 12.

        GIRTH is required if container is specified NONRECTANGULAR.
            girth: of package, in inches, float or int.

        container: (other potential values)
        Flat Rate Envelope | Padded Flat Rate Envelope | Legal Flat Rate Envelope |
        Sm Flat Rate Envelope | Window Flat Rate Envelope | Gift Card Flat Rate Envelope |
        Flat Rate Box | Sm Flat Rate Box | Md Flat Rate Box | Lg Flat Rate Box

    Responses:

        The response will be a JSON object whose keys are mail service name, and whose values are objects
        containing:
            rate: price of service in dollars and cents, e.g. "6.10"
            service_type: argument that can be passed as-is to label maker for selected service
            container: argument that can be passed as-is to label make for selected service.
    """
    serializer_class = RateForm

    def fetch_rate(self, request):
        # Validate arguments as we arrange them for USPS Interface.
        try: # Required args must exist.
            getrate_args = [request.data['from_zip'], request.data['to_zip'], request.data['weight']]
        except KeyError:
            return Response({"errors": "Rate request must specify origin and destination zips, weight."}, status=400)

        #Keyword args need not exist, but if they do, they must coerce to numbers.
        getrate_kwargs = {}
        for x in ['width', 'height', 'depth', 'girth']:
            if x in request.data and request.data[x] != '':
                getrate_kwargs[x] = request.data[x]
                if type(request.data[x]) == str:
                    try:
                        float(request.data[x].strip())
                    except ValueError:
                        return Response({"errors": "{0} must be a number".format(x)}, status=400)

        # Pass our prepared arguments to our USPS API interface, and return result.
        responseDict = get_rates_in_dictionary(*getrate_args, **getrate_kwargs)

        status = responseDict.pop("status")
        response = Response(responseDict, status=status)
        return response

    def get(self, request, *args, **kwargs):
        if not request.data:
            return Response({}) #renders the browsable API, and therefore documentation.
        else:
            return self.fetch_rate(request)

    def post(self, request, *args, **kwargs):
        return self.fetch_rate(request)

def get_label(request):

    AVAILABLE_LABEL_KWARGS = ("width", "height", "depth", "container", "girth", "service_type")

    from_dict = {key[5:]: value for key, value in request.GET.items() if key[:5]=="from_"}
    to_dict = {key[3:]: value for key, value in request.GET.items() if key[:3]=="to_"}
    flip_address_1_and_2(from_dict)
    flip_address_1_and_2(to_dict)
    label_kwargs = {key: value  for key, value in request.GET.items() if key in AVAILABLE_LABEL_KWARGS}
    label = get_label_image(from_dict, to_dict, request.GET['weight'], **label_kwargs)

    response = HttpResponse(status=200, content_type="image/tiff")
    response.write(label)
    return response
