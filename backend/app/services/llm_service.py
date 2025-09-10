import openai
import anthropic
from typing import List, Dict, Any
from app.config import Config

class LLMService:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.use_openai = True
        elif Config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            self.use_openai = False
        else:
            raise ValueError("Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be provided")
    
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
            if self.use_openai:
                response = await self._openai_summarize(prompt)
            else:
                response = await self._anthropic_summarize(prompt)
            return response
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    async def _openai_summarize(self, prompt: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes social media content and provides structured summaries using bullet points. Always format your responses with clear section headers and bullet points (•) for easy reading."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    async def _anthropic_summarize(self, prompt: str) -> str:
        message = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text.strip()