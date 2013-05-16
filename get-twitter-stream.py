#!/usr/bin/python

from twython import Twython

import re 
import codecs

# -------------------------- #
#          Parametri            
# -------------------------- #

#searchString = u'#opendata'
#searchString = u'#opendata +exclude:retweets'
#searchString = u'#opendataitaly OR #opendatatrentino OR opendata +exclude:retweets'
searchString = u'#opendatatrentino OR #opendataitaly +exclude:retweets'

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
    twitter = Twython()
    search_results = twitter.search(q=searchString, lang="it", page="1")
    res = search_results['results'][:4]
except:
    res = [{u'text': u'RT @TechEcon: @stefanoepifani @diritto2punto0 OpenLinks #3: Italia, Canada, Cile, Stati Uniti e India per l\u2019Open government #opendata http://t.co/joPb1xmo', 
        u'from_user_name': u'Angela Creta', 
        u'profile_image_url': u'http://a0.twimg.com/profile_images/2199018188/twett_normal.jpg', 
        u'id': '227696029972180992', 
        u'from_user': u'AngelaCreta'}, 
        {u'text': u'OpenLinks #3: Italia, Canada, Cile, Stati Uniti e India per l\u2019Open government http://t.co/qSku63IL via @techecon #opengov #opendata', 
        u'from_user_name': u'Francesco Minazzi', 
        u'profile_image_url': u'http://a0.twimg.com/profile_images/2215883092/image_normal.jpg', 
        u'id': '227688271390588928', 
        u'from_user': u'FraMinazzi' 
        },
        {u'text': u'@stefanoepifani @diritto2punto0 OpenLinks #3: Italia, Canada, Cile, Stati Uniti e India per l\u2019Open government #opendata http://t.co/joPb1xmo', 
        u'from_user_name': u'Tech Economy', 
        u'profile_image_url': u'http://a0.twimg.com/profile_images/1710115074/logo_moebius_piccolo_normal.jpg', 
        u'id': '227684556583604224', 
        u'from_user': u'TechEcon'}]   

fout = codecs.open(fileout, encoding='utf-8', mode='w') 
fout.write("<ul>\n")
for item in res:

    out = templLi % (cleanText(item['profile_image_url']), 
        cleanText(item['from_user_name']), 
        cleanText(item['from_user_name']), 
        parse_tweet(cleanText(item['text'])),
        cleanText(item['from_user']),
        cleanText(str(item['id']))) 
        
    fout.write(out)
    fout.write('\n')

fout.write("</ul>\n")
fout.flush()
fout.close()

