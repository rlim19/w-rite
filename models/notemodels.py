#! /usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import db

note_key = db.Key.from_path('WRite', 'notes')

class Note(db.Model):
    userID = db.StringProperty(required = True)
    userName = db.StringProperty()
    userEmail = db.StringProperty(required = True)
    title = db.StringProperty(required=True)
    note = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    coords = db.GeoPtProperty()
    city = db.StringProperty()
    country = db.StringProperty()
