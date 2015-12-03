
import math
import requests
import xml.etree.ElementTree as ET
import os

try:
    ORDORO_USPS_KEY = os.environ['ORDORO_USPS_KEY']
except:
    raise RuntimeError("You don't have the Ordoro USPS API key loaded as an environment variable.")

def get_rate_from_usps(zip_origin, zip_dest, ounces, width, height, depth):

    size = 'REGULAR' if int(width)+int(height)+int(depth) < 12 else 'LARGE'
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
    <Machinable>true</Machinable>
    </Package>
    </RateV4Request>""".format(ORDORO_USPS_KEY, zip_origin, zip_dest, pounds, ozs, size)

    return requests.get('http://production.shippingapis.com/ShippingAPI.dll?API=RateV4&XML='+rateV4Request)


def get_services_from_response(xmlstring):
    out = {}
    root = ET.fromstring(xmlstring)
    package = root.find('Package')
    for service in package.findall('Postage'):
        out[service.find('MailService').text] = service.find('Rate').text
    return out


if __name__ == "__main__":
    a = get_rate_from_usps(78701, 83501, 32, 3,2,5)
    # make sure status was good, etc.
    b = get_services_from_response(a.text)
    print(a.status_code)
