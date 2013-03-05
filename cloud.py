import json as simplejson
import cgi
import datetime
import urllib
import webapp2
import random
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.api import users
import jinja2
import os
import unicodedata 

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Buzz(db.Model):
  user_name = db.StringProperty()
  search_keyword = db.StringProperty()  
  value = db.StringProperty()

def searchTweets(query):
 query=str(query)
 search = urllib.urlopen("http://search.twitter.com/search.json?q="+query+"&rpp=30&lang=en")
 dict = simplejson.loads(search.read())
 return dict["results"] 


def analysisTweets(query):
 search = urllib.urlopen("http://www.sentiment140.com/api/classify?text="+query)
 dict = simplejson.loads(search.read())
 return dict["results"]["polarity"]
class MainPage(webapp2.RequestHandler):
  def get(self):
    if users.get_current_user():
      currentUser=users.get_current_user().nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      currentUser="DefaultUser"
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
    dict={}  
    template_values = {
      'currentUser': currentUser,
      'url': url,
      'url_linktext': url_linktext,
      'keyword': "null",
      'answer': 0,
      'dict': dict,
    }
    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))
  
class ShowResult(webapp2.RequestHandler):
  def post(self):
    if users.get_current_user():
      currentUser=users.get_current_user().nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      currentUser="DefaultUser"
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'  
    keyword = self.request.get("content")
    dict = searchTweets(keyword)
    stas = {'negative':0,'neutral':0,'positive':0}    
    num=0
    for curtext in dict: 
      curtext["text"] = curtext["text"].replace('\'','').replace('"','').replace('#','')
      ascii = unicodedata.normalize('NFKD',curtext["text"]).encode('ascii', 'ignore')
      try:
        ans = analysisTweets(ascii)         
        if ans == 0:
          stas['negative'] = stas['negative'] + 1
        elif ans == 2:
          stas['neutral'] = stas['neutral'] + 1
        else:
          stas['positive'] = stas['positive'] + 1  
      except:
        num = num + 1               
    max=0
    for x in stas.keys():
      if stas[x] > max:
        max = stas[x]
        max_key = x     
    buzz = Buzz(user_name=currentUser,search_keyword=keyword,value=max_key) 
    buzz.put()
    template_values = {
      'currentUser': currentUser,
      'url': url,
      'url_linktext': url_linktext,
      'keyword': keyword,
      'dict': dict,
      'stas': stas,
      'num': num,
    }
    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))
    
    
class ShowBuzz(webapp2.RequestHandler):
  def get(self):    
    if users.get_current_user():
      currentUser=users.get_current_user().nickname()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      currentUser="DefaultUser"
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
    buzzQuery=Buzz.all()  
    template_values = {
      'currentUser': currentUser,
      'url': url,
      'url_linktext': url_linktext,
      'buzzQuery': buzzQuery,
    }  
    template = jinja_environment.get_template('buzz.html')
    self.response.out.write(template.render(template_values))
app = webapp2.WSGIApplication([('/',MainPage),('/search', ShowResult),('/buzz',ShowBuzz)],
                              debug=True)
