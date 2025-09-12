import httpx
from typing import List, Dict, Any
from app.config import Config

class LLMService:
    def __init__(self):
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY must be provided")
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com"
    
    async def summarize_tweets(self, tweets: List[Dict[str, Any]], keyword: str) -> str:
        if not tweets:
            return "No tweets found for analysis."
        
        tweet_texts = []
        for tweet in tweets:
            author_info = ""
            if tweet.get('author'):
                username = tweet['author'].get('username', 'Unknown')
                verified = " ✓" if tweet['author'].get('verified') else ""
                author_info = f"@{username}{verified}: "
            
            tweet_texts.append(f"{author_info}{tweet['text']}")
        
        tweets_text = "\n\n".join(tweet_texts[:20])
        
        prompt = f"""Summarize the following tweets about "{keyword}" into:
1. Main themes / repeated ideas
2. Positive sentiment (if any)
3. Negative sentiment (if any)
4. Notable quotes or insights

Return a concise summary (5–10 bullet points).

Use bullet points (•) for each item within sections.

Tweets:
{tweets_text}

Format your response with clear section headers and bullet points."""

        try:
            response = await self._deepseek_summarize(prompt)
            return response
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    async def _deepseek_summarize(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": Config.DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that analyzes social media content and provides structured summaries using bullet points. Always format your responses with clear section headers and bullet points (•) for easy reading."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()