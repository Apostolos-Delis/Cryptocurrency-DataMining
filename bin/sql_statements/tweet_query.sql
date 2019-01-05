/* Query for joining all the seperate tables found in tweets with their corresponding ids" */
SELECT 
    tweets.id, 
    tweets.date, 
    tweets.content, 
    tweets.sentiment,
    tweets.retweets,
    cryptocurrencies.name AS coin, 
    twitter_users.followers AS user_followers,
    twitter_users.friends AS user_friends
FROM tweets 
    JOIN cryptocurrencies ON cryptocurrencies.id = tweets.coin_id
    JOIN twitter_users ON twitter_users.id = tweets.user_id 
ORDER BY twitter_users.followers DESC 
