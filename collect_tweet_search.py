# coding: utf-8
# A command line tool to persist tweets in json files over time.
# The program is called with a search term as it's 1st argument.
#
# Two files will be created SEARCHTERM_ids.json and SEARCHTERM_tweets.json
# The *_ids.json file stores only the tweet ids and serves as a lookup data
# structure to make sure tweets are stored only once in the actual *_tweets.json
# file that contain all found tweets.
#
# Tweet ids are stored in a dict and tweets in a list.

import sys, re, tweepy

if 2 != len(sys.argv):
    print('Usage\n%s "search term"' % sys.argv[0])
    sys.exit()

search_term = sys.argv[1].strip().lower()
basename = unicode(re.sub('[^\w-]', '-', search_term))
id_file = basename + '_ids.json'
tweet_file = basename + '_tweets.json'

print (id_file, tweet_file)
