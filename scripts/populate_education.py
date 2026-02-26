import json
import os
import shutil

# Paths
source_dirs = [
    r"C:\Users\Probook\Desktop\msasl-video-downloader-master\MS-ASL1000\train",
    r"C:\Users\Probook\Desktop\msasl-video-downloader-master\MS-ASL1000\test"
]
dest_base = r"C:\Users\Probook\Desktop\new project\train\education"
words_file = r"C:\Users\Probook\Desktop\new project\new_words_to_add.txt"
classes_file = r"C:\Users\Probook\Desktop\new project\MSASL_classes.json"

# Load classes
with open(classes_file, "r") as f:
    classes_list = json.load(f)

# Load target words
with open(words_file, "r") as f:
    target_words = [line.strip() for line in f if line.strip()]

# Mapping
index_to_word = {str(i): word for i, word in enumerate(classes_list)}
word_to_index = {word: str(i) for i, word in enumerate(classes_list)}

target_indices = {word_to_index[word] for word in target_words if word in word_to_index}
target_words_set = set(target_words)
for word in target_words:
    if " " in word:
        target_words_set.add(word.replace(" ", "_"))

print(f"Target words: {len(target_words)}")

# Process files
moved_count = 0
found_words = set()

for source_dir in source_dirs:
    if not os.path.exists(source_dir):
        print(f"Skipping missing source: {source_dir}")
        continue
        
    print(f"Scanning {source_dir}...")
    files = os.listdir(source_dir)
    for filename in files:
        if not filename.lower().endswith(".mp4"):
            continue
            
        word = None
        if "_" in filename:
            name_part = filename.rsplit("_", 1)[0]
            if name_part in target_words_set:
                word = name_part.replace("_", " ")
                if word not in target_words and name_part in target_words:
                    word = name_part
            elif name_part in target_indices:
                word = index_to_word[name_part]
        
        if word:
            target_folder_name = word.replace(" ", "_")
            target_dir = os.path.join(dest_base, target_folder_name)
            os.makedirs(target_dir, exist_ok=True)
            
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(target_dir, filename)
            
            # Use copy2 to keep metadata
            shutil.copy2(src_path, dst_path)
            moved_count += 1
            found_words.add(word)

print(f"Successfully copied {moved_count} videos total.")
print(f"Categorized {len(found_words)} distinct words.")

missing_words = set(target_words) - found_words
print(f"Missing words: {len(missing_words)}")
with open(r"C:\Users\Probook\Desktop\new project\missing_videos.txt", "w") as f:
    for w in sorted(list(missing_words)):
        f.write(w + "\n")
