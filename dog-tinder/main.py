#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import jinja2
import webapp2

env = jinja2.Environment(loader = jinja2.FileSystemLoader("templates"))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        temp = env.get_template("homepage.html")
        self.response.out.write(temp.render())

class DiscussionPage(webapp2.RequestHandler):
    def get(self):
        temp = env.get_template("discussion.html")
        self.response.out.write(temp.render())

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        temp = env.get_template("user_profile.html")
        self.response.out.write(temp.render())

class UserProfile(webapp2.RequestHandler):
    def get(self):
        self.redirect('/profile')

class AllProfilesPage(webapp2.RequestHandler):
    def get(self):
        temp = env.get_template("all_profiles.html")
        self.response.out.write(temp.render())


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/discuss', DiscussionPage),
    ('/profile', ProfileHandler),

    ('/my_profile', UserProfile),
    ('/all_profiles', AllProfilesPage),
], debug=True)
