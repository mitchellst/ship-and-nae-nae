
import math
import requests
import xml.etree.ElementTree as ET
import html
import os


###########################################
#### SHARED LABEL + RATE LOGIC
###########################################

#Get the API Key from environment
try:
    ORDORO_USPS_KEY = os.environ['ORDORO_USPS_KEY']
except:
    raise RuntimeError("You don't have the Ordoro USPS API key loaded as an environment variable.")


def container_xml_section(width, height, depth, girth, container):
    """
    Creates and returns a common piece of XML shared by the label creator and rate API's.
    From "Container" element through "Girth."
    """
    girth = "" if girth is None else girth #minor bug fix
    size, whd_xml = "REGULAR", "" #default, override below in dimensions if clause
    container_xml = """
    <Container>{0}</Container>
    """.format(container)

    if width is not None and height is not None and depth is not None:
        dimensions = [float(width), float(height), float(depth)]
        if sum(dimensions) > 12:
            size = 'LARGE'
            whd_xml = """"
                <Width>{1}</Width>
                <Length>{2}</Length>
                <Height>{3}</Height>
                """.format(width, height, depth)

        if girth is None:
            #calculate a girth if none provided. Take 2 shortest dimensions and multiply.
            dimensions.sort()
            girth = 2 * dimensions[0] + 2 * dimensions[1]

    size_xml = "<Size>{0}</Size>".format(size)

    return container_xml + size_xml + whd_xml + "<Girth>{0}</Girth>".format(girth)


def issue_usps_api_request(xmlstring, api="rates"):
    """Function used to issue calls to the USPS API via GET request. Returns a requests.Response
    object. This function will need to be extended as I add the label maker, but it's here to make
    unit testing possible without pestering the USPS API too much."""

    valid_api_identifiers = {"rates": "http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML=",
        "certify": "https://secure.shippingapis.com/ShippingAPI.dll?API=DelivConfirmCertifyV4&XML=",}
    try:
        this_api = valid_api_identifiers[api]
    except KeyError:
        options = ' '.join(valid_api_identifiers.keys())
        raise RuntimeError("That's not an API we support. Choose from: "+ options)

    request_string = this_api + xmlstring
    return requests.get(request_string)


###########################################
#### RATE REQUEST INTERFACE
###########################################

def build_rate_request_xml(zip_origin, zip_dest, ounces, width=None, height=None, depth=None,
                        girth=None, container=""):

    dimensions_xml = container_xml_section(width, height, depth, girth, container)

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
    <Ounces>{4}</Ounces>{5}
    <Machinable>true</Machinable>
    </Package>
    </RateV4Request>""".format(ORDORO_USPS_KEY, zip_origin, zip_dest, pounds, ozs, dimensions_xml)

    return rateV4Request


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
    print('request:')
    print(requestxml)
    from_usps = issue_usps_api_request(requestxml, api="rates")
    print('from usps:')
    print(from_usps.text)
    return get_service_rates_from_response(from_usps.text)


###########################################
#### LABEL REQUEST INTERFACE
###########################################

def build_label_request_xml(fromDict, toDict, weight, service_type="PRIORITY",
                width=None, height=None, depth=None, girth=None, container=""):

    request_xml = """<?xml version="1.0" encoding="UTF-8" ?>
    <DelivConfirmCertifyV4.0Request USERID="{0}">
    <Revision>2</Revision>
    <ImageParameters />
    <FromName>{1}</FromName>
    <FromFirm>{2}</FromFirm>
    <FromAddress1>{3}</FromAddress1>
    <FromAddress2>{4}</FromAddress2>
    <FromCity>{5}</FromCity>
    <FromState>{6}</FromState>
    <FromZip5>{7}</FromZip5>
    <FromZip4>{8}</FromZip4>
    <ToName>{9}</ToName>
    <ToFirm>{10}</ToFirm>
    <ToAddress1>{11}</ToAddress1>
    <ToAddress2>{12}</ToAddress2>
    <ToCity>{13}</ToCity>
    <ToState>{14}</ToState>
    <ToZip5>{15}</ToZip5>
    <ToZip4>{16}</ToZip4>
    <WeightInOunces>{17}</WeightInOunces>
    <ServiceType>{18}</ServiceType>
    <ImageType>TIF</ImageType>
    {19}
    <Machinable>true</Machinable>
    </DelivConfirmCertifyV4.0Request>""".format(ORDORO_USPS_KEY,
        fromDict['name'], fromDict['firm'], fromDict['address1'], fromDict['address2'],
        fromDict['city'], fromDict['state'], fromDict['zip'], fromDict['zip4'],

        toDict['name'], toDict['firm'], toDict['address1'], toDict['address2'],
        toDict['city'], toDict['state'], toDict['zip'], toDict['zip4'],

        weight, service_type, container_xml_section(width, height, depth, girth, container)
    )

    return request_xml

def confirm_label():
    pass


#convenient little tester while building.
if __name__ == "__main__":
    a = buid_rate_request_xml(78701, 83501, 32, width=3, height=2, depth=5)
    b = issue_usps_api_request(a)
    # make sure status was good, etc.
    c = get_service_rates_from_response(b.text)
    print(b.status_code)
    print(b.text)
    print(c)
