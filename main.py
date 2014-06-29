#!/usr/bin/env python

import os
import webapp2
import jinja2
from WRite import WRite_handlers


#DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

app = webapp2.WSGIApplication([
    ('/', WRite_handlers.WRite),
], debug=False)
