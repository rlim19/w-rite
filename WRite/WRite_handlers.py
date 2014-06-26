#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from google.appengine.ext import db
import time

class WRite(basehandler.BaseHandler):
    def get(self):
        self.render('WRite.html')

