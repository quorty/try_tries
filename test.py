## write to file words.txt
words = ["battery", "car", "train", "gas"]
with open("words.txt", 'w') as text_file:
    for word in words:
        text_file.write(word + '\0' + '\n')