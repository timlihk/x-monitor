import tweepy
from typing import List, Dict, Any, Optional
from app.config import Config

class TwitterService:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=Config.X_BEARER_TOKEN,
            consumer_key=Config.X_API_KEY,
            consumer_secret=Config.X_API_SECRET,
            access_token=Config.X_ACCESS_TOKEN,
            access_token_secret=Config.X_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
    
    async def search_tweets(self, keyword: str, restrict_following: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
        try:
            query = keyword
            if restrict_following:
                query += " from:following"
            
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'name', 'verified'],
                expansions=['author_id']
            ).flatten(limit=max_results)
            
            tweet_data = []
            users_dict = {}
            
            for tweet in tweets:
                if hasattr(tweet, 'includes') and 'users' in tweet.includes:
                    for user in tweet.includes['users']:
                        users_dict[user.id] = user
                
                author = users_dict.get(tweet.author_id)
                
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author': {
                        'username': author.username if author else None,
                        'name': author.name if author else None,
                        'verified': author.verified if author else None
                    } if author else None,
                    'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                    'url': f"https://twitter.com/i/status/{tweet.id}"
                }
                tweet_data.append(tweet_info)
            
            return tweet_data
            
        except Exception as e:
            print(f"Error searching tweets: {str(e)}")
            return []
    
    def get_user_following(self, user_id: Optional[str] = None) -> List[str]:
        try:
            if not user_id:
                me = self.client.get_me()
                user_id = me.data.id
            
            following = tweepy.Paginator(
                self.client.get_following,
                id=user_id,
                max_results=1000
            ).flatten(limit=5000)
            
            return [user.username for user in following]
            
        except Exception as e:
            print(f"Error getting following list: {str(e)}")
            return []