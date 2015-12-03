
import math
import requests
import xml.etree.ElementTree as ET
import html
import os

try:
    ORDORO_USPS_KEY = os.environ['ORDORO_USPS_KEY']
except:
    raise RuntimeError("You don't have the Ordoro USPS API key loaded as an environment variable.")

def get_rate_from_usps(zip_origin, zip_dest, ounces, width=None, height=None, depth=None,
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

    return requests.get('http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML='+rateV4Request)


def get_services_from_response(xmlstring):
    out = {}
    root = ET.fromstring(xmlstring)
    package = root.find('Package')
    for service in package.findall('Postage'):
        service_name_raw = service.find('MailService').text

        #USPS returns weird superscript html characters, which it has to escape for XML.
        # Make them unicode for our JSON response. Note: this leaves <sup> html tags in place.
        service_name = html.unescape(service_name_raw.replace('&amp;', '&'))

        out[service_name] = service.find('Rate').text
    return out


if __name__ == "__main__":
    a = get_rate_from_usps(78701, 83501, 32, width=3, height=2, depth=5)
    # make sure status was good, etc.
    b = get_services_from_response(a.text)
    print(a.status_code)
    print(a.text)
    print(b)
