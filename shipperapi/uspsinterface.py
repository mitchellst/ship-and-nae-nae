
import math
import requests
import xml.etree.ElementTree as ET
import html
import base64
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
            whd_xml = """
                <Width>{0}</Width>
                <Length>{1}</Length>
                <Height>{2}</Height>
                """.format(width, height, depth)

        if girth == "":
            #calculate a girth if none provided. Take 2 shortest dimensions and multiply.
            dimensions.sort()
            girth = 2 * dimensions[0] + 2 * dimensions[1]

    size_xml = """<Size>{0}</Size>
    """.format(size)

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

def flip_address_1_and_2(addressDict):
    """
    Swaps the values of "address1" and "address2" in the dict it is passed.

    The USPS label API reverses the normal uses of "addres 1" and "address 2".
    Address 1 is the apartment/unit/suite number, and can be blank. Address 2 is the street number,
    and is required.
    """
    swap = addressDict['address1']

    #since address 2 isn't required, it may not exist.
    try:
        addressDict['address1'] = addressDict['address2']
    except KeyError:
        addressDict['address1'] = ''
    addressDict['address2'] = swap
    return None


###########################################
#### RATE REQUEST INTERFACE
###########################################

def build_rate_request_xml(zip_origin, zip_dest, ounces, width=None, height=None, depth=None,
                        girth=None, container=""):

    #specifying container causes rate API to error out unless requesting specific service.
    dimensions_xml = container_xml_section(width, height, depth, girth, '')

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

def container_and_service(serviceName):
    """
    Takes a service description as returned from the rates API and returns the ServiceType and Container
    enumerations as required by the labels API in order to print a label for that service. Returns these in
    a dictionary with two keys, "service_type" and "container". Client can simply repeat these back to our label
    endpoint for their chosen service.
    """

    SERVICES = {
        "Library": 'LIBRARY MAIL',
        "First Class": "FIRST CLASS",
        "Standard Post": 'STANDARD POST',
        "Media Mail": 'MEDIA MAIL',
        "Priority": 'PRIORITY',
    }

    CONTAINERS = {
        "Small Flat Rate Envelope": "SM FLAT RATE ENVELOPE",
        "Legal Flat Rate Envelope": "LEGAL FLAT RATE ENVELOPE",
        "Window Flat Rate Envelope": "WINDOW FLAT RATE ENVELOPE",
        "Padded Flat Rate Envelope": "PADDED FLAT RATE ENVELOPE",
        "Gift Card Flat Rate Envelope": "GIFT CARD FLAT RATE ENVELOPE",
        "Flat Rate Envelope": "FLAT RATE ENVELOPE",
        "Small Flat Rate Box": "SM FLAT RATE BOX",
        "Medium Flat Rate Box": "MD FLAT RATE BOX",
        "Large Flat Rate Box": "LG FLAT RATE BOX",
        "Flat Rate Box": "FLAT RATE BOX",
    }

    out = {"service_type": "", "container": ""}

    for container in CONTAINERS.keys():
        if container in serviceName:
            out['container'] = CONTAINERS[container]

    for service in SERVICES.keys():
        if service in serviceName:
            out['service_type'] = SERVICES[service]

    return out


def get_service_rates_from_response(rates_xmlstring):
    """
    Builds the dictionary of rate responses. Also adds one other key, status,
    which is an integer representing the HTTP status that should be passed back with
    the response. It leverages USPS's error handling. If USPS hands back an error, that
    error will be in "errors", and "status" will be 400 (Bad Request)
    """

    out = {}
    error = None
    root = ET.fromstring(rates_xmlstring)
    package = root.find('Package')
    if package is not None:
        for service in package.findall('Postage'):
            service_name_raw = service.find('MailService').text

            #USPS returns weird superscript html characters, which it has to escape for XML.
            # Make them unicode for our JSON response. Note: this leaves <sup> html tags in place.
            service_name = html.unescape(service_name_raw.replace('&amp;', '&'))
            service_info = {"rate": service.find('Rate').text,}
            service_info.update(container_and_service(service_name))
            out[service_name] = service_info

        #Error can be in two places. Inside the Package tag:
        package_has_error = package.find('Error')
        if package_has_error is not None:
            error = package_has_error

    # or outside the package tag:
    if error is None:
        error = root if root.tag == 'Error' else root.find('Error')


    # Now put the error in our dictionary.
    if error is not None:
        out['errors'] = 'USPS Error: ' + error.find('Description').text
        out['status'] = 400
    else:
        out['status'] = 200

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


###########################################
#### LABEL REQUEST INTERFACE
###########################################

def build_label_request_xml(fromDict, toDict, weight, service_type="PRIORITY",
                width=None, height=None, depth=None, girth=None, container=""):

    # Bug fix. USPS API crashes if you pass a pound sign, e.g. "Apt #20"
    for key, value in fromDict.items():
        if type(value) == str:
            fromDict[key] = value.replace('#', '')
    for key, value in toDict.items():
        if type(value) == str:
            toDict[key] = value.replace('#', '')

    request_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <DelivConfirmCertifyV4.0Request USERID="{0}">
    <Revision>2</Revision>
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
    <ImageType>TIF</ImageType>{19}
    <Machinable>true</Machinable>
    </DelivConfirmCertifyV4.0Request>""".format(ORDORO_USPS_KEY,
        fromDict['name'], fromDict['firm'], fromDict['address1'], fromDict['address2'],
        fromDict['city'], fromDict['state'], fromDict['zip'], fromDict['zip4'],

        toDict['name'], toDict['firm'], toDict['address1'], toDict['address2'],
        toDict['city'], toDict['state'], toDict['zip'], toDict['zip4'],

        weight, service_type, container_xml_section(width, height, depth, girth, container)
    )

    return request_xml

def extract_image_from_label_response(label_xmlstring):
    """
    Decodes tiff image from USPS XML label response, and returns it as bytes.
    You can either save and store it and provide a url for it in JSON, or just
    write this image to your response.

    If the XML string contains an error in stead of an encoded label, it returns
    a dictionary with the key "errors" and a description of the error.
    """
    root = ET.fromstring(label_xmlstring)

    if root.tag == 'Error':
        return {'errors': root.find('Description').text }

    #OK, then it should be a label!
    label = root.find('DeliveryConfirmationLabel')
    return base64.b64decode(label.text)

def get_label_image(fromDict, toDict, weightInOunces, api="certify", **kwargs):
    request_xml = build_label_request_xml(fromDict, toDict, weightInOunces, **kwargs)
    label_xml = issue_usps_api_request(request_xml, api=api)
    return extract_image_from_label_response(label_xml.text)


#convenient little tester while building.
if __name__ == "__main__":
    #Note the ridiculous way that "address1" is the apt/unit number, "address2" is main address.
    fromDict = {'name': 'Mitchell', 'firm': '', 'address2': r'111 Preston Ave', 'address1': '',
        'city': 'Lewiston', 'state': 'ID', 'zip': '83501', 'zip4': ''}
    toDict = {'name': 'Stoutin', 'firm': '', 'address2': r'11160 Jollyvill Rd', 'address1': 'APT 1000',
        'city': 'Austin', 'state': 'TX', 'zip': '78759', 'zip4': ''}
