# Simple ICMP Pinger in Python
### Thomas Reichman, Patrick Gemperline, Aaron Pitman
UPDATE: This was originally an assignment from April 2017. Forked to my main account in May 2018.
## Prerequisites

None. Having 'sl' and 'cowsay' installed is highly reccommended. Patrick insists it's required.

## Usage

`python Pinger.py`

This asks whether you want to ping or trace. You'll need to give it a destination address. If you're doing ping, you'll also need to say how many times to ping. We default to 10 if you screw the input up.

Also, be aware that we run the next stuff through python as sudo!

## Testing
For ping:
  * We pinged something that exists, like "xavier.edu".
  * We pinged something that doesn't exist.
  * Servers we couldn't reach (timeout)
  * Many many pings, so we could test inevitable packet loss calculation.
  * Patrick insisted on pinging North Korea. He really really wanted to do SQL injection for the DROP Nuke; pun...

For trace:
  * Tried tracing ourselves.
  * Typical xavier.edu, google.com
  * Stuff we couldn't hit (see above)
  * Foreign/overseas stuff, like agar.io, which is in the Indian Ocean. It takes a lot more links to get out there.
