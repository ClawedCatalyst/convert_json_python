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
            question_string = ""
            current_index = index + 1
            while lines[current_index] != "[OPTION 1]":
                if lines[current_index].startswith("![original image]"):
                    current_index = current_index + 1
                else:
                    question_string += lines[current_index]
                    current_index = current_index + 1
                    if lines[current_index] != "[OPTION 1]":
                        question_string += "\n"

            question_object["question"] = {"text": question_string, "image": None}

        elif line.startswith("[OPTION"):
            """store the options"""
            if not lines[index + 1].startswith("![original image]"):
                option_text = lines[index + 1]
            else:
                option_text = None

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
            solution_string = ""
            current_index = index + 2
            while lines[current_index] != "[OBJECT END]":
                if lines[current_index].startswith("![original image]"):
                    current_index = current_index + 1
                else:
                    solution_string += lines[current_index]
                    current_index = current_index + 1
                    if lines[current_index] != "[OBJECT END]":
                        solution_string += "\n"

            if solution_string == "":
                solution_string = "No Solution Available"

            question_object["solution"] = {"text": solution_string, "image": None}
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
