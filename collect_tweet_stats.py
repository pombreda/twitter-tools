# -*- coding: utf-8 -*-
import sys
import re
import time
import calendar
import twitter
import twitter_text
import redis

# TODO store tweets in mongodb?

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


def get_entities(text):
    """Extract entities from tweet text
    
    Extract urls, @mentions, hashtags from tweet text.
    Function modified from:
    https://github.com/ptwobrussell/Mining-the-Social-Web/blob/master/python_code/the_tweet__extract_tweet_entities.py
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


def store_entities(text, query)
    """Store tweet entities in DB

    Store urls, @mentions, hashtags and store them with counts in DB.
    """

    global redis_server
    entities = get_entities(text)

    #TODO store entities in sorted sets
    #for e in entities:
        #redis_server.zincrby("user_mentions:%s" % query, user_mention, 1)
        #redis_server.zincrby("urls:%s" % query, url, 1)
        #redis_server.zincrby("hashtags:%s" % query, hashtag, 1)


def store_words(text, query):
    """Store words and phrases in DB

    Store single words, two and three words phrases with counts in DB.
    """

    global redis_server

    # remove URIs
    text = re.sub(re_uri,"", text)
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


def proc_tweet(tweet, query):
    """Process a single tweet.
    
    Determines single words, word pairs, and word triples and stores them with
    counts in corresponding ordered sets in redis."""

    global redis_server, re_non_word

    text = tweet['text']

    # store tweet entities
    store_entities(text)

    # store from_user
    #redis_server.zincrby("from_user_ids:%s" % query, from_user_id, 1)

    # store to_user
    #if to_user_ids is not None:
        #redis_server.zincrby("to_user_ids:%s" % query, to_user_id, 1)


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
