SELECT 
    tweets.date, 
    tweets.content, 
    tweets.sentiment,
    hashtags.name
FROM tweet_hashtag
    JOIN tweets ON tweets.id = tweet_hashtag.tweet_id
    JOIN hashtags ON hashtags.id = tweet_hashtag.hashtag_id
LIMIT 0, 100000
