import os
import yt_dlp

def extract_m3u8_link(file_path):
    """Extracts the first valid M3U8 link from a text file."""
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '.m3u8' in line:
                # Ensure we extract only the URL part if there's extra text
                m3u8_url = line.split()[-1]  # Extract the last part as the URL
                if m3u8_url.startswith("http"):
                    return m3u8_url  # Return the cleaned M3U8 link
    return None  # Return None if no valid M3U8 link is found

def download_m3u8_from_file(file_path):
    # Extract the M3U8 link from the file
    m3u8_url = extract_m3u8_link(file_path)
    
    if not m3u8_url:
        print(f"No valid M3U8 link found in {file_path}. Skipping file.")
        return

    # Extract the base filename and number from the text file's name
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    
    # Ensure the filename contains a number
    try:
        base_number = int(base_filename)  # Convert filename to integer
        output_number = base_number + 175
        output_file = f"{output_number}.MP4"  # Create output filename
    except ValueError:
        print(f"Skipping {file_path}: Filename does not contain a valid number.")
        return

    # Check if the file already exists to prevent duplicate downloads
    if os.path.exists(output_file):
        print(f"{output_file} already exists. Skipping download.")
        return

    # Define yt-dlp options
    ydl_opts = {
        'format': 'best',  # Default to download the best available quality
        'noplaylist': True,  # Do not download playlists, just the video
        'quiet': True,  # Suppress output for the format list
    }

    # Fetch available formats
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Get information about the video
        try:
            info_dict = ydl.extract_info(m3u8_url, download=False)
        except yt_dlp.utils.DownloadError as e:
            print(f"Error downloading {m3u8_url}: {e}")
            return
        
        # Print available formats
        print(f"Available formats for {output_file}:")
        for format_info in info_dict['formats']:
            print(f"Format ID: {format_info['format_id']}, Resolution: {format_info.get('height', 'N/A')}p, URL: {format_info['url']}")
        
        # Check for 720p format
        target_format = next((f for f in info_dict['formats'] if f.get('height') == 720), None)

        if target_format:
            print(f"\nDownloading 720p format for {output_file}...")
            # Download the selected 720p format
            ydl_opts['format'] = target_format['format_id']  # Set to download 720p
            ydl_opts['outtmpl'] = output_file  # Output path for the downloaded file
            
            # Create a new instance to download the video with the specified format
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([m3u8_url])
        else:
            print(f"720p format not found for {output_file}. Downloading best available format...")
            # Fallback to the best format if 720p is not available
            ydl_opts['format'] = 'best'  # Reset to best format
            ydl_opts['outtmpl'] = output_file  # Output path for the downloaded file
            
            # Create a new instance to download the video with the specified format
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([m3u8_url])

if __name__ == "__main__":
    # Get the current directory where the script is located
    current_directory = os.getcwd()
    
    # Loop through all .txt files in the directory
    for filename in os.listdir(current_directory):
        if filename.endswith(".txt"):
            txt_file_path = os.path.join(current_directory, filename)
            print(f"Processing {txt_file_path}...")
            download_m3u8_from_file(txt_file_path)
