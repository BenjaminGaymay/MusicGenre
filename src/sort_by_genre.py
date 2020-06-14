#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import load, dump
from os.path import dirname

print('Sorting by genre...', end='')

with open(f'{dirname(__file__)}/../json/tracks.json', 'r', encoding='utf-8') as fd:
	tracks = load(fd)

genres = {}
for track in tracks:
	if 'error' in track:
		continue

	for track_genre in track['genre']:
		if track_genre not in genres:
			genres[track_genre] = []

		genres[track_genre].append({
		    'id': track['id'],
		    'spotify': track['spotify'],
		    'ratio': track['ratio'],
		    'track': track['track'],
		    'audio_features': track['audio_features'],
		    'popularity': track['popularity']
		})

genres_array = [{
    'length': len(genre_tracks),
    'genre': genre,
    'tracks': genre_tracks,
} for genre, genre_tracks in genres.items()]

genres_array.sort(key=lambda x: x['length'], reverse=True)

with open(f'{dirname(__file__)}/../json/genres.json', 'w', encoding='utf-8') as fd:
	dump(genres_array, fd, ensure_ascii=False, indent=4)

print(' Done.')