import json
import os

# Load classes and target words
with open("MSASL_classes.json", "r") as f:
    classes_list = json.load(f)

with open("new_words_to_add.txt", "r") as f:
    target_words = [line.strip() for line in f if line.strip()]

word_to_index = {word: str(i) for i, word in enumerate(classes_list)}
target_indices = {word_to_index[word] for word in target_words if word in word_to_index}
target_words_set = {w.replace(" ", "_") for w in target_words}
target_words_set.update(set(target_words))

print(f"Target indices sample: {list(target_indices)[:5]}")
print(f"Target words sample: {list(target_words_set)[:5]}")

match_count = 0
with open("zip_contents.txt", "r") as f:
    for line in f:
        line = line.strip().replace("\\", "/")
        if not line.lower().endswith(".mp4"):
            continue
        
        parts = line.split("/")
        if len(parts) < 2:
            continue
        
        parent = parts[-2]
        filename = parts[-1]
        
        if parent in target_indices or parent in target_words_set:
            match_count += 1
            if match_count <= 5:
                print(f"Match found: {line}")

print(f"Total potential matches: {match_count}")
