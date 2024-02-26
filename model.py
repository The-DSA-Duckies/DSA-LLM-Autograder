import os
import time

import modal

from modal import Image, Stub, wsgi_app

bot_image = modal.Image.debian_slim().pip_install("openai")
bot_image = bot_image.pip_install("numpy")
bot_image = bot_image.pip_install("pandas")
bot_image = bot_image.pip_install("youtube_transcript_api")
bot_image = bot_image.pip_install("flask")
bot_image = bot_image.pip_install("flask_cors")

stub = modal.Stub("GPT wins 😔", image=bot_image)

@stub.function(secret=modal.Secret.from_name("my-openai-secret"))
def complete_text(prompt):
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125", # note, test this with gpt-4 for quality improvements
        messages=[
            {"role": "system", "content": "You are an instructor."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

@stub.local_entrypoint()
def main():
    assignment = open("assignment.txt", "r").read()
    rubric = open("rubric.txt", "r").read()
    student_submission = open("student.txt", "r", encoding='utf-8').read()
    example = open("example.txt", "r", encoding='utf-8').read()

    questions = [
        f"""
        Act as a very dilligent teacher's assistant grading a given assignment from the rubric provided. Explain for each decision you make why you
        made it, and why it checks off certain boxes on the rubric. 

        Do the grading step by step by going through each part of the ASSIGNMENT and STUDENT SUBMISSION. Then compare that answer to the grading criteria. Use the EXAMPLE FEEDBACK for formatting, changing the w, x, y and z variables to the correct numbers. The answer should be formatted as follows in a single text block:

        CRITERIA: [go through each criteria and explain if the student has completed it]

        FEEDBACK: [what did the student do well and what could be improved (but isn't wrong) in plain text]

        FIXING: [Anything that is missing, incorrect or incomplete from the ASSIGNMENT]

        GRADE: [Each breakdown of points lost for missing parts of the rubric]

        Here follows the assignment, grading criteria and student submission

        ASSIGNMENT:
        \"\"\"
        {assignment}
        \"\"\"

        GRADING:
        \"\"\"
        {rubric}
        \"\"\"

        STUDENT SUBMISSION:
        \"\"\"
        {student_submission}
        \"\"\"

        EXAMPLE FEEDBACK:
        \"\"\"
        {example}    
        \"\"\"
    """
    ]
    for question in questions:
        print("Sending new request:", question)
        print(complete_text.remote(question))
            

