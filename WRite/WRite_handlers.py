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
from datetime import datetime, timedelta


def get_notes(userID, update=False):
    """
    display notes implemented with CAS (Check and Set)
    age = age of cache
    """
    memc = memcache.Client()
    key = 'NOTES' 

    while True: 
    #for i in xrange(1,10):
        r = memc.gets(key)
        if r:
            #logging.error('age computed')
            notes, save_time = r
            age = (datetime.utcnow() - save_time). total_seconds()
        else:
            notes, age = None, 0 
            logging.error('initialized')

        if notes is None or update:
            logging.error('DB Query')
            notes = db.GqlQuery("SELECT * FROM Note "
                                "WHERE ANCESTOR is :1 AND userID = :2 "
                                "ORDER BY created DESC " , 
                                note_key, userID)

            notes = list(notes)
            save_time = datetime.utcnow()
            memc.add(key, (notes, save_time))
            

        assert notes is not None, "Uninitialized notes"
        if memc.cas(key, (notes, save_time)):
            #logging.error('Test cas pass')
            break
        #logging.error('Loop hell')


    return notes, age

def age_str(age):
    s = 'Queried %s seconds ago'
    age = int(age)
    if age == 1:
        s = s.replace('seconds', 'second')
    return s % age

class WRite(basehandler.BaseHandler, IpLocation):
    def render_write(self,logout='',name='',title='',note='',error=''):

        user = users.get_current_user()
        userID = user.user_id()
        name = user.nickname()
        logout = users.create_logout_url("/") 
        notes, age = get_notes(userID = userID)

        points = filter(None, (n.coords for n in notes))

        img_url = None
        if points:
            img_url = gmaps_img(points)

        self.render("WRite.html",
                    name = name, title = title, 
                    note = note, error = error, 
                    notes = notes, logout = logout, 
                    img_url = img_url, age= age_str(age))

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
                get_notes(userID = userID, update=True)
                #time.sleep(1)
                self.redirect('/')
            else:
                error = "Please enter a title and a note"
                self.render_write(title = title, 
                                  note = note, 
                                  error = error, 
                                  name = name)
