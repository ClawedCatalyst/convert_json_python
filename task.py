import json
import os
import random
import re
import string

import requests


def save_image_to_folder(url):
    """method to save images to a folder named images"""

    if not os.path.exists("images"):
        os.makedirs("images")
    try:
        # Download image
        response = requests.get(url)
        if response.status_code == 200:
            # split the url to get uuid of the image with the extention ( ex .png )
            file_name = url.split("/")[-1]
            with open(f"images/{file_name}", "wb") as image:
                image.write(response.content)

    except Exception as e:
        # error message if an exception occurs
        print(f"An error occurred: {e}")


def generate_random_5_character_id():
    """method to generate character id for options , length 5."""

    characters = string.ascii_letters
    return "".join(random.choice(characters) for _ in range(5))


def generate_random_mongo_id():
    """method to generate a random 24 character id of alphabets and digits"""

    mongo_id = "".join(random.choice("0123456789abcdef") for _ in range(24))
    return mongo_id


def convert_to_json_file(content):
    """method to convert the given txt file to json file of desired format"""

    # questions list to store all the question with their options and solution i.e question_object.
    questions = []

    # a question object
    question_object = {}
    lines = content.strip().split("\n")
    for index, line in enumerate(lines):
        if line.startswith("[OBJECT START]"):
            """whenever a new question object starts first generates random mongo id of 24 digits"""

            question_object["id"] = generate_random_mongo_id()

        elif line.startswith("[SINGLE CORRECT]"):
            """mark the question as single correct"""

            question_object["type"] = "singleCorrect"

        elif line.startswith("[QUESTION]"):
            """now store the question"""

            question_object["question"] = {"text": lines[index + 1], "image": None}

        elif line.startswith("[OPTION"):
            """store the options"""

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
            """get the solution and check if the question consists of a solution or not"""

            correct_option = lines[index + 1]
            correct_option = correct_option.split("[")[-1].split("]")[0]
            question_object["options"][int(correct_option) - 1]["isCorrect"] = True

            # extract the solution text and save it in the question_object
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
            """save the object in the questions list"""

            questions.append(question_object)
            question_object = {}

    return questions


if __name__ == "__main__":
    # input file name
    file_name = "input_file.txt"

    # reading the content of the file
    with open(file_name, "r") as file:
        content = file.read()

    # getting the final list of objects and converting it to json
    json_array = json.dumps(convert_to_json_file(content), indent=2)
    output_file = "output_file.json"

    # saving the json array in a .json file
    with open(output_file, "w") as file:
        file.write(json_array)

    print("File has been converted")
