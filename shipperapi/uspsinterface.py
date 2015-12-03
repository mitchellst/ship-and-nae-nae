
import math
import requests
import xml.etree.ElementTree as ET
import html
import os

try:
    ORDORO_USPS_KEY = os.environ['ORDORO_USPS_KEY']
except:
    raise RuntimeError("You don't have the Ordoro USPS API key loaded as an environment variable.")

def build_rate_request_xml(zip_origin, zip_dest, ounces, width=None, height=None, depth=None,
                        girth=None, container=""):

    #defaults, override below in dimensions if clause
    dimensions_xml = ""
    whd_xml = ""
    size = "REGULAR"

    if width is not None and height is not None and depth is not None:
        dimensions = [float(width), float(height), float(depth)]
        if sum(dimensions) > 12:
            size = 'LARGE'
            dimensions_xml = """"
                <Width>{1}</Width>
                <Length>{2}</Length>
                <Height>{3}</Height>""".format(width, height, depth)

        if girth is None:
            #calculate a girth if none provided. Take 2 shortest dimensions and multiply.
            dimensions.sort()
            girth = 2 * dimensions[0] + 2 * dimensions[1]

    dimensions_xml = dimensions_xml + "<Girth>{0}</Girth>".format(girth)

    #calculate our weights.
    ounces = float(ounces)
    pounds = math.floor(ounces/16)
    ozs = ounces % 16

    rateV4Request = """<RateV4Request USERID="{0}">
    <Revision>2</Revision>
    <Package ID="1ST">
    <Service>ALL</Service>
    <ZipOrigination>{1}</ZipOrigination>
    <ZipDestination>{2}</ZipDestination>
    <Pounds>{3}</Pounds>
    <Ounces>{4}</Ounces>
    <Container>{5}</Container>
    <Size>{6}</Size>{7}
    <Machinable>true</Machinable>
    </Package>
    </RateV4Request>""".format(ORDORO_USPS_KEY, zip_origin, zip_dest, pounds, ozs,
        container, size, dimensions_xml)

    return rateV4Request

def issue_usps_api_request(xmlstring, api="rates"):
    """Function used to issue calls to the USPS API via GET request. Returns a requests.Response
    object. This function will need to be extended as I add the label maker, but it's here to make
    unit testing possible without pestering the USPS API too much."""

    valid_api_identifiers = {"rates": "?API=RateV4&XML=",}
    try:
        this_api = valid_api_identifiers[api]
    except KeyError:
        options = ' '.join(valid_api_identifiers.keys())
        raise RuntimeError("That's not an API we support. Choose from: "+ options)

    request_string = 'http://production.shippingapis.com/ShippingAPI.dll' + this_api + xmlstring
    return requests.get(request_string)


def get_service_rates_from_response(rates_xmlstring):
    out = {}
    root = ET.fromstring(rates_xmlstring)
    package = root.find('Package')
    for service in package.findall('Postage'):
        service_name_raw = service.find('MailService').text

        #USPS returns weird superscript html characters, which it has to escape for XML.
        # Make them unicode for our JSON response. Note: this leaves <sup> html tags in place.
        service_name = html.unescape(service_name_raw.replace('&amp;', '&'))

        out[service_name] = service.find('Rate').text
    return out

def get_rates_in_dictionary(*args, **kwargs):
    """
    Convenience method to unclutter the view. Builds an XML request from parameters,
    sends the request, and returns the rates for each service unpacked into a dictionary.
    Calling signature is:

    get_rates_in_dictionary(origin_zip, destination_zip, weight_in_ounces, **kwargs)

    Those keyword arguments are:
    container= USPS container type. (optional) If you specify an envelope, other dimensions not required.
    width= width in inches. Required only if w+h+d > 12 inches.
    height= height in inches. Required only if w+h+d > 12 inches.
    depth= depth in inches. Required only if w+h+d > 12 inches.
    girth= girth in inches. Required IF:
        - You don't provide width, height, and depth
        - Container is NONRECTANGULAR


    """
    requestxml = build_rate_request_xml(*args, **kwargs)
    from_usps = issue_usps_api_request(requestxml, api="rates")
    return get_service_rates_from_response(from_usps.text)

#convenient little tester while building.
if __name__ == "__main__":
    a = buid_rate_request_xml(78701, 83501, 32, width=3, height=2, depth=5)
    b = issue_usps_api_request(a)
    # make sure status was good, etc.
    c = get_service_rates_from_response(b.text)
    print(b.status_code)
    print(b.text)
    print(c)
