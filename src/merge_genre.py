#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
from os.path import dirname
from json import load, dump

print('Merging genre...', end='')

with open(f'{dirname(__file__)}/../json/genres.json', 'r', encoding='utf-8') as fd:
	genres = load(fd)

with open(f'{dirname(__file__)}/../json/tracks.json', 'r', encoding='utf-8') as fd:
	tracks = load(fd)

popularity = list(map(lambda x: x['genre'], genres))
popularity.append('')

genres_by_popularity = list(map(lambda x: {'genre': x, 'tracks': []}, popularity))

for track in tracks:
	if 'error' in track:
		continue

	if track['genre']:
		track['genre'].sort(key=lambda x: popularity.index(x))

		index = popularity.index(track['genre'][0])
	else:
		index = len(popularity) - 1

	genres_by_popularity[index]['tracks'].append(track)

filtered = list(filter(lambda x: x['tracks'], genres_by_popularity))
filtered_genres = list(map(lambda x: x['genre'], filtered))

for genre in filtered:

	for track in genre['tracks'][:10]:
		new_genres = list(filter(lambda x: x in filtered_genres, track['genre']))
		track['genre'] = new_genres

with open(f'{dirname(__file__)}/../json/filtered_genres.json', 'w', encoding='utf-8') as fd:
	dump(filtered, fd, ensure_ascii=False, indent=4)

print(' Done.')