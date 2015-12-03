Rounding out the shipper API from our interview.

This first commit is essentially just the interview code, with one slight difference:
the ordoro USPS api key has been moved into an environment variable in order to keep
it out of version control. Before running, in bash:

    $export ORDORO_USPS_KEY="#the key"
    $echo $ORDORO_USPS_KEY
    $ #make sure you see the key here
