#!/usr/bin/env python
import twitter
import csv
api = twitter.Api(username='', password='')
csvWriter = csv.writer(open('linux_twitter_sorted.csv', 'w'), delimiter=';', quotechar='"')

twitter_profiles = {
    'General': [
        'linuxfoundation',
        'LinuxDotCom',
        'DistroWatch',
        'linuxtracker'
        ],
    'Linux Distros': [
        'debianproject',
        'fedora_linux',
        'mandriva',
        'opensuse',
        'planetalinux',
        'Linux_Mint',
        'moblin_netbook',
        'geteasypeasy',
        'CRUNCHBANG',
        'jolicloud',
        'eyeOS',
        'archlinux',
        'ipodlinux'
        ],
    'Linux Communities': [
        'LinuxCommunity',
        'clububuntu',
        'kdecommunity',
        'planetalinux',
        'LinuxDevNetwork'
        ],
    'Linux Geeks': [
        'jonobacon',
        'galaxiecruzin',
        'linuxing',
        'linuxrebel',
        'popey',
        'schestowitz',
        'linuxartist',
        'tuxplanet',
        'ubuntugeek',
        'linus_torvalds'
        ],
    'Linux Media': [
        'linuxjournal',
        'tuxradar',
        'linuxmagazine',
        'linux_pro',
        'ubuntupodcast',
        'linuxoutlaws',
        'goinglinux',
        'uupc'
        ],
    'Linux Howto': [
        'commandlinefu',
        'howtolinux',
        'LinuxHowto',
        'bashcookbook'
        ],
    'Linux Hardware': [
        'linuxdevices',
        'desktoplinux',
        'linuxnetbook'
        ]
}

count = 0
for cat, profiles in sorted(twitter_profiles.items()):
    for profile in profiles:
    
        count += 1
        print count

        try:
            user = api.GetUser(profile)
            name = user.name or ''
            desc = user.description or ''
            loc =  user.location or ''
            url = user.url or ''

            csvWriter.writerow([
                cat,
                name,
                user.profile_image_url,
                user.screen_name,
                desc,
                loc,
                url
                ])
        except:
            print profile

#Other
#gnome
#GetLinuxJobs