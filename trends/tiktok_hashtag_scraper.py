import csv
import json
from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get(
    "y51e-qrNU4ErmtYoc1cJGZBpXDLRTwJM0zwtx8NLhTadugAsrE85e6GeT3PTsY9BBiZ2R2t3oBAcP6AOuybQxTxRGXRuU6Xx4QcwUwtbGOPxAfE02G2kMD29W8qX9MukBLojq18LZYixDTCS", None
)

async def get_hashtag_videos():
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3, headless=False, override_browser_args=["--incognito"])
        tag = api.hashtag(name="fyp")
        
        with open("hashtags.csv", mode="w", newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(['hashtagName'])  # Write the header
            
            async for video in tag.videos(count=30):
                video_dict = video.as_dict  # Assumes as_dict is a property; use as_dict() if it's a method
                contents = video_dict.get('contents', [])
                
                for content in contents:
                    text_extra = content.get('textExtra', [])
                    
                    for item in text_extra:
                        hashtag_name = item.get('hashtagName', '')
                        if hashtag_name:
                            writer.writerow([hashtag_name])  # Write each hashtagName to the CSV

if __name__ == "__main__":
    asyncio.run(get_hashtag_videos())
