import time
import random
from requests.exceptions import RequestException

import browser_cookie3
import http.cookiejar

import os
import yt_dlp  # Library for downloading YouTube video information
from youtube_transcript_api import YouTubeTranscriptApi  # For accessing YouTube transcripts
from youtube_transcript_api.formatters import WebVTTFormatter  # For formatting transcripts

proxies = [
    'http://proxy1.example.com:8080',
    'http://proxy2.example.com:8080',
    'http://proxy3.example.com:8080'
]

def get_youtube_video_details(video_id, headers, proxy=None, cookies=None):
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'youtube_include_dash_manifest': False,
        'headers': headers,
    }
    
    if proxy:
        ydl_opts['proxy'] = proxy
    if cookies:
        ydl_opts['cookiefile'] = cookies
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    title = info.get('title', 'No title found')
    description = info.get('description', 'No description found')
    
    return title, description

def get_formatted_transcript(video_id, headers, proxy=None, cookies=None):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, preserve_formatting=True, headers=headers, proxies={'https': proxy} if proxy else None, cookies=cookies)
    formatter = WebVTTFormatter()
    return formatter.format_transcript(transcript)

def create_full_transcript(video_id, headers, proxy=None, cookies=None):
    # Get the video title and description
    title, description = get_youtube_video_details(video_id, headers, proxy, cookies)
    
    # Create a string with the video info
    vid_info = f"Title: {title}\nDescription: {description}"
    
    # Get the formatted transcript
    vtt_formatted = get_formatted_transcript(video_id, headers, proxy, cookies)
    
    # Combine the video info and transcript
    full_transcript = f"{vid_info}\n\n{vtt_formatted}"
    
    return full_transcript

def save_transcript_to_file(video_id, filepath, headers, proxy=None, cookies=None):
    full_transcript = create_full_transcript(video_id, headers, proxy, cookies)
    
    with open(filepath, 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_transcript)

def process_videos(video_ids, output_dir='yt-transcripts', proxies=None, cookies=None):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving transcripts to directory: {output_dir}")

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/78.0.4093.184',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]

    for i, video_id in enumerate(video_ids, 1):
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                print(f"Processing video {i}/{len(video_ids)}: {video_id}")
                
                filename = f"transcript_{video_id}.txt"
                filepath = os.path.join(output_dir, filename)
                
                headers = {'User-Agent': random.choice(user_agents)}
                
                if proxies:
                    current_proxy = random.choice(proxies)
                    print(f"Using proxy: {current_proxy}")
                    save_transcript_to_file(video_id, filepath, headers, proxy=current_proxy, cookies=cookies)
                else:
                    save_transcript_to_file(video_id, filepath, headers, cookies=cookies)
                
                print(f"Saved transcript to: {filepath}")
                
                delay = random.uniform(30, 60)  # Increased delay between requests
                print(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
                
                break
            except Exception as e:
                print(f"Error processing video {i}/{len(video_ids)}: {video_id}")
                print(f"Error message: {str(e)}")
                if "Sign in to confirm you're not a bot" in str(e):
                    wait_time = (2 ** retries) * 60 + random.uniform(0, 30)  # Exponential backoff
                    print(f"Bot detection triggered. Waiting {wait_time:.2f} seconds before retrying...")
                    time.sleep(wait_time)
                retries += 1
                if retries >= max_retries:
                    print("Max retries reached. Continuing to next video...")
        
        print("---")

    print("Processing complete.")
    print(f"All transcripts saved in directory: {output_dir}")

if __name__ == "__main__":
    # Create a cookie jar
    cookie_jar = http.cookiejar.MozillaCookieJar('youtube_cookies.txt')
    chrome_cookies = browser_cookie3.chrome(domain_name='.youtube.com')
    for cookie in chrome_cookies:
        cookie_jar.set_cookie(cookie)
    cookie_jar.save()

    # Real YouTube video IDs
    video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw", "9bZkp7q19f0"]
    process_videos(video_ids, cookies='youtube_cookies.txt')