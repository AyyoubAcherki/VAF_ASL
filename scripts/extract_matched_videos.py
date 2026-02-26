import json
import os
import subprocess
import shutil

# Paths
zip_contents_file = "zip_contents.txt"
zip_file = "train1.zip"
words_file = "new_words_to_add.txt"
classes_file = "MSASL_classes.json"
dest_base = os.path.join("train", "education")

# Load classes and target words
with open(classes_file, "r") as f:
    classes_list = json.load(f)

with open(words_file, "r") as f:
    target_words = [line.strip() for line in f if line.strip()]

# Mapping
word_to_index = {word: str(i) for i, word in enumerate(classes_list)}
index_to_word = {str(i): word for i, word in enumerate(classes_list)}

target_indices = {word_to_index[word] for word in target_words if word in word_to_index}
target_words_set = set(target_words)
for word in target_words:
    if " " in word:
        target_words_set.add(word.replace(" ", "_"))

# Read zip contents
with open(zip_contents_file, "r") as f:
    zip_entries = [line.strip() for line in f if line.strip()]

matches = []
found_words_in_zip = set()

for entry in zip_entries:
    if not entry.lower().endswith(".mp4"):
        continue
    
    # Path parts: e.g., ["train", "21", "21_801.mp4"]
    parts = entry.replace("\\", "/").split("/")
    if len(parts) < 2:
        continue
        
    parent_dir = parts[-2]
    filename = parts[-1]
    
    word = None
    
    # Check parent_dir (index or word)
    if parent_dir in target_indices:
        word = index_to_word[parent_dir]
    elif parent_dir in target_words_set:
        word = parent_dir.replace("_", " ")
        if word not in target_words and parent_dir in target_words:
            word = parent_dir
            
    # If not found in parent, check filename
    if not word and "_" in filename:
        name_part = filename.rsplit("_", 1)[0]
        if name_part in target_words_set:
            word = name_part.replace("_", " ")
            if word not in target_words and name_part in target_words:
                word = name_part
        elif name_part in target_indices:
            word = index_to_word[name_part]
            
    if word:
        matches.append((entry, word))
        found_words_in_zip.add(word)

print(f"Total entries in zip: {len(zip_entries)}")
print(f"Matches found: {len(matches)}")
print(f"Unique words found in zip: {len(found_words_in_zip)}")

# Extract matches
if matches:
    print("Starting extraction...")
    for entry, word in matches:
        target_folder_name = word.replace(" ", "_")
        target_dir = os.path.join(dest_base, target_folder_name)
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            # Entry might be something like 'train/909/file.mp4'
            subprocess.run(["tar", "-xf", zip_file, entry], check=True)
            
            # Entry is the relative path from where tar was run
            extracted_path = entry
            if os.path.exists(extracted_path):
                dest_path = os.path.join(target_dir, os.path.basename(extracted_path))
                shutil.move(extracted_path, dest_path)
                print(f"Extracted and moved: {os.path.basename(entry)} -> {target_folder_name}/")
            else:
                print(f"Warning: Extracted file not found at {extracted_path}")
        except Exception as e:
            print(f"Error extracting {entry}: {e}")

print("Extraction complete.")
