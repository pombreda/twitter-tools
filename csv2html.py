#!/usr/bin/env python
import csv
twitter_profiles = {}
csvReader = csv.reader(open('linux_twitter_sorted.csv'), delimiter=';', quotechar='"')
for row in csvReader:
    #twitter_profiles[row[0]] = [row[1], row[2], row[3], row[4], row[5], row[6]]
    vals = row[1], row[2], row[3], row[4], row[5], row[6]
    if twitter_profiles.has_key(row[0]):
        val = twitter_profiles[row[0]]
        val.append(vals)
    else:
        twitter_profiles[row[0]] = [vals]

for cat, profiles in sorted(twitter_profiles.items()):
    print '<h3>' + cat + '</h3>'
    
    for profile in profiles:
        name = profile[0] or ''
        src = profile[1] or ''
        user = profile[2] or ''
        desc = profile[3] or ''
        url = profile[5] or ''
        
        a_start = '<a href="http://twitter.com/' + user + '">'

        print '<div class="twitter-profile">'
        print '<h4>' + a_start + name + '</a></h4>'
        print '<div class="twitter-profile-image">' + a_start + '<img src="' + src + '" alt="' + name + '" title="Follow on Twitter" /></a></div>'
        if desc:
            print '<p class="twitter-profile-desc">' + desc.strip() + '</p>'
        if url:
            print '<div>Website: <a href="' + url + '">' + url + '</a></div>'
        print '<div class="clear"></div></div>'