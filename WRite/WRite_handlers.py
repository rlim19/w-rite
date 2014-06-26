#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from google.appengine.ext import db
from google.appengine.api import users
import time

class Note(db.Model):
    userid = db.StringProperty(required = True)
    title = db.StringProperty(required = True)
    note = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class WRite(basehandler.BaseHandler):
    def render_write(self, logout='', name='', title='', note='', error=''):

        user = users.get_current_user()
        name = user.nickname()
        logout = users.create_logout_url("/") 

        # queries the note of the active user's id
        notes = db.GqlQuery("SELECT * FROM Note "
                            "WHERE userid = :1 "
                            "ORDER BY created DESC " , user.user_id())

                            #"ORDER BY created DESC "
                            #"WHERE userid = :1 ", user.user_id())
        self.render("WRite.html",
                    name = name, title = title, 
                    note = note, error = error, 
                    notes = notes, logout = logout)

    def get(self):
        self.render_write()

    def post(self):
        # post the note of the active user only
        user = users.get_current_user()
        if user:
            name = user.nickname()
            userid = user.user_id()
            title = self.request.get('title')
            note = self.request.get('note')

            if title and note:
                NOTE = Note(userid = userid, title = title, note = note)
                NOTE.put()
                time.sleep(1)
                self.redirect('/')
            else:
                error = "Please enter a title and a note"
                self.render_write(title = title, note = note, error = error, name = name)
        else:
            self.write("error")
