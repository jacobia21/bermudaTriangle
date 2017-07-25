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
import datetime
import jinja2
import logging
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb

env = jinja2.Environment(loader = jinja2.FileSystemLoader("templates"))

def getUserInfo(path):
    cur_user = users.get_current_user()
    log_url = ''
    if cur_user:
        log_url = users.create_logout_url(path)
        name = cur_user.nickname().split('@')[0]
    else:
        log_url = users.create_login_url(path)
        name = 'none'
    return {
        "log_url": log_url,
        "user": cur_user,
        "username": name
    }

def requestSafely(page,property_name,default_value = '',backup_value = None):
    request = page.request.get(str(property_name))
    if request:
        return request
    else:
        if backup_value:
            return backup_value
        else:
            return default_value


#data model classes

class User(ndb.Model):
    name = ndb.StringProperty()
    dog_name = ndb.StringProperty()
    age = ndb.StringProperty()
    breed = ndb.StringProperty()
    hometown = ndb.StringProperty()
    active = ndb.BooleanProperty()
    fav_toy = ndb.StringProperty()
    bio = ndb.StringProperty()
    kid_friendly = ndb.BooleanProperty()
    vaccinated = ndb.BooleanProperty()

class DiscussPost(ndb.Model):
    title = ndb.StringProperty()
    content = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
    user_key = ndb.KeyProperty(User)


#basic page handler classes

class MainHandler(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/')
        temp = env.get_template("homepage.html")
        self.response.out.write(temp.render(my_vars))

class DiscussionPage(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/discuss')

        query = DiscussPost.query().order(-DiscussPost.time)
        posts = query.fetch()
        logging.info(posts)
        my_vars['posts'] = posts

        temp = env.get_template("discussion.html")
        self.response.out.write(temp.render(my_vars))

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/')
        user = my_vars['user']

        profile = ndb.Key('User',user.nickname()).get()
        my_vars['profile'] = profile

        temp = env.get_template("user_profile.html")
        self.response.out.write(temp.render(my_vars))

class EditProfile(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/')
        temp = env.get_template("edit_profile.html")
        self.response.out.write(temp.render(my_vars))

class MyProfile(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/profile')
        user = my_vars['user']
        if user:
            self.redirect('/profile')
        else:
            self.redirect('/')

class AllProfilesPage(webapp2.RequestHandler):
    def get(self):
        my_vars = getUserInfo('/all_profiles')
        temp = env.get_template("all_profiles.html")
        self.response.out.write(temp.render(my_vars))


#Datastore page handler classes

class DiscussPostMaker(webapp2.RequestHandler):
    def post(self):
        user_info = getUserInfo('/')
        user = user_info['user']

        if not user:
            self.redirect('/discuss')

        user_key = ndb.Key('User',user.nickname())
        user_ent = user_key.get()
        if not user_ent:
            user_ent = User(
                name = user_info['username']
            )
        user_ent.key = user_key
        user_ent.put()

        discuss_key = ndb.Key('DiscussPost',self.request.get('title')+str(datetime.datetime.now()))
        discuss_post = discuss_key.get()
        discuss_post = DiscussPost(
            title = self.request.get("title"),
            content = self.request.get("content"),
            user_key = user_ent.key
        )
        discuss_post.key = discuss_key
        discuss_post.put()
        self.redirect('/discuss')

class SaveProfileChanges(webapp2.RequestHandler):
    def post(self):
        user_info = getUserInfo('/')
        user = user_info['user']

        if not user:
            self.redirect('/')

        user_key = ndb.Key('User',user.nickname())
        user_ent = user_key.get()

        logging.info(self.request.get('foo'))
        logging.info(requestSafely(self,'foo'),'',user_ent)
        if user_ent:
            user_ent = User(
                name = user_info['username'],
                dog_name = requestSafely(self,'name','',user_ent.dog_name),
                age = requestSafely(self,'age','',user_ent.age),
                breed = requestSafely(self,'breed','',user_ent.breed),
                hometown = requestSafely(self,'town','',user_ent.hometown),
                active = requestSafely(self,'active','false',user_ent.active)=='true',
                fav_toy = requestSafely(self,'fav_toy','',user_ent.fav_toy),
                bio = requestSafely(self,'bio','',user_ent.bio),
                kid_friendly = requestSafely(self,'kid_friendly','false',user_ent.kid_friendly)=='true',
                vaccinated = requestSafely(self,'vaccinated','false',user_ent.vaccinated)=='true'
            )
        else:
            user_ent = User(
                name = user_info['username'],
                dog_name = requestSafely(self,'name'),
                age = requestSafely(self,'age'),
                breed = requestSafely(self,'breed'),
                hometown = requestSafely(self,'hometown'),
                active = requestSafely(self,'active','false')=='true',
                fav_toy = requestSafely(self,'fav_toy'),
                bio = requestSafely(self,'bio'),
                kid_friendly = requestSafely(self,'kid_friendly','false')=='true',
                vaccinated = requestSafely(self,'vaccinated','false')=='true'
            )
        user_ent.key = user_key
        user_ent.put()

        self.redirect('/my_profile')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/discuss', DiscussionPage),
    ('/profile', ProfileHandler),
    ('/profile/edit', EditProfile),
    ('/all_profiles', AllProfilesPage),
    ('/my_profile', MyProfile),

    ('/discuss/makepost', DiscussPostMaker),
    ('/profile/submit_changes', SaveProfileChanges),
], debug=True)
