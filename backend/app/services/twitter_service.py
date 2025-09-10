import tweepy
from typing import List, Dict, Any, Optional, Set
from app.config import Config
import logging

logger = logging.getLogger(__name__)

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
        self._following_cache: Optional[Set[str]] = None
        self._following_user_ids: Optional[Set[str]] = None
    
    async def search_tweets(self, keyword: str, restrict_following: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for tweets with optional restriction to followed accounts.
        
        Args:
            keyword: Search query (hashtags, keywords, tickers)
            restrict_following: If True, only return tweets from accounts the user follows
            max_results: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries with author and engagement data
        """
        try:
            # Build the search query
            query = keyword
            use_api_filter = False
            
            if restrict_following:
                # Try using X API's from:following filter first
                try:
                    query_with_filter = f"{keyword} from:following"
                    logger.info(f"Attempting search with from:following filter: {query_with_filter}")
                    
                    # Test the query with from:following filter
                    tweets = await self._search_tweets_with_query(
                        query_with_filter, 
                        max_results,
                        test_mode=True  # First try with limited results to test
                    )
                    
                    if tweets:  # If we got results, use the API filter
                        use_api_filter = True
                        query = query_with_filter
                        logger.info("Successfully using from:following API filter")
                    else:
                        logger.info("from:following filter returned no results, trying fallback")
                        
                except Exception as api_error:
                    logger.warning(f"from:following API filter failed: {str(api_error)}, using fallback")
            
            # Execute the search with the determined query
            tweets = await self._search_tweets_with_query(query, max_results)
            
            # If restrict_following is True and we couldn't use API filter, 
            # apply local filtering
            if restrict_following and not use_api_filter and tweets:
                logger.info("Applying local filtering for followed accounts")
                tweets = await self._filter_tweets_by_following(tweets)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error in search_tweets: {str(e)}")
            return []
    
    async def _search_tweets_with_query(self, query: str, max_results: int, test_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Execute tweet search with the given query.
        
        Args:
            query: The search query string
            max_results: Maximum number of results
            test_mode: If True, limit to 10 results for testing
            
        Returns:
            List of formatted tweet dictionaries
        """
        try:
            limit = min(10, max_results) if test_mode else max_results
            
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'context_annotations'],
                user_fields=['username', 'name', 'verified'],
                expansions=['author_id']
            ).flatten(limit=limit)
            
            tweet_data = []
            users_dict = {}
            
            # Process the response to extract user info
            for tweet in tweets:
                if hasattr(tweet, 'includes') and 'users' in tweet.includes:
                    for user in tweet.includes['users']:
                        users_dict[user.id] = user
                
                author = users_dict.get(tweet.author_id)
                
                tweet_info = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                    'author_id': tweet.author_id,
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
            logger.error(f"Error in _search_tweets_with_query: {str(e)}")
            return []
    
    async def _filter_tweets_by_following(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter tweets to only include those from accounts the user follows.
        This is a fallback when the API from:following filter doesn't work.
        
        Args:
            tweets: List of tweet dictionaries
            
        Returns:
            Filtered list of tweets from followed accounts only
        """
        try:
            # Get the list of followed user IDs
            followed_user_ids = await self._get_following_user_ids()
            
            if not followed_user_ids:
                logger.warning("No following list available for filtering")
                return tweets
            
            # Filter tweets by author_id
            filtered_tweets = [
                tweet for tweet in tweets 
                if tweet.get('author_id') and str(tweet['author_id']) in followed_user_ids
            ]
            
            logger.info(f"Filtered {len(tweets)} tweets to {len(filtered_tweets)} from followed accounts")
            return filtered_tweets
            
        except Exception as e:
            logger.error(f"Error filtering tweets by following: {str(e)}")
            return tweets  # Return original tweets if filtering fails
    
    async def _get_following_user_ids(self) -> Set[str]:
        """
        Get the set of user IDs that the authenticated user follows.
        Uses caching to avoid repeated API calls.
        
        Returns:
            Set of user ID strings
        """
        if self._following_user_ids is not None:
            return self._following_user_ids
        
        try:
            # Get current user
            me = self.client.get_me()
            if not me.data:
                logger.error("Could not get authenticated user info")
                return set()
            
            user_id = me.data.id
            
            # Get following list with user IDs
            following = tweepy.Paginator(
                self.client.get_following,
                id=user_id,
                max_results=1000,
                user_fields=['id']
            ).flatten(limit=5000)
            
            # Cache the user IDs
            self._following_user_ids = {str(user.id) for user in following}
            logger.info(f"Cached {len(self._following_user_ids)} followed user IDs")
            
            return self._following_user_ids
            
        except Exception as e:
            logger.error(f"Error getting following user IDs: {str(e)}")
            return set()
    
    def clear_following_cache(self):
        """Clear the cached following list to force refresh on next request."""
        self._following_cache = None
        self._following_user_ids = None
        logger.info("Following cache cleared")
    
    def get_user_following(self, user_id: Optional[str] = None) -> List[str]:
        """
        Get list of usernames that the authenticated user follows.
        This method is kept for backward compatibility.
        
        Args:
            user_id: Optional user ID (defaults to authenticated user)
            
        Returns:
            List of usernames (not user IDs)
        """
        try:
            if not user_id:
                me = self.client.get_me()
                user_id = me.data.id
            
            following = tweepy.Paginator(
                self.client.get_following,
                id=user_id,
                max_results=1000,
                user_fields=['username']
            ).flatten(limit=5000)
            
            usernames = [user.username for user in following if user.username]
            logger.info(f"Retrieved {len(usernames)} following usernames")
            return usernames
            
        except Exception as e:
            logger.error(f"Error getting following list: {str(e)}")
            return []