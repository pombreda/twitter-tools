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
# FIXME this code is a quick ugly hack

import os, sys, re, json, ConfigParser, tweepy

dirsrc = os.path.dirname(os.path.abspath(__file__))

def get_data_from_file(filename, default):
    fname = os.path.join(dirsrc, filename)
    if os.path.exists(fname):
        with open(fname, 'r') as f:
            return json.load(f)
    return default

def write_data_to_file(filename, data):
    fname = os.path.join(dirsrc, filename)
    with open(fname, 'w') as f: json.dump(data, f)

if 2 != len(sys.argv):
    print('Usage\n%s "search term"' % sys.argv[0])
    sys.exit()

search_term = sys.argv[1].strip().lower()
basename = unicode(re.sub('[^\w-]', '-', search_term))
id_file = basename + '_ids.json'
tweet_file = basename + '_tweets.json'
ids = get_data_from_file(id_file, {})
tweets = get_data_from_file(tweet_file, [])
new_tweet_count = 0

config = ConfigParser.ConfigParser()
config.readfp(open(os.path.join(dirsrc, 'collect_tweet_search.cfg')))

auth = tweepy.OAuthHandler(config.get('twitter', 'CONSUMER_KEY'), config.get('twitter', 'CONSUMER_SECRET'))
auth.set_access_token(config.get('twitter', 'ACCESS_TOKEN'), config.get('twitter', 'ACCESS_TOKEN_SECRET'))
api = tweepy.API(auth)

def proc_tweets():
    global new_tweet_count
    for page in tweepy.Cursor(api.search, search_term, include_entities=1, count=200, include_rts=True).pages():
        for tweet in page:
            # must use id string because of json encoding
            if tweet.id_str in ids:
                return # suppose all subsequent tweets have been seen already
            ids[tweet.id_str] = 1
            td = tweet.__dict__
            td['created_at'] = str(td['created_at'])
            tweets.append(td)
            new_tweet_count += 1

proc_tweets()

print('Added %d new tweets' % new_tweet_count)

write_data_to_file(id_file, ids)
write_data_to_file(tweet_file, tweets)
