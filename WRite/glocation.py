#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
from xml.dom import minidom
from google.appengine.ext import db

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
        content = urllib2.urlopen(self.url).read()
        content = None
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
