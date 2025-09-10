import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from app.services.twitter_service import TwitterService
from app.config import Config


class TestTwitterService:
    """Test cases for TwitterService restrict_following functionality."""
    
    @pytest.fixture
    def mock_twitter_service(self):
        """Create a TwitterService instance with mocked tweepy client."""
        with patch('app.services.twitter_service.tweepy.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            service = TwitterService()
            service.client = mock_client
            return service, mock_client
    
    @pytest.fixture 
    def sample_tweets(self):
        """Sample tweet data for testing."""
        return [
            {
                'id': '123456',
                'text': 'Test tweet about #AI from user1',
                'created_at': '2024-01-01T10:00:00',
                'author_id': '1001',
                'author': {'username': 'user1', 'name': 'User One', 'verified': False},
                'public_metrics': {'like_count': 5, 'retweet_count': 2},
                'url': 'https://twitter.com/i/status/123456'
            },
            {
                'id': '789012',
                'text': 'Another #AI tweet from user2',
                'created_at': '2024-01-01T11:00:00',
                'author_id': '1002',
                'author': {'username': 'user2', 'name': 'User Two', 'verified': True},
                'public_metrics': {'like_count': 10, 'retweet_count': 5},
                'url': 'https://twitter.com/i/status/789012'
            }
        ]
    
    @pytest.mark.asyncio
    async def test_search_tweets_without_restriction(self, mock_twitter_service, sample_tweets):
        """Test normal search without following restriction."""
        service, mock_client = mock_twitter_service
        
        # Mock the _search_tweets_with_query method
        with patch.object(service, '_search_tweets_with_query', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = sample_tweets
            
            result = await service.search_tweets("AI", restrict_following=False)
            
            # Should call _search_tweets_with_query with just the keyword
            mock_search.assert_called_once_with("AI", 50)
            assert len(result) == 2
            assert result == sample_tweets
    
    @pytest.mark.asyncio
    async def test_search_tweets_with_api_filter_success(self, mock_twitter_service, sample_tweets):
        """Test search with restrict_following when API filter works."""
        service, mock_client = mock_twitter_service
        
        # Mock successful API filter search
        with patch.object(service, '_search_tweets_with_query', new_callable=AsyncMock) as mock_search:
            # First call (test mode) returns results, second call returns full results
            mock_search.side_effect = [sample_tweets[:1], sample_tweets]  # Test mode returns 1, full returns all
            
            result = await service.search_tweets("AI", restrict_following=True)
            
            # Should make two calls: one test, one real
            assert mock_search.call_count == 2
            mock_search.assert_any_call("AI from:following", 50, test_mode=True)
            mock_search.assert_any_call("AI from:following", 50)
            assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_search_tweets_with_api_filter_fallback(self, mock_twitter_service, sample_tweets):
        """Test search with restrict_following when API filter fails, uses fallback."""
        service, mock_client = mock_twitter_service
        
        with patch.object(service, '_search_tweets_with_query', new_callable=AsyncMock) as mock_search, \
             patch.object(service, '_filter_tweets_by_following', new_callable=AsyncMock) as mock_filter:
            
            # API filter test returns no results, regular search returns tweets
            mock_search.side_effect = [[], sample_tweets]  # Test mode fails, regular search succeeds
            mock_filter.return_value = sample_tweets[:1]  # Filter returns subset
            
            result = await service.search_tweets("AI", restrict_following=True)
            
            # Should try API filter first, then fallback to local filtering
            assert mock_search.call_count == 2
            mock_search.assert_any_call("AI from:following", 50, test_mode=True)
            mock_search.assert_any_call("AI", 50)
            mock_filter.assert_called_once_with(sample_tweets)
            assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_filter_tweets_by_following(self, mock_twitter_service, sample_tweets):
        """Test local filtering of tweets by followed accounts."""
        service, mock_client = mock_twitter_service
        
        # Mock followed user IDs - only user 1001 is followed
        with patch.object(service, '_get_following_user_ids', new_callable=AsyncMock) as mock_following:
            mock_following.return_value = {'1001'}  # Only user1 is followed
            
            result = await service._filter_tweets_by_following(sample_tweets)
            
            # Should return only tweets from followed users
            assert len(result) == 1
            assert result[0]['author_id'] == '1001'
            assert result[0]['author']['username'] == 'user1'
    
    @pytest.mark.asyncio
    async def test_get_following_user_ids_caching(self, mock_twitter_service):
        """Test that following user IDs are cached properly."""
        service, mock_client = mock_twitter_service
        
        # Mock the API calls
        mock_user = Mock()
        mock_user.data.id = 'authenticated_user_id'
        mock_client.get_me.return_value = mock_user
        
        # Mock following users
        mock_following_users = [Mock(id='1001'), Mock(id='1002'), Mock(id='1003')]
        with patch('app.services.twitter_service.tweepy.Paginator') as mock_paginator_class:
            mock_paginator = Mock()
            mock_paginator.flatten.return_value = mock_following_users
            mock_paginator_class.return_value = mock_paginator
            
            # First call should hit the API
            result1 = await service._get_following_user_ids()
            assert result1 == {'1001', '1002', '1003'}
            assert mock_client.get_me.call_count == 1
            
            # Second call should use cache
            result2 = await service._get_following_user_ids()
            assert result2 == {'1001', '1002', '1003'}
            assert mock_client.get_me.call_count == 1  # Still only 1 call
            
            # Clear cache and call again
            service.clear_following_cache()
            result3 = await service._get_following_user_ids()
            assert result3 == {'1001', '1002', '1003'}
            assert mock_client.get_me.call_count == 2  # Now 2 calls
    
    @pytest.mark.asyncio
    async def test_search_tweets_api_filter_exception(self, mock_twitter_service, sample_tweets):
        """Test handling of API exceptions when trying from:following filter."""
        service, mock_client = mock_twitter_service
        
        with patch.object(service, '_search_tweets_with_query', new_callable=AsyncMock) as mock_search, \
             patch.object(service, '_filter_tweets_by_following', new_callable=AsyncMock) as mock_filter:
            
            # First call (test mode) raises exception, second call succeeds
            mock_search.side_effect = [Exception("API Error"), sample_tweets]
            mock_filter.return_value = sample_tweets[:1]
            
            result = await service.search_tweets("AI", restrict_following=True)
            
            # Should catch exception and fallback to local filtering
            assert mock_search.call_count == 2
            mock_filter.assert_called_once_with(sample_tweets)
            assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_filter_tweets_no_following_list(self, mock_twitter_service, sample_tweets):
        """Test behavior when no following list is available."""
        service, mock_client = mock_twitter_service
        
        with patch.object(service, '_get_following_user_ids', new_callable=AsyncMock) as mock_following:
            mock_following.return_value = set()  # Empty following list
            
            result = await service._filter_tweets_by_following(sample_tweets)
            
            # Should return original tweets if no following list available
            assert len(result) == 2
            assert result == sample_tweets
    
    def test_clear_following_cache(self, mock_twitter_service):
        """Test cache clearing functionality."""
        service, mock_client = mock_twitter_service
        
        # Set some cache data
        service._following_cache = {'user1', 'user2'}
        service._following_user_ids = {'1001', '1002'}
        
        # Clear cache
        service.clear_following_cache()
        
        # Verify cache is cleared
        assert service._following_cache is None
        assert service._following_user_ids is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])