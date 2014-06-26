#! /usr/bin/env python
# -*- coding: utf-8 -*-

from basehandler import basehandler

class Login(basehandler.BaseHandler):
    def render_login(self, email="", password=""):
        self.render('login.html', email = email, 
                                  password = password)
    def get(self):
        #self.write('hello world')
        self.render_login()

