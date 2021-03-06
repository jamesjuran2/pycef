#!/usr/bin/env python

import sys
import re
import json


def cef_parse(str):
    """
    Parse a string in CEF format and return a dict with the header values
    and the extension data.
    """

    # Create the empty dict we'll return later
    values = dict()

    # This regex separates the string into the CEF header and the extension
    # data.  Once we do this, it's easier to use other regexes to parse each
    # part.
    header_re = r'(.*(?<!\\)\|){,7}(.*)'
    
    res = re.search(header_re, str)
    if res:
        header = res.group(1)
        extension = res.group(2)

        # Split the header on the "|" char.  Uses a negative lookbehind
        # assertion to ensure we don't accidentally split on escaped chars,
        # though.
        spl = re.split(r'(?<!\\)\|', header)

        # Since these values are set by their position in the header, it's
        # easy to know which is which.
        values["DeviceVendor"] = spl[1]
        values["DeviceProduct"] = spl[2]
        values["DeviceVersion"] = spl[3]
        values["DeviceEventClassID"] = spl[4]
        values["DeviceName"] = spl[5]
        values["DeviceSeverity"] = spl[6]
        
        # The first value is actually the CEF version, formatted like
        # "CEF:#".  We split on the colon and use the second value as the
        # version number.
        (cef, version) = spl[0].split(':')
        values["CEFVersion"] = version

        # The ugly, gnarly regex here finds a single key=value pair,
        # taking into account multiple whitespaces, escaped '=' and '|'
        # chars.  It returns an iterator of tuples.
        spl = re.findall(r'([^=\s]+)=((?:[\\]=|[^=])+)(?:\s|$)', extension)
        for i in spl:
            # Split the tuples and put them into the dictionary
            values[i[0]] = i[1]

    # Now we're done!
    return values

###### Main ######
if len(sys.argv) != 2:
    print "USAGE: %s <file>" % sys.argv[0]
    sys.exit(-1)

file = sys.argv[1]

for line in open(file, "r").readlines():
    line = line.rstrip('\n')

    # Read the file, and parse each line of CEF into a separate JSON document
    # to stdout
    values = cef_parse(line)
    print json.dumps(values)

