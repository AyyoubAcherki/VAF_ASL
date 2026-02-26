import json

with open("MSASL_classes.json", "r") as f:
    classes = json.load(f)

with open("missing_videos.txt", "r") as f:
    missing = [line.strip() for line in f if line.strip()]

for word in missing[:10]:
    if word in classes:
        print(f"{word}: {classes.index(word)}")
    else:
        print(f"{word}: NOT FOUND")
