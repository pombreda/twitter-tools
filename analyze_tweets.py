# -*- coding: utf-8 -*-
import os
import sys
import redis
import re
import operator
from tweet_stats import TweetStats

redis_server = redis.Redis("localhost")

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


def print_format_stats(tweet_stats):
    """Print formatted tweet_stats."""

    for k in tweet_stats:
        print "\n######### Index: %s #########\n" % k

        k_stats = tweet_stats[k]
        k_stats_sorted = sorted(k_stats.iteritems(), key=operator.itemgetter(1), reverse=True)[0:10]

        cnt = 0
        for val, card in k_stats_sorted:
            cnt += 1
            print "%4d %-60s %5d" % (cnt, val, card)


if len(sys.argv) > 1:
    query = sys.argv[1]
    tweet_set_name = "tweets:%s" % query
    ts = TweetStats()
    ts.write_stats(os.curdir)

#    tweets = list(redis_server.smembers("tweets:%s" % query))
#    subset = set(tweets[0:10])
#    for t in subset:

    for i in range(1000):
        tweet = redis_server.srandmember(tweet_set_name)
        ts.update(tweet_str_to_dict(tweet))

    print_format_stats(ts['stats'])

else:
    print 'Usage: %s "query string"' % sys.argv[0]
