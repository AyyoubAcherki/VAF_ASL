import ast
import os

with open(r"C:\Users\Probook\Desktop\new project\words_list.txt", "r", encoding="utf-16") as f:
    content = f.read()
    # Extract the list part
    list_str = content.split("=")[1].strip()
    words = ast.literal_eval(list_str)

print(f"Total words in words_list.txt: {len(words)}")

train_dir = r"C:\Users\Probook\Desktop\new project\train"
existing_dirs = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
print(f"Existing folders in train: {len(existing_dirs)}")

new_words = [w for w in words if w not in existing_dirs]
print(f"New words to add: {len(new_words)}")

# Save the new words to a file for later use
with open("new_words_to_add.txt", "w") as f:
    for w in new_words:
        f.write(w + "\n")
