# -*- coding: utf-8 -*-
import sys
import re
import time
import calendar
import twitter
import redis

redis_server = redis.Redis("localhost")
re_non_word = re.compile("\W+")
re_uri = re.compile("https?://\S+")

def get_phrase_list(words, length):
    """Get a list of word lists from given list of words of the given length.
    
    Returns list of lists or None if length of given list is less than given length."""

    if len(words) >= length:
        return [words[i:i+length] for i in range(len(words) - length + 1)]
    else:
        return None

def proc_tweet(tweet, query):
    """Process a single tweet.
    
    Determines single words, word pairs, and word triples and stores them with
    counts in corresponding ordered sets in redis."""

    global redis_server, re_non_word

    # remove URIs
    text = re.sub(re_uri,"", tweet['text'])

    # lower case string and remove non word characters
    text = re.sub(re_non_word, " ",  text.lower()).strip()

    words = text.split()

    # process single words
    for word in words:
        print word, redis_server.zincrby("words:%s" % query, word, 1)

    # process 2 word lists
    pairs = get_phrase_list(words, 2)
    if pairs is not None:
        for word_pair in get_phrase_list(words, 2):
            print word_pair, redis_server.zincrby("word_pairs:%s" % query, word_pair, 1)

    # process 3 word lists
    triples = get_phrase_list(words, 3)
    if triples is not None:
        for word_triple in get_phrase_list(words, 3):
            print word_triple, redis_server.zincrby("word_triples:%s" % query, word_triple, 1)

def search_tweets(query, query_count, rpp):
    """Searches twitter for given query and collects results of processing in redis.
    
    Stops processing when all tweets on a result page have been processed in a
    previous request to avoid unnecessary Twitter API requests."""

    global redis_server
    twitter_search = twitter.Twitter(domain="search.twitter.com")
    for page in range(1, query_count + 1):
        tweets_seen_before = 0
        try:
            result = twitter_search.search(q=query, rpp=rpp, page=page)
        except:
            continue
        else:
            for tweet in result['results']:
                # make sure the tweet has not been processed yet
                if redis_server.sadd("tweet_ids:%s" % query, tweet['id']):
                    # store tweet in a set of tweets
                    redis_server.sadd("tweets:%s" % query, tweet)

                    # store tweet dates in an ordered set of dates
                    created_at = tweet['created_at']
                    created_struct_time = time.strptime(created_at, "%a, %d %b %Y %H:%M:%S +0000")
                    unixtime = calendar.timegm(created_struct_time)
                    # the order of args to zadd is reversed in redis-py from that in redis
                    # https://github.com/andymccurdy/redis-py/issues/70
                    redis_server.zadd("tweet_dates:%s" % query, created_at, unixtime)

                    proc_tweet(tweet, query)
                else:
                    tweets_seen_before += 1
                    # Stop if all tweets on a page were processed in a previous request
                    if tweets_seen_before == rpp:
                        print "All tweets on page %d seen before, stop processing" % page
                        return

if len(sys.argv) > 1:
    # Clients may request up to 1,500 statuses via the page and rpp parameters for the search method
    # http://dev.twitter.com/pages/every_developer
    search_tweets(sys.argv[1], 15, 100)
else:
    print 'Usage: %s "query string"' % sys.argv[0]
