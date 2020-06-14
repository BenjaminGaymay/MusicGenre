#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import dump
from time import sleep
from html import unescape
from pprint import pprint
from os.path import dirname
from requests import request
from difflib import SequenceMatcher

#####################
#					#
#	GET MY TRACKS	#
#					#
#####################

response = request('GET', 'http://benjamin-gaymay.eu/musiques')

html = unescape(response.text)

lines = [line.strip() for line in html.split('\n')]

condition = '<button type="button" class="btn btn-outline-success music list-group-item list-group-item-action date" name="'
filtered = filter(lambda x: condition in x, lines)
mapped = map(lambda x: x.split('>')[1].split('<')[0].strip(), filtered)

unique = list(set([line for line in mapped]))

my_tracks = [{
    'title': track.split(' - ')[1].strip().lower(),
    'artist': track.split(' - ')[0].strip().lower().split('&')[0],
    'track': track
} for track in unique]

#########################
#						#
#	SEARCH ON SPOTIFY	#
#						#
#########################

headers = {
    'Authorization':
    'Bearer BQBZvi90Feh8vYaoVBGU0FLHWFZJeNP1m5zoF7I4bvhq-TvtHZQni6Q28qX8CupVqQKKIDlsLiHjrPzYmZoz7dTBfmcLBlp3XR8xKgtsGFSQQch2R3OpVfcq_1I7MCHSEHqPERWDBS81SEo7OYjZK0-2wmXH4w',
}


def make_request(url, headers, step, querystring=None):
	json = None
	for i in range(3):
		try:
			json = request('GET', url, headers=headers, params=querystring).json()
			return json
		except:
			sleep(1)
			continue

	print(f'error: request: {step}')
	exit(1)


def search_for_track(querystring, my_track, title):
	url = 'https://api.spotify.com/v1/search'

	json = make_request(url, headers, f'search: {title}', querystring)

	if 'error' in json:
		print(json['error']['message'])
		exit(1)

	spotify_tracks = []
	for spotify_track in json['tracks']['items']:
		sequence = SequenceMatcher(None, my_track['artist'].lower(),
		                           spotify_track['album']['artists'][0]['name'].lower())

		spotify_tracks.append({
		    'name': spotify_track['name'],
		    'albumID': spotify_track['album']['id'],
		    'artist': spotify_track['album']['artists'][0]['name'],
		    'artistID': spotify_track['album']['artists'][0]['id'],
		    'trackID': spotify_track['id'],
		    'popularity': spotify_track['popularity'],
		    'ratio': sequence.ratio()
		})

	spotify_tracks.sort(key=lambda track: (track['ratio'], track['popularity']))

	if spotify_tracks:
		founded_tracks = filter(lambda track: track['ratio'] == spotify_tracks[-1]['ratio'], spotify_tracks)

		with_title_ratio = []
		for found in founded_tracks:
			sequence = SequenceMatcher(None, title.lower(), found['name'].lower())

			with_title_ratio.append({
			    'title': found['name'],
			    'albumID': found['albumID'],
			    'artist': found['artist'],
			    'artistID': found['artistID'],
			    'trackID': found['trackID'],
			    'ratioArtist': found['ratio'],
			    'ratioTitle': sequence.ratio(),
			    'popularity': found['popularity']
			})

		with_title_ratio.sort(key=lambda track: track['ratioTitle'])
		return with_title_ratio[-1]

	return None


def search_for_genre(track, album, artist):
	url = f'https://api.spotify.com/v1/audio-features/{track}'
	json = make_request(url, headers, f'genre: audio-features: {track}')

	if 'error' in json:
		print(json['error']['message'])
		exit(1)

	audio_features = {
	    'danceability': json['danceability'],
	    'acousticness': json['acousticness'],
	    'energy': json['energy'],
	    'instrumentalness': json['instrumentalness'],
	    'liveness': json['liveness'],
	    'loudness': json['loudness'],
	    'speechiness': json['speechiness'],
	    'tempo': json['tempo'],
	    'valence': json['valence'],
	}

	url = f'https://api.spotify.com/v1/albums/{album}'
	json = make_request(url, headers, f'genre: albums: {album}')

	if 'error' in json:
		print(json['error']['message'])
		exit(1)

	if json['genres']:
		return json['genres'], audio_features

	url = f'https://api.spotify.com/v1/artists/{artist}'
	json = make_request(url, headers, f'genre: artist: {artist}')

	if 'error' in json:
		print(json['error']['message'])
		exit(1)

	return json['genres'], audio_features


fd = open(f'{dirname(__file__)}/../json/tracks.json', 'w', encoding='utf-8')
fd.write('[\n')

for i, my_track in enumerate(my_tracks):
	loader = ['-', '\\', '|', '/'][i % 4]

	print(f" [{loader}] {i}/{len(my_tracks)}", end='\r')

	without_parenthesis = my_track['title'].split('(')[0].strip()

	remix = ''
	attempts = 0
	if 'remix' in my_track['title']:
		tmp = my_track['title']
		inside = tmp[tmp.find('(') + 1:tmp.find(')')]
		while 'remix' not in inside and attempts < 5:
			attempts += 1
			tmp = tmp[tmp.find(')') + 1:]
			inside = tmp[tmp.find('(') + 1:tmp.find(')')]

		remix = f' {inside}'

	full_filtered = without_parenthesis.lower().split('feat.')[0].split('ft.')[0] + remix

	q8 = search_for_track({
	    'q': f"{full_filtered} {my_track['artist']}",
	    'type': 'track',
	    'limit': 50
	}, my_track, full_filtered)

	if q8:
		genre, audio_features = search_for_genre(q8['trackID'], q8['albumID'], q8['artistID'])
		dump(
		    {
		        'id': q8['trackID'],
		        'genre': genre,
		        'spotify': f"{q8['artist']} - {q8['title']}",
		        'ratio': f"{q8['ratioArtist']} - {q8['ratioTitle']}",
		        'track': my_track['track'],
		        'audio_features': audio_features,
		        'popularity': q8['popularity']
		    },
		    fd,
		    indent=4,
		    ensure_ascii=False)
	else:
		dump({'track': my_track['track'], 'error': 'not found'}, fd, indent=4, ensure_ascii=False)

	fd.write(',\n' if i + 1 != len(my_tracks) else '\n')
	fd.flush()

fd.write(']\n')
fd.close()

print('Getting tracks... Done.')