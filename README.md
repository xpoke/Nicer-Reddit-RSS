# Nicer-Reddit-RSS
Simple server to fetch, parse and return reddit RSS feeds, making a user friendly experience

## What is this
This python 3 script sets up a server that listens for rss requests and passes them along to reddit, and modifies the content before returning the feed.

## Who is this for
If you are using a cloud based RSS reader like Feedly or Inoreader to get your Reddit homepage, or if you just want a nicer reddit feed. This is also a good start for people who want to make their own modifications.

## Features:
* Proxy for reddit feeds
* Images and gifs are shown inline in the feed
* Self posts have a reddit icon (for thumbnails)
* Content links are visible and domain is highlighted
* Moved the links around for consistency and clickability

## Prerequisites

    Python3
       ├─ urllib
       ├─ tldextract
       ├─ flask
       └─ lxml

You'll want to set up an AWS server, raspberry pi, etc - as long as it has a static ip

Install the python3 packages with pip

## Usage
Run the server:

    python3 main.py

By default it will listen on port 8080. Modify the source's start to change this or other defaults.

Use a url that looks like this:

    http://ip:8080/
    http://ip:8080/?limit=10
    http://ip:8080/?feed=cad769dfgbjhlk64kljhv7q&user=gallowboob&limit=20

This script currently only supports the "feed", "user" and "limit" parameters.

You can get the parameters for the request from your own reddit profile: www.reddit.com/prefs/feeds

## Preview
https://raw.githubusercontent.com/xPoke/Nicer-Reddit-RSS/master/preview.png

## Credits
Original skeleton based on github.com/therippa/kaRdaSShian
Idea for inline photos is from www.inline-reddit.com
