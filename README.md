# Twitter Archiver

Archive your favorite twitter account with all its media contents.

### Supports

- [x] Photo
- [x] Video
- [ ] Animated GIF


### Changes

This project was using Twint but has now shifted to Twitter's front-end API and GraphQL API

### Usage

1. install ```youtube-dl``` with ```pip install youtube-dl```
2. install ```requests``` with ```pip install requests```
3. find your GraphQL endpoint and Bearer token from Twitter (details below)
4. edit ```main.py``` and put your GraphQL endpoint and Bearer token accordingly
5. optional: if you want to store archived tweets(json, image and video) to directory other than ```data``` you need to change it in ```main.py``` and ```base.py```


### Find your GraphQL endpoint and Bearer token

1. open any twitter user's profile (e.g. https://twitter.com/realDonaldTrump)
2. right-click anywhere in your browser and select inspect (for Chrome. other browser may have different naming)
3. go to ```Network``` tab. select ```XHR``` as the filter
4. find a ```GET``` call to ```UserByScreenName``` endpoint. you may need to refresh the page for network inspector to record
5. the request url will have the format like this ```graphql/YOUR_GRAPHQL_ENDPOINT/UserByScreenName?``` copy the graphql endpoint
6. the request headers will have an ```authorization``` header with format like this ```Bearer YOUR_BEARER_TOKEN``` copy the bearer token


### TODO
- [x] add config file for more flexible configuration
- [ ] add a json file for metadata storage
- [ ] add backend for archive
- [ ] add fronend for archived tweets management 