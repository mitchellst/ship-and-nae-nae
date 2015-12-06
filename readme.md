Rounding out the shipper API from our interview.

This first commit is essentially just the interview code, with one slight difference:
the ordoro USPS api key has been moved into an environment variable in order to keep
it out of version control. Before running, in bash:

    $export ORDORO_USPS_KEY="#the key"
    $echo $ORDORO_USPS_KEY
    $ #make sure you see the key here

## Some Test URL Strings
URL-encoded GET requests are annoying to write, I know. Since I didn't build a nice JS client, here are some templates to cut-and-pasted into your browser and mess around with:

For `getlabel` endpoint:

    http://localhost:8000/getlabel/?weight=44&width=6&height=9&depth=7&from_name=Mitchell&from_firm=&from_address2=&from_address1=111%20Preston%20Ave&from_city=Lewiston&from_state=ID&from_zip=83501&from_zip4=&to_name=Stoutin&to_firm=&to_address2=11160%20Jollyville%20Rd&to_address1=APT%201000&to_city=Austin&to_state=TX&to_zip=78759&to_zip4=

It will return a label as a tiff image.

for `getrates` endpoint:

    http://localhost:8000/getquotes/?or_zip=78701&ds_zip=83501&weight=66&width=3&height=6&depth=3

it will return:

    {
      "Library Mail Parcel": {
        "rate": "4.51",
        "service_type": "LIBRARY MAIL",
        "container": ""
      },
      "Priority Mail 3-Day<sup>\u2122<\/sup> Padded Flat Rate Envelope": {
        "rate": "6.10",
        "service_type": "PRIORITY",
        "container": "FLAT RATE ENVELOPE"
      },
      "Priority Mail Express 2-Day<sup>\u2122<\/sup> Flat Rate Boxes": {
        "rate": "44.95",
        "service_type": "PRIORITY",
        "container": "FLAT RATE BOX"
      },
      "Priority Mail 3-Day<sup>\u2122<\/sup> Window Flat Rate Envelope": {
        "rate": "5.75",
        "service_type": "PRIORITY",
        "container": "FLAT RATE ENVELOPE"
      },
      "Priority Mail 3-Day<sup>\u2122<\/sup> Small Flat Rate Envelope": {
        "rate": "5.75",
        "service_type": "PRIORITY",
        "container": "FLAT RATE ENVELOPE"
      }, ... TRUNCATED ...}
