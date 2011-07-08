# -*- coding: utf-8 -*-
# TODO set text and text_normalized properties and use them
# set type and token counts on update not on write
# consider not updating stats if text is false
import os
import re
import operator
import twitter_text

class TweetStats(dict):

    # Object properties

    stats = {}
    stats_summary = []
    text = ''
    tweet_count = 0
    tweet_fields = ['iso_language_code', 'source', 'from_user', 'to_user_id', 'geo', 'created_at', 'metadata']
    formats = ['html', 'json', 'txt']
    re_non_word = re.compile("\W+")
    re_uri = re.compile("https?://\S+")

    # Override dict functions

    def __init__(self):
        # init fields
        for f in self.tweet_fields:
            self.stats[f] = {}


    def __len__(self):
        return self.tweet_count


    def update(self, tweet):
        self.tweet_count += 1
        self.set_text(tweet)
        self.update_field_stats(tweet)
        self.update_word_stats(tweet)
        self.update_entities_stats(tweet)


    # Custom functions

    def write_file(self, directory, name, content):
        """Write content to file.

        An existing file with the same name will be erased.
        """

        try:
            f = open(os.path.join(directory, name), 'w')
            f.write(content)
            f.close()
        except:
            print "Content not written to file: %s" % name


    def write_stats(self, directory):
        """Write statistics for each index to files in several formats."""

        target_dir = os.path.join(directory, 'tweet_stats')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # general stats
        self.stats_summary.append("%-30s\t%12d\n" % ('Number of tweets', len(self)))
        self.stats_summary.append('%-30s\t%-12s\t%-12s' % ('Index', 'Type count', 'Token count'))

        for k in self.stats:
            k_stats = self.stats[k]

            rank = 0
            token_count = 0
            lines = []

            # Sort by frequency of words, pairs, triples, urls etc.
            k_stats_sorted = sorted(k_stats.iteritems(), key=operator.itemgetter(1), reverse=True)

            for val, card in k_stats_sorted:
                rank += 1
                token_count += card
                lines.append("%4d %-60s %5d" % (rank, val, card))

            self.write_file(target_dir, "%s.txt" % k, "\n".join(lines))

            # update summary with index name and corresponding type and token counts
            self.stats_summary.append('%-30s\t%12d\t%12d' % (k, len(k_stats), token_count))

        # write summary info
        self.write_file(target_dir, 'general.txt', "\n".join(self.stats_summary))


    def set_text(self, tweet):
        """Set text property to normalized text of tweet."""

        if not tweet.has_key('text'):
            return

        text = tweet['text']

        # remove URIs
        text = re.sub(self.re_uri,"", text)
        # lower case string and remove non word characters
        text = re.sub(self.re_non_word, " ",  text.lower()).strip()

        self.text = text


    def get_phrase_list(self, words, length):
        """Get a list of word lists from given list of words of the given length.

        Returns list of lists or None if length of given list is less than given length."""

        if len(words) >= length:
            return [words[i:i+length] for i in range(len(words) - length + 1)]
        else:
            return None


    def update_stats(self, idx, key):
        """Update statistics for given index and key."""

        stats = self.stats
        if not stats.has_key(idx):
            stats[idx] = {}
        if stats[idx].has_key(key):
            stats[idx][key] += 1
        else:
            stats[idx][key] = 1


    def get_index_from_list(self, l):
        """Generate and return a hashable index."""

        return " ".join(l)


    def update_field_stats(self, tweet):
        """Update statistics for tweet_fields."""

        stats = self.stats
        for f in self.tweet_fields:
            if tweet.has_key(f):
                f_val = tweet[f]
                if f_val is None:
                    continue
                if stats[f].has_key(f_val):
                    stats[f][f_val] += 1
                else:
                    stats[f][f_val] = 1


    def update_word_stats(self, tweet):
        """Update statistics for words, word pairs and triples."""

        if not self.text:
            return

        words = self.text.split()

        # process single words
        for word in words:
            self.update_stats('words', word)

        # process 2 word lists
        pairs = self.get_phrase_list(words, 2)
        if pairs is not None:
            for word_pair in pairs:
                self.update_stats('word_pairs', self.get_index_from_list(word_pair))

        # process 3 word lists
        triples = self.get_phrase_list(words, 3)
        if triples is not None:
            for word_triple in triples:
                self.update_stats('word_triples', self.get_index_from_list(word_triple))


    def get_entities(self, text):
        """Extract entities from tweet as text and return an entity dict.

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


    def update_entities_stats(self, tweet):
        """Process tweet entities and add them to tweet_stats dict."""

        if not tweet.has_key('text'):
            return

        entities = self.get_entities(tweet['text'])
        for ent in entities:
            if entities[ent]:
                e_list = entities[ent]
                for k in e_list:
                    v = None
                    if k.has_key('url'):
                        v = k['url']
                    # FIXME Further normalize text?
                    if k.has_key('text'):
                        v = k['text'].lower()
                    if v:
                        tweet_stats = self.stats
                        if not tweet_stats.has_key(ent):
                            tweet_stats[ent] = {}
                        if not tweet_stats[ent].has_key(v):
                            tweet_stats[ent][v] = 1
                        else:
                            tweet_stats[ent][v] += 1

if __name__ == "__main__":

    tweet = {u'iso_language_code': u'en', u'to_user_id_str': None, u'text': u'PCMS 4n1 Combo - MSI Wind U100-641US 10-Inch #Netbook Carrying Bag with AC and DC Adapter Charger Home / Car / A... http://amzn.to/f2wssq', u'from_user_id_str': u'104656176', u'profile_image_url': u'http://a2.twimg.com/profile_images/771807838/sleeper-chairs-03-300x146_normal.jpg', u'id': 56183119782477824L, u'source': u'&lt;a href=&quot;http://twitterfeed.com&quot; rel=&quot;nofollow&quot;&gt;twitterfeed&lt;/a&gt;', u'id_str': u'56183119782477824', u'from_user': u'sleeperchairs', u'from_user_id': 104656176, u'to_user_id': None, u'geo': None, u'created_at': u'Fri, 08 Apr 2011 02:34:34 +0000', u'metadata': {u'result_type': u'recent'}}
    ts = TweetStats()
    
    for i in range(10):
        ts.update(tweet)

    print ts
