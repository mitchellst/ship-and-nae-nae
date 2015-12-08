Rounding out the shipper API from our interview.

This first commit is essentially just the interview code, with one slight difference:
the ordoro USPS api key has been moved into an environment variable in order to keep
it out of version control. Before running, in bash:

    $export ORDORO_USPS_KEY="#the key"
    $echo $ORDORO_USPS_KEY
    $ #make sure you see the key here

## Taking it for a Spin
Once you have the environment variable in place, in your virtual environment run `pip install -r requirements.txt`. You're ready to spin it up: `python manage.py runserver` will run it on port 8000.

From here, there are two urls:

    http://localhost:8000/getrates/
    http://localhost:8000/getlabel/

Navigate to each one and you'll see a browsable API. You can issue GET requests with percent-encoded strings or POST JSON or form-encoded data.

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
* Plug in a database, add:
    * authentication, with ability to save labels you've created to your profile
    * Amazon S3 integration, putting labels in buckets, and creating signed URL's for (semi-) securely/privately accessing them. (This will be my favorite feature if I get around to building it.)
    * Support for more of the USPS API-- insurance options, live animal shipping, etc.
