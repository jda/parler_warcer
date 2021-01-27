#!/usr/bin/env python3

import datetime
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from dateparser import DateDataParser
ddp = DateDataParser(languages=['en'])

def find_relative_time_as_of_time(req_time, rel_time):
    req = datetime.datetime.strptime(req_time,"%Y-%m-%dT%H:%M:%SZ")
    fake_rel_time = ddp.get_date_data(rel_time).date_obj
    delta = datetime.datetime.now() - fake_rel_time
    sorta_post_time = req - delta
    return sorta_post_time.isoformat()

def read_parler_warc(warc_file):
    with open(warc_file, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response':
                src_url = record.rec_headers.get_header('WARC-Target-URI')
                # https://parler.com/post/36627e701bfc4158a2e6dc682689f711
                if "parler.com/post" not in src_url:
                    continue

                parler_id = src_url.split('/')[-1]

                if len(parler_id) != 32:
                    continue
                
                req_time = record.rec_headers.get_header('WARC-Date')
                soup = BeautifulSoup(record.content_stream().read(), 'html.parser')
                
                try:
                  author = soup.find('span', {'class': 'author--name'}).text
                except AttributeError:
                  author = ""
    
                try:
                  username = soup.find('span', {'class': 'author--username'}).text
                except AttributeError:
                  username = ""

                try: 
                  profile_pic = soup.find('img', {'alt': 'Post Author Profile Pic'}).get('src', '')
                except AttributeError:
                  profile_pic = ""
    
                try:
                  post_text = soup.find('div', {'class': 'card--body'}).find('p').text
                except AttributeError:
                  post_text = ""

                try:
                  post_image = soup.find('img', {'class': "mc-image--modal--element"}).get('src', '')
                except AttributeError:
                  post_image = ""

                try:
                  post_rel_timestamp = soup.find('span', {'class': 'post--timestamp'}).text
                except AttributeError:
                  post_rel_timestamp = ""

                try:
                  post_impressions = soup.find('span', {'class': 'impressions--count'}).text
                except AttributeError:
                  post_impressions = ""
                
                post_timestamp = ""
                if post_rel_timestamp:
                    post_timestamp = find_relative_time_as_of_time(req_time, post_rel_timestamp)

                yield (
                    parler_id, author, username, profile_pic, post_text, post_image, 
                    post_rel_timestamp, post_timestamp, post_impressions, src_url, req_time
                )
