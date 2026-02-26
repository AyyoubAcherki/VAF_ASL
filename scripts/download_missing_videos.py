import json
import os
import subprocess
import time

# Paths
missing_file = "missing_videos.txt"
json_file = "MSASL_train.json"
dest_base = os.path.join("train", "education")

# Load missing words
with open(missing_file, "r") as f:
    missing_words = [line.strip() for line in f if line.strip()]

# Load JSON data
with open(json_file, "r") as f:
    videos_data = json.load(f)

# Organize JSON data by word for faster lookup
word_lookup = {}
for entry in videos_data:
    gloss = entry['clean_text'].lower()
    if gloss not in word_lookup:
        word_lookup[gloss] = []
    word_lookup[gloss].append(entry)

print(f"Loaded {len(missing_words)} words to download.")

success_count = 0
failed_words = []

for i, word in enumerate(missing_words):
    word_lower = word.lower()
    if word_lower not in word_lookup:
        # Try with underscores if spaces
        word_alt = word_lower.replace(" ", "_")
        if word_alt not in word_lookup:
            print(f"[{i+1}/{len(missing_words)}] Word '{word}' not found in MSASL_train.json")
            failed_words.append(word)
            continue
        entries = word_lookup[word_alt]
    else:
        entries = word_lookup[word_lower]

    print(f"[{i+1}/{len(missing_words)}] Downloading '{word}' ({len(entries)} samples found)...")
    
    target_dir = os.path.join(dest_base, word.replace(" ", "_"))
    os.makedirs(target_dir, exist_ok=True)
    
    word_success = False
    for j, entry in enumerate(entries):
        url = entry['url']
        start = entry['start_time']
        end = entry['end_time']
        video_id = entry.get('video_id', f'sample_{j+1}')
        
        output_filename = f"{word.replace(' ', '_')}_{video_id}.mp4"
        output_path = os.path.join(target_dir, output_filename)
        
        if os.path.exists(output_path):
            print(f"  Sample {j+1} already exists.")
            word_success = True
            continue
            
        print(f"  Downloading sample {j+1} from {url}...")
        
        # yt-dlp --download-sections "*00:00:01-00:00:05" -f "bestvideo[ext=mp4]/best[ext=mp4]/best" -o "output.mp4" URL
        # We need to format seconds to HH:MM:SS.mmm
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = seconds % 60
            return f"{h:02d}:{m:02d}:{s:06.3f}"

        time_range = f"*{format_time(start)}-{format_time(end)}"
        
        cmd = [
            'yt-dlp',
            '--download-sections', time_range,
            '--force-keyframes-at-cuts',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--merge-output-format', 'mp4',
            '-o', output_path,
            '--no-playlist',
            '--quiet',
            url
        ]
        
        try:
            result = subprocess.run(cmd, timeout=300) # 5 min timeout
            if result.returncode == 0:
                print(f"  Successfully downloaded sample {j+1}")
                word_success = True
                # Limit to 3 samples per word for now to save time and space
                if j >= 2:
                    break
            else:
                print(f"  Failed to download sample {j+1}")
        except Exception as e:
            print(f"  Error downloading sample {j+1}: {e}")
            
    if word_success:
        success_count += 1
    else:
        failed_words.append(word)
        
    # Small pause to be nice to servers
    time.sleep(1)

print(f"Download process complete. Successfully added {success_count} words.")
if failed_words:
    with open("failed_downloads.txt", "w") as f:
        for w in failed_words:
            f.write(w + "\n")
    print(f"Failed to find/download {len(failed_words)} words. Logged to 'failed_downloads.txt'")
