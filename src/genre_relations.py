#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from os.path import dirname
from json import load, dump
from requests import request
import oauthlib.oauth1.rfc5849.signature as oauth
from urllib.parse import quote

with open(f'{dirname(__file__)}/../json/filtered_genres.json', 'r', encoding='utf-8') as fd:
	json_file = load(fd)

genres = []
for genre in json_file:
	genres.append(genre['genre'])

request_url = 'http://api.music-story.com/oauth/request_token'
search_url = 'http://api.music-story.com/fr/genre/search'
relation_url = 'http://api.music-story.com/fr/genre/1/'

# headers = {
#     "Authorization": ('oauth_consumer_key="", '
#                       'oauth_signature_method="HMAC-SHA1", ')
# }

# headers = {
#     "Authorization": ('oauth_consumer_key="89da603cd6ee602aaf300c86ad25f73e80d143c2", '
#                       'oauth_signature_method="HMAC-SHA1"')
# }

# client_secret = '08bfc2dace06f85da43a82c5e0dbb9b177cb43fb'

# query = ''  # f'name={quote(genres[3])}'

# params = oauth.collect_parameters(uri_query=query,
#                                   body=[],
#                                   headers=headers,
#                                   exclude_oauth_signature=True,
#                                   with_realm=False)

# norm_params = oauth.normalize_parameters(params)
# print(norm_params)
# base_string = oauth.signature_base_string('GET', request_url, norm_params)

# sig = oauth.sign_hmac_sha1(base_string, '08bfc2dace06f85da43a82c5e0dbb9b177cb43fb', '')

# print(sig, quote(sig))
# 'name': genres[3],
json = request("GET", request_url, headers=headers, params={'oauth_signature': quote(sig)})

pprint(json.text)