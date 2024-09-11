import os
import yt_dlp  # Library for downloading YouTube video information
from youtube_transcript_api import YouTubeTranscriptApi  # For accessing YouTube transcripts
from youtube_transcript_api.formatters import WebVTTFormatter  # For formatting transcripts

def get_youtube_video_details(video_id):
    # Construct the full YouTube URL from the video ID
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Options for yt_dlp to quietly extract info without downloading the video
    ydl_opts = {
        'quiet': True,  # Don't print progress to console
        'no_warnings': True,  # Don't print warnings
        'skip_download': True,  # Don't download the video, just fetch metadata
    }
    
    # Use yt_dlp to extract video information
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    # Extract title and description from the info dictionary
    # If not found, use default strings
    title = info.get('title', 'No title found')
    description = info.get('description', 'No description found')
    
    # Return the title and description as a tuple
    return title, description

def get_formatted_transcript(video_id):
    # Fetch the transcript for the given video ID
    transcript = YouTubeTranscriptApi.get_transcript(video_id, preserve_formatting=True)
    
    # Create a WebVTT formatter
    formatter = WebVTTFormatter()
    
    # Format the transcript using the WebVTT formatter
    return formatter.format_transcript(transcript)

def create_full_transcript(video_id):
    # Get the video title and description
    title, description = get_youtube_video_details(video_id)
    
    # Create a string with the video info
    vid_info = f"Title: {title}\nDescription: {description}"
    
    # Get the formatted transcript
    vtt_formatted = get_formatted_transcript(video_id)
    
    # Combine the video info and formatted transcript
    return f"{vid_info}\n\n{vtt_formatted}"

def save_transcript_to_file(video_id, filepath):
    # Get the full transcript (video details + formatted transcript)
    full_transcript = create_full_transcript(video_id)
    
    # Open the file and write the transcript
    with open(filepath, 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_transcript)

def process_videos(video_ids, output_dir='yt-transcripts'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving transcripts to directory: {output_dir}")

    for i, video_id in enumerate(video_ids, 1):
        try:
            print(f"Processing video {i}/{len(video_ids)}: {video_id}")
            
            # Create a filename using just the video ID
            filename = f"transcript_{video_id}.txt"
            # Create the full file path
            filepath = os.path.join(output_dir, filename)
            
            # Save the transcript for this video
            save_transcript_to_file(video_id, filepath)
            print(f"Saved transcript to: {filepath}")
            
        except Exception as e:
            print(f"Error processing video {i}/{len(video_ids)}: {video_id}")
            print(f"Error message: {str(e)}")
            print("Continuing to next video...")
        
        print("---")  # Separator between videos

    print("Processing complete.")
    print(f"All transcripts saved in directory: {output_dir}")

if __name__ == "__main__":
    # Real YouTube video IDs
    video_ids = ["dQw4w9WgXcQ", "jNQXAC9IVRw", "9bZkp7q19f0"]
    process_videos(video_ids)