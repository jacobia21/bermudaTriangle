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
import binascii
import datetime
import jinja2
import logging
import webapp2
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import ndb

env = jinja2.Environment(loader = jinja2.FileSystemLoader("templates"))

def get_user_info(path):
    cur_user = users.get_current_user()
    log_url = ''
    if cur_user:
        log_url = users.create_logout_url(path)
        name = cur_user.nickname().split('@')[0]
        user_id = ndb.Key('Profile',cur_user.nickname())
    else:
        log_url = users.create_login_url(path)
        name = 'none'
        user_id = 'none'
    return {
        "log_url": log_url,
        "user": cur_user,
        "username": name,
        "user_id": user_id
    }

def request_safely(page,property_name,default_value = '',backup_value = None):
    request = page.request.get(str(property_name))
    if request:
        return request
    else:
        if backup_value:
            return backup_value
        else:
            return default_value

def string2bool(boolStr):
    if boolStr in ['True','true','1']:
        return True
    elif boolStr in ['False','false','0']:
        return False
    else:
        return None

#data model classes

class Profile(ndb.Model):
    name = ndb.StringProperty()
    profile_pic = ndb.BlobProperty()
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
    profile_key = ndb.KeyProperty(Profile)

class PicturePost(ndb.Model):
    title = ndb.StringProperty()
    pic = ndb.BlobProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
    profile_key = ndb.KeyProperty(Profile)
    likes = ndb.IntegerProperty()

class Comment(ndb.Model):
    content = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
    discuss_post_key = ndb.KeyProperty(DiscussPost)
    pic_post_key = ndb.KeyProperty(PicturePost)
    profile_key = ndb.KeyProperty(Profile)

class Like(ndb.Model):
    pic_post_key = ndb.KeyProperty(PicturePost)
    profile_key = ndb.KeyProperty(Profile)
    time = ndb.DateTimeProperty(auto_now_add=True)


#basic page handler classes

class MainHandler(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/')

        query = PicturePost.query().order(-PicturePost.time)
        posts = query.fetch()

        post_pics = []
        for post in posts:
            if post.pic:
                post_pics.append("data:image;base64," + binascii.b2a_base64(post.pic))
            else:
                post_pics.append("")

        my_vars['posts'] = posts
        my_vars['post_pics'] = post_pics

        temp = env.get_template("homepage.html")
        self.response.out.write(temp.render(my_vars))

class DiscussionPage(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/discuss')

        query = DiscussPost.query().order(-DiscussPost.time)
        posts = query.fetch()
        my_vars['posts'] = posts

        temp = env.get_template("discussion.html")
        self.response.out.write(temp.render(my_vars))

class DiscussionPostHandler(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/discuss/post?id='+self.request.get('id'))

        post_key = ndb.Key(urlsafe=self.request.get('id'))
        post = post_key.get()

        if post:
            post.key = post_key

            query = Comment.query(Comment.discuss_post_key == post_key).order(-Comment.time)
            comments = query.fetch()

            my_vars['post'] = post
            my_vars['comments'] = comments

            temp = env.get_template("discussion_post.html")
            self.response.out.write(temp.render(my_vars))
        else:
            self.redirect('/discuss')

class ProfileHandler(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/all_profiles')
        user = my_vars['user']

        profile_key = ndb.Key(urlsafe=self.request.get('id'))
        profile = profile_key.get()

        if not profile:
            self.redirect('/edit_profile')

        if profile.profile_pic:
            pic = "data:image;base64," + binascii.b2a_base64(profile.profile_pic)
        else:
            pic = "../resources/dog_404.png"

        query = PicturePost.query(PicturePost.profile_key == profile_key).order(-PicturePost.time)
        posts = query.fetch()
        post_pics = []
        liked_posts = []

        for post in posts:
            if post.pic:
                post_pics.append("data:image;base64," + binascii.b2a_base64(post.pic))
            else:
                post_pics.append("")

            query = Like.query(Like.profile_key == profile_key, Like.pic_post_key==post.key)
            likes = query.fetch()
            if len(likes) > 0:
                liked_posts.append(post)


        my_vars['profile'] = profile
        my_vars['pic'] = pic
        my_vars['posts'] = posts
        my_vars['post_pics'] = post_pics
        my_vars['liked_posts'] = liked_posts

        temp = env.get_template("user_profile.html")
        self.response.out.write(temp.render(my_vars))
class EditProfile(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/')
        temp = env.get_template("edit_profile.html")
        self.response.out.write(temp.render(my_vars))

class MyProfile(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/profile')
        user = my_vars['user']
        if user:
            profile_key = ndb.Key('Profile',user.nickname())
            profile = profile_key.get()
            if not profile:
                profile = Profile(
                    name = user.nickname()
                )
            profile.key = profile_key
            profile.put()
            self.redirect('/profile?id='+profile_key.urlsafe())
        else:
            self.redirect('/')

class AllProfilesPage(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/all_profiles')

        query = Profile.query()
        profiles = query.fetch()
        my_vars['profiles'] = profiles

        temp = env.get_template("all_profiles.html")
        self.response.out.write(temp.render(my_vars))

class TestHeaderPage(webapp2.RequestHandler):
    def get(self):
        temp = env.get_template("test_headers.html")
        self.response.out.write(temp.render())
class AboutUsPage(webapp2.RequestHandler):
    def get(self):
        my_vars = get_user_info('/')
        temp = env.get_template("about.html")
        self.response.out.write(temp.render(my_vars))

#Datastore page handler classes

class DiscussPostMaker(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/')
        user = user_info['user']

        if not user:
            self.redirect('/discuss')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()
        if not profile:
            profile = Profile(
                name = user_info['username']
            )
        profile.key = profile_key
        profile.put()

        discuss_key = ndb.Key('DiscussPost',self.request.get('title')+str(datetime.datetime.now()))
        discuss_post = discuss_key.get()
        discuss_post = DiscussPost(
            title = self.request.get("title"),
            content = self.request.get("content"),
            profile_key = profile.key
        )
        discuss_post.key = discuss_key
        discuss_post.put()
        self.redirect('/discuss')

class CommentMaker(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/')
        user = user_info['user']

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()
        if not profile:
            profile = Profile(
                name = user_info['username']
            )
        profile.key = profile_key
        profile.put()

        post_key = ndb.Key(urlsafe=self.request.get('id'))
        post = post_key.get()

        post_type = self.request.get('post_type')

        if not post or not user:
            if post_type=='discuss':
                self.redirect('/discuss')
            else:
                self.redirect('/')

        comment_key = ndb.Key('Comment',self.request.get('content')+str(datetime.datetime.now()))
        comment = comment_key.get()
        comment = Comment(
            content = self.request.get('content'),
            profile_key = profile.key
        )
        if post_type == "discuss":
            comment.discuss_post_key = post_key
        comment.key = comment_key
        comment.put()
        if post_type == "discuss":
            self.redirect('/discuss/post?id='+self.request.get('id'))
        else:
            self.redirect('/')

class SaveProfileChanges(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/')
        user = user_info['user']

        if not user:
            self.redirect('/')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()

        if profile:
            profile = Profile(
                name = user_info['username'],
                dog_name = request_safely(self,'name','',profile.dog_name),
                age = request_safely(self,'age','',profile.age),
                breed = request_safely(self,'breed','',profile.breed),
                hometown = request_safely(self,'town','',profile.hometown),
                active = string2bool(request_safely(self,'active','false',profile.active)),
                fav_toy = request_safely(self,'fav_toy','',profile.fav_toy),
                bio = request_safely(self,'bio','',profile.bio),
                kid_friendly = string2bool(request_safely(self,'kid_friendly','false',profile.kid_friendly)),
                vaccinated = string2bool(request_safely(self,'vaccinated','false',profile.vaccinated))
            )
        else:
            profile = Profile(
                name = user_info['username'],
                dog_name = request_safely(self,'name'),
                age = request_safely(self,'age'),
                breed = request_safely(self,'breed'),
                hometown = request_safely(self,'hometown'),
                active = string2bool(request_safely(self,'active','false')),
                fav_toy = request_safely(self,'fav_toy'),
                bio = request_safely(self,'bio'),
                kid_friendly = string2bool(request_safely(self,'kid_friendly','false')),
                vaccinated = string2bool(request_safely(self,'vaccinated','false'))
            )
        profile.key = profile_key
        profile.put()

        self.redirect('/my_profile')

class UploadProfilePic(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/all_profiles')
        user = user_info['user']

        if not user:
            self.redirect('/all_profiles')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()

        img_bin = self.request.get('profile_pic')

        #img = images.Image(img_bin)
        #if img.width>200 or img.height>200:
        #    img.resize(200,200)
        #    img_bin = img.execute_transforms()


        if profile:
            profile.profile_pic = img_bin
            profile.key = profile_key
            profile.put()

        self.redirect('/my_profile')

class PicturePostMaker(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/all_profiles')
        user = user_info['user']

        if not user:
            self.redirect('/all_profiles')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()

        if not profile:
            profile = Profile(
                name = user_info['username']
            )
        profile.key = profile_key
        profile.put()

        pic_post_key = ndb.Key('PicturePost',self.request.get('title')+str(datetime.datetime.now()))
        pic_post = pic_post_key.get()
        pic_post = PicturePost(
            title = self.request.get('title'),
            pic = self.request.get('post_pic'),
            likes = 0,
            profile_key = profile.key,
        )
        pic_post.key = pic_post_key
        pic_post.put()
        self.redirect('/my_profile')

class LikePost(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/all_profiles')
        user = user_info['user']

        if not user:
            self.redirect('/')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()

        if not profile:
            profile = Profile(
                name = user_info['username']
            )
        profile.key = profile_key
        profile.put()

        post_key = ndb.Key(urlsafe=self.request.get('id'))
        post = post_key.get()
        post.likes = post.likes + 1
        post.put()

        like_key = ndb.Key('Like',post.title+user.nickname()+str(datetime.datetime.now()))
        like = Like(
            pic_post_key = post_key,
            profile_key = profile.key
        )
        like.key = like_key
        like.put()

        url = self.request.get("url")
        uid = self.request.get("uid")
        if uid:
            self.redirect("/"+url+"?id="+uid)
        else:
            self.redirect("/"+url)

class UnlikePost(webapp2.RequestHandler):
    def post(self):
        user_info = get_user_info('/all_profiles')
        user = user_info['user']

        if not user:
            self.redirect('/')

        profile_key = ndb.Key('Profile',user.nickname())
        profile = profile_key.get()

        if not profile:
            profile = Profile(
                name = user_info['username']
            )
        profile.key = profile_key
        profile.put()

        post_key = ndb.Key(urlsafe=self.request.get('id'))
        post = post_key.get()

        query = Like.query(Like.profile_key == profile_key, Like.pic_post_key==post.key)
        likes = query.fetch()
        for like in likes:
            post.likes = post.likes - 1
            like.key.delete()
        post.put()

        url = self.request.get("url")
        uid = self.request.get("uid")
        if uid:
            self.redirect("/"+url+"?id="+uid)
        else:
            self.redirect("/"+url)

class CustomQuery(webapp2.RequestHandler):
    def get(self):

        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/discuss', DiscussionPage),
    ('/discuss/post', DiscussionPostHandler),
    ('/profile', ProfileHandler),
    ('/profile/edit', EditProfile),
    ('/all_profiles', AllProfilesPage),
    ('/my_profile', MyProfile),
    ('/about_us', AboutUsPage),

    ('/discuss/makepost', DiscussPostMaker),
    ('/discuss/send_comment', CommentMaker),

    ('/profile/submit_changes', SaveProfileChanges),
    ('/profile/upload_profile_pic', UploadProfilePic),
    ('/profile/upload_photos', PicturePostMaker),

    ('/likepost', LikePost),
    ('/unlikepost', UnlikePost),

    ('/test_headers', TestHeaderPage),
    ('/run_query', CustomQuery)
], debug=True)
