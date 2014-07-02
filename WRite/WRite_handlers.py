#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from models.notemodels import *
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import time
import logging
from glocation import *


def display_notes(userID, update=False):
    """
    display notes implemented with CAS (Check and Set)
    """

    memc = memcache.Client()
    key = 'top' 

    while True: 
        notes = memc.gets(key)

        if notes is None or update:
            #logging.error('DB Query')
            notes = db.GqlQuery("SELECT * FROM Note "
                                "WHERE ANCESTOR is :1 AND userID = :2 "
                                "ORDER BY created DESC " , 
                                note_key, userID)
            notes = list(notes)
            memc.add(key, notes)

        assert notes is not None, "Uninitialized notes"
        if memc.cas(key, notes):
            #logging.error('Test cas pass')
            break

    return notes

class WRite(basehandler.BaseHandler, IpLocation):
    def render_write(self,logout='',name='',title='',note='',error=''):

        user = users.get_current_user()
        userID = user.user_id()
        name = user.nickname()
        logout = users.create_logout_url("/") 
        notes = display_notes(userID = userID)

        points = filter(None, (n.coords for n in notes))

        img_url = None
        if points:
            img_url = gmaps_img(points)

        self.render("WRite.html",
                    name = name, title = title, 
                    note = note, error = error, 
                    notes = notes, logout = logout, img_url = img_url)

    def get(self):
        self.render_write()

    def post(self):
        # post the note of the active user only
        user = users.get_current_user()
        if user:
            userName = user.nickname()
            userID = user.user_id()
            userEmail = user.email()
            title = self.request.get('title')
            note = self.request.get('note')

            if title and note:
                NOTE = Note(parent=note_key, userID = userID, 
                            userEmail = userEmail, userName = userName, 
                            title = title, note = note)
                loc = IpLocation(self.request.remote_addr)
                loc_xml = loc.get_xml()
                coords = loc_xml.get_coords()
                city = loc_xml.get_city()
                country = loc_xml.get_country()

                if coords:
                    NOTE.coords = coords
                if city:
                    NOTE.city = city
                if country:
                    NOTE.country = country

                NOTE.put()
                display_notes(update=True, userID = userID)
                #time.sleep(1)
                self.redirect('/')
            else:
                error = "Please enter a title and a note"
                self.render_write(title = title, 
                                  note = note, 
                                  error = error, 
                                  name = name)
