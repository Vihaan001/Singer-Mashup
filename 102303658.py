import sys
import os
import shutil
import yt_dlp
from pydub import AudioSegment

def download_videos(singer_name, num_videos):
    """Searches and downloads the exact number of videos, saving them as MP3s."""
    print(f"Searching for {num_videos} videos of '{singer_name}'...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'max_downloads': num_videos,
        'extractor_args': {'youtube': {'client': ['android', 'ios']}},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{num_videos}:{singer_name}"
            ydl.extract_info(search_query, download=True)
            
    except Exception as e:
        # Ignore the "error" if it's just yt-dlp telling us it hit our download limit
        if "Maximum number of downloads reached" in str(e) or "MaxDownloadsReached" in str(type(e)):
            pass # This is expected, do nothing and continue!
        else:
            print(f"Error downloading videos: {e}")
            sys.exit(1)

    # Grab all MP3s in the folder
    downloaded_files = [
        os.path.join('downloads', f) 
        for f in os.listdir('downloads') 
        if f.endswith('.mp3')
    ]
    
    print(f"\nSuccessfully downloaded and converted {len(downloaded_files)} files.")
    return downloaded_files

def process_and_merge_audio(file_paths, duration_sec, output_filename):
    """Trims and merges all provided audio files."""
    print(f"Trimming {len(file_paths)} files to {duration_sec} seconds each and merging...")
    combined_audio = AudioSegment.empty()
    duration_ms = duration_sec * 1000  
    
    try:
        for file in file_paths:
            audio = AudioSegment.from_file(file)
            trimmed_audio = audio[:duration_ms]
            combined_audio += trimmed_audio  # Appends the audio clip
                
        # Export the final master file
        combined_audio.export(output_filename, format="mp3")
        print(f"\n🎉 Success! Mashup saved as {output_filename}")
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        sys.exit(1)

def main():
    # [cite_start]1. Validate the correct number of parameters [cite: 26]
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters.")
        print("Usage: python 102303658.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer_name = sys.argv[1]
    output_filename = sys.argv[4]

    # [cite_start]2. Handle exceptions and validate integer inputs [cite: 28]
    try:
        num_videos = int(sys.argv[2])
        audio_duration = int(sys.argv[3])
    except ValueError:
        print("Error: <NumberOfVideos> and <AudioDuration> must be integers.")
        sys.exit(1)

    # [cite_start]Assignment constraints warnings [cite: 18, 21]
    if num_videos <= 10:
        print("Warning: Assignment requires NumberOfVideos to be > 10.")
    if audio_duration <= 20:
        print("Warning: Assignment requires AudioDuration to be > 20.")

    # Create a fresh temporary directory for downloads
    if os.path.exists('downloads'):
        shutil.rmtree('downloads')
    os.makedirs('downloads')

    # 3. Execute the core tasks
    downloaded_files = download_videos(singer_name, num_videos)
    
    if downloaded_files:
        process_and_merge_audio(downloaded_files, audio_duration, output_filename)
        
    # 4. Clean up the downloads folder ruthlessly
    if os.path.exists('downloads'):
        shutil.rmtree('downloads')

if __name__ == "__main__":

    main()
