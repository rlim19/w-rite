#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler
from models.notemodels import *
from google.appengine.ext import db
from google.appengine.api import users
import time
import urllib2
from xml.dom import minidom

IP_URL = "http://api.hostip.info/?ip="
class IpLocation(object):
    def __init__(self, ip):
        #ip = "4.2.2.2" # for a test!
        #ip = "23.24.209.141"
        #ip = "114.4.23.119"
        #ip = "23.24.209.141"
        self.ip = ip
        self.url = IP_URL + self.ip
    def get_xml(self):
        content = None
        content = urllib2.urlopen(self.url).read()
        try: 
            content = urllib2.urlopen(self.url).read()
        except URLError:
            return
        if content:
            self.xml = minidom.parseString(content)
            return self
    def get_coords(self):
        coords = self.xml.getElementsByTagName("gml:coordinates")
        if coords and coords[0].firstChild.nodeValue:
            lan, lat = coords[0].firstChild.nodeValue.split(',')
            return db.GeoPt(lat, lan)
    def get_city(self):
        city = self.xml.getElementsByTagName("gml:name")[1].firstChild.nodeValue 
        return city

    def get_country(self):
        country = self.xml.getElementsByTagName("countryName")[0].firstChild.nodeValue
        return country



GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=800x800&scale=1&sensor=false&"
def gmaps_img(points):
    """
    Generate static google map with markers 
    """
    markers = '&'.join('markers=%s,%s' %(p.lat, p.lon) for p in points)
    return GMAPS_URL + markers

class WRite(basehandler.BaseHandler, IpLocation):
    def render_write(self, logout='', name='', title='', note='', error=''):

        user = users.get_current_user()
        name = user.nickname()
        logout = users.create_logout_url("/") 

        # queries the note of the active user's id
        notes = db.GqlQuery("SELECT * FROM Note "
                            "WHERE ANCESTOR is :1 AND userID = :2 "
                            "ORDER BY created DESC " , note_key, user.user_id())

        notes = list(notes)

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
            name = user.nickname()
            userID = user.user_id()
            userEmail = user.email()
            title = self.request.get('title')
            note = self.request.get('note')

            if title and note:
                NOTE = Note(parent=note_key, userID = userID, userEmail = userEmail, 
                            title = title, note = note)
                #coords = get_coords(self.request.remote_addr)
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
                time.sleep(1)
                # city and country rendered directly to the templates, check template!
                self.redirect('/')
            else:
                error = "Please enter a title and a note"
                self.render_write(title = title, note = note, error = error, name = name)
        else:
            self.write("error")
