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

    http://localhost:8000/getquotes/?from_zip=78701&to_zip=83501&weight=66&width=3&height=6&depth=3

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

## Answers to Ben's Questions

### The Most Difficult Part:
Working with XML. It was unfamiliar-- I hadn't used it in a couple years, but that wasn't the hard part. A tree is a tree. My issue was with the subtle rules of what is, and is not allowable in XML. You saw me struggle in the interview with understanding the escaped html characters in some of the USPS service names. I knew they were *sort of* escaped characters, but they didn't look right. The reason was that XML needed to escape the ampersands that were also being used to escape html, e.g., `&lt;` became `&amp;lt;`. Weird. But at least it didn't break the app.

Later, with the label maker, I got stumped trying to mail to "Apt # 1000". That pound sign broke the XML parser at USPS, with a thoroughly unhelpful error message that didn't even point to a line number. I put my request XML through an online validator and it came out clean. I didn't find anything on the need to escape that character, but figured it out with trial and error. In terms of getting code running, that was the hardest part.

More generally, the parts I found intellectually challenging were the architecture and code organization choices. Working at home, I could still hear Darrell asking about my rationale for every refactor. I tried to have good answers for him. As I told you, API design is a skill I'm trying to develop, and sometimes code organization seems ambiguous to me. The anti-pattern "inversion of abstraction" is something I've found myself caught in more than once, but avoiding it isn't always obvious ahead of time.

### My Favorite Feature:
My favorite feature of my app is really the only non-barebones feature it has. I modified the "get rates" response to provide a guide for making the label call. Each service indicates the "service_type" and "container" fields that can be passed to "label" in order to yield a label for that service.

I know the implementation is simple. Perhaps it doesn't maximally "showcase my abilities" as the assignment description said. Nevertheless, I think it demonstrates the way I think about development: it's a utility that's focused on making life easier for the client. It's a big convenience that minimizes work on the client side, and it makes my api feel more "cohesive," as a suite of tools meant to be used together.

My Roadmap from here:
I don't think I'm going to do most of this, just because we're short on time. But in a perfect world, here's what I'd extend from here:
* Finish the test suite... by which I mean, at this point, make one.
* Error handling and data validation-- there's a whole lot of it I didn't do, because it's a wireframe.
* Add support for other kinds of request-- POST with form data, json (fairly trivial with Django Rest Framework.)
* Plug in a database, add:
    * authentication, with ability to save labels you've created to your profile
    * Amazon S3 integration, putting labels in buckets, and creating signed URL's for (semi-) securely/privately accessing them. (This will be my favorite feature if I get around to building it.)
    * Support for more of the USPS API-- insurance options, live animal shipping, etc.
