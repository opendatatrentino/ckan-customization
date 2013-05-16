#!/usr/bin/python

from twython import Twython, TwythonError

import re 
import codecs

# -------------------------- #
#          Parametri            
# -------------------------- #

APP_KEY='EtyftSKWzog9LjNE50g'
APP_SECRET='7MptO9zzAz231diK75aFV2pu5nmxy9sefWCcZ7FJA'
OAUTH_TOKEN='1417803013-8ubWGlXFiqahoipwqyJ1YapsR1ONbrz0oviyafs'
OAUTH_TOKEN_SECRET='z1Uu2dPVwzphRz8imRZPIFoKSFO3m1fK3d5sw4SAL0Q'

searchString = u'#opendata'
fileout = '/home/ckan/pyenv/src/ckan/my-templates/home/twitterstream.html'

hash_regex = re.compile(r'#[0-9a-zA-Z+_]*',re.IGNORECASE)   
user_regex = re.compile(r'@[0-9a-zA-Z+_]*',re.IGNORECASE)  

templLi = u"""<li>
<div class="tw-user">
<img width= "40" height="40" src="%s"  alt="%s" />
</div>
<div class="tweet">
<h4>%s</h4>
    %s - <a href="https://twitter.com/%s/status/%s" target="_new">vai </a>
</div> 
</li>
"""

# -------------------------- #
#     function CleanText            
# -------------------------- #

def cleanText (string):
    return (u' '.join(string.split()))
    

# -------------------------- #
#  function parse_tweet           
# -------------------------- #

def parse_tweet(tweet):  
 
    #first deal with links. Any http://... string change to a proper link  
    tweet = re.sub('http://[^ ,]*', lambda t: '<a href="%s" target="_new">%s</a>' % (t.group(0), t.group(0)), tweet)  
          
    #for all elements matching our pattern...  
    for usr in user_regex.finditer(tweet):  
            
        #for each whole match replace '@' with ''  
        url_tweet = usr.group(0).replace('@','')  
  
        tweet = tweet.replace(usr.group(0),  
                '<em>'+usr.group(0)+'</em>')  
  
    for hash in hash_regex.finditer(tweet):  
        url_hash = hash.group(0).replace('#','%23')  
        if len ( hash.group(0) ) > 2:  
            tweet = tweet.replace(hash.group(0),  
                    '<em>'+hash.group(0)+'</em>');   
      
    return tweet 

# -------------------------- #
#            main            
# -------------------------- #

try:
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    search_results = twitter.search(q=searchString, lang="it", rpp=4)
    res = search_results['statuses'][:4]
except TwythonError as e:
    print e

fout = codecs.open(fileout, encoding='utf-8', mode='w') 
fout.write("<ul>\n")
for item in res:
    out = templLi % (cleanText(item['user']['profile_image_url']), 
        cleanText(item['user']['name']), 
        cleanText(item['user']['name']), 
        parse_tweet(cleanText(item['text'])),
        cleanText(item['user']['screen_name']),
        cleanText(str(item['id']))) 
        
    fout.write(out)
    fout.write('\n')

fout.write("</ul>\n")
fout.flush()
fout.close()

