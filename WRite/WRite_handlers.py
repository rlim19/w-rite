#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from google.appengine.ext import db
import time

class Note(db.Model):
    title = db.StringProperty(required = True)
    note = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class WRite(basehandler.BaseHandler):
    def render_write(self, title = '', note = '', error = ''):
        notes = db.GqlQuery("SELECT * FROM Note "
                            "ORDER BY created DESC ")
        self.render("WRite.html", 
                    title = title, note = note, error = error, notes = notes)
    def get(self):
        self.render_write()

    def post(self):
        title = self.request.get('title')
        note = self.request.get('note')

        if title and note:
            NOTE = Note(title = title, note = note)
            NOTE.put()
            time.sleep(1)
            self.redirect('/')
        else:
            error = "Please enter a title and a note"
            self.render_write(title = title, note = note, error = error)


