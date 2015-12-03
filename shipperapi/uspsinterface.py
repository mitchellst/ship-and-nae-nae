
import math
import requests
import xml.etree.ElementTree as ET
import html
import os

try:
    ORDORO_USPS_KEY = os.environ['ORDORO_USPS_KEY']
except:
    raise RuntimeError("You don't have the Ordoro USPS API key loaded as an environment variable.")

def get_rate_from_usps(zip_origin, zip_dest, ounces, width, height, depth, girth=None):

    size = 'REGULAR' if int(width)+int(height)+int(depth) < 12 else 'LARGE'
    girth = int(width)*2 + int(depth)*2 if girth is None else girth
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
    <Container />
    <Size>{5}</Size>
    <Width>{6}</Width>
    <Length>{7}</Length>
    <Height>{8}</Height>
    <Girth>{9}</Girth>
    <Machinable>true</Machinable>
    </Package>
    </RateV4Request>""".format(ORDORO_USPS_KEY, zip_origin, zip_dest, pounds, ozs,
        size, width, height, depth, girth)

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
    a = get_rate_from_usps(78701, 83501, 32, 3,2,5)
    # make sure status was good, etc.
    b = get_services_from_response(a.text)
    print(a.status_code)
