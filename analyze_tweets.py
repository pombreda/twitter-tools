# -*- coding: utf-8 -*-
import sys
import twitter_text
import redis
import re

redis_server = redis.Redis("localhost")
urls = {}
hashtags = {}
from_users = {}
to_users = {}
mentioned_users = {}

tpl_field_value = "u'%s': u?'?(.*?)'?, u'%s': "
re_hex_code = re.compile('\\\\x[0-9a-z]{2}')
tweet_fields = ['iso_language_code', 'to_user_id_str', 'text', 'from_user_id_str', 'profile_image_url', 'id', 'source', 'id_str', 'from_user', 'from_user_id', 'to_user_id', 'geo', 'created_at', 'metadata']


def tweet_str_to_dict(s):
    """Convert python tweet string to dict

    Redis stores JSON strings as Python strings in sets using single quotes, not 
    quoting None, integers and long integers, and using hexadecimal character 
    codes for non ASCII chars, which poses problems to json.loads. This is a
    workaround.
    """

    global tpl_field_value, tweet_fields, re_hex_code
    tweet_dict = {}
    for i in range(0,len(tweet_fields)-1):
        curr_field = tweet_fields[i]
        regex = tpl_field_value % (curr_field, tweet_fields[i+1])
        m = re.search(regex, s)
        if m is not None:
            val = m.group(1)

            #TODO convert hex codes
            #if re.search(re_hex_code, val):
                #val = val.decode('iso-8859-1')

            # convert None string to None object
            if "None" == val:
                val = None

            tweet_dict[curr_field] = val

    return tweet_dict


def get_entities(text):
    """modified from https://github.com/ptwobrussell/Mining-the-Social-Web/blob/master/python_code/the_tweet__extract_tweet_entities.py
    """

    extractor = twitter_text.Extractor(text)

    entities = {}
    entities['user_mentions'] = []
    for um in extractor.extract_mentioned_screen_names_with_indices():
        entities['user_mentions'].append(um)

    entities['hashtags'] = []
    for ht in extractor.extract_hashtags_with_indices():

        # massage field name to match production twitter api
        ht['text'] = ht['hashtag']
        del ht['hashtag']
        entities['hashtags'].append(ht)

    entities['urls'] = []
    for url in extractor.extract_urls_with_indices():
        entities['urls'].append(url)

    return entities


if len(sys.argv) > 1:
    query = sys.argv[1]
    tweets = list(redis_server.smembers("tweets:%s" % query))
    subset = set(tweets[0:1])

    for t in subset:
        print tweet_str_to_dict(t)
#        jt = json.loads(fix_str(t))
#        print jt['text']
#        print getEntities(jt)

else:
    print 'Usage: %s "query string"' % sys.argv[0]

#{u'iso_language_code': u'en', u'to_user_id_str': None, u'text': u'PCMS 4n1 Combo - MSI Wind U100-641US 10-Inch Netbook Carrying Bag with AC and DC Adapter Charger Home / Car / A... http://amzn.to/f2wssq', u'from_user_id_str': u'104656176', u'profile_image_url': u'http://a2.twimg.com/profile_images/771807838/sleeper-chairs-03-300x146_normal.jpg', u'id': 56183119782477824L, u'source': u'&lt;a href=&quot;http://twitterfeed.com&quot; rel=&quot;nofollow&quot;&gt;twitterfeed&lt;/a&gt;', u'id_str': u'56183119782477824', u'from_user': u'sleeperchairs', u'from_user_id': 104656176, u'to_user_id': None, u'geo': None, u'created_at': u'Fri, 08 Apr 2011 02:34:34 +0000', u'metadata': {u'result_type': u'recent'}}
