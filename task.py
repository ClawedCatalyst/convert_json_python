import json
import os
import random
import re
import string

import requests
from bson import ObjectId


def save_image_to_folder(url):
    if not os.path.exists("images"):
        os.makedirs("images")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = url.split("/")[-1]
            with open(f"images/{file_name}", "wb") as image:
                image.write(response.content)
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_random_5_character_id():
    characters = string.ascii_letters
    return "".join(random.choice(characters) for _ in range(5))


def generate_random_mongo_id():
    mongo_id = "".join(random.choice("0123456789abcdef") for _ in range(24))
    return mongo_id


def convert_to_json_file(content):
    questions = []
    question_object = {}
    lines = content.strip().split("\n")
    for index, line in enumerate(lines):
        if line.startswith("[OBJECT START]"):
            question_object["id"] = generate_random_mongo_id()
        elif line.startswith("[SINGLE CORRECT]"):
            question_object["type"] = "singleCorrect"
        elif line.startswith("[QUESTION]"):
            question_object["question"] = {"text": lines[index + 1], "image": None}
        elif line.startswith("[OPTION"):
            option_text = lines[index + 1]
            is_correct = False
            if "options" not in question_object:
                question_object["options"] = []
            question_object["options"].append(
                {
                    "id": generate_random_5_character_id(),
                    "text": option_text,
                    "image": None,
                    "isCorrect": is_correct,
                }
            )
        elif line.startswith("[SOLUTION]"):
            correct_option = lines[index + 1]
            correct_option = correct_option.split("[")[-1].split("]")[0]
            question_object["options"][int(correct_option) - 1]["isCorrect"] = True
            solution = "No Solution Available"
            if lines[index + 2].startswith("![original image]") and not lines[
                index + 3
            ].startswith("[OBJECT END]"):
                solution = lines[index + 3]
            elif not lines[index + 2].startswith("![original image]") and not lines[
                index + 2
            ].startswith("[OBJECT END]"):
                solution = lines[index + 2]
            question_object["solution"] = {"text": solution, "image": None}
        elif line.startswith("![original image]"):
            regex = r"\((.*?)\)"
            url = re.search(regex, line)
            url = url.group(1)
            save_image_to_folder(url)
        elif line.startswith("[OBJECT END]"):
            questions.append(question_object)
            question_object = {}

    return questions


if __name__ == "__main__":
    file_name = "input_file.txt"

    with open(file_name, "r") as file:
        content = file.read()
    json_array = json.dumps(convert_to_json_file(content), indent=2)
    output_file = "output_file.json"
    with open(output_file, "w") as file:
        file.write(json_array)
