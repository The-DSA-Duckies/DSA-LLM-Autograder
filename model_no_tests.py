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
        model="gpt-4", # note, test this with gpt-4 for quality improvements
        messages=[
            {"role": "system", "content": "You are an instructor."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content

@stub.function(secret=modal.Secret.from_name("my-anthropic-secret"))
def complete_text_anthropic(prompt):
    import anthropic

    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=32000,
        temperature=0.0,
        system="Respond only in Yoda-speak.",
        messages=[
            {"role": "system", "content": "You are an instructor who is very good at grading."},
            {"role": "user", "content": prompt},
        ]
    )

    return message.content

@stub.local_entrypoint()
def main():
    assignment = open("assignment.txt", "r").read()
    rubric = open("rubric.txt", "r").read()
    student_submission = open("./student_stuff/student_report.txt", "r",    encoding='utf-8').read()
    #example = open("example.txt", "r", encoding='utf-8').read()
    student_code = open("./student_stuff/main.cpp", "r", encoding='utf-8').read()

    questions = [
        f"""
        Act as a very dilligent and extremely harsh teacher's assistant grading a given assignment from the rubric provided. Explain for each decision you make why you
        made it, and why it checks off certain boxes on the rubric. 

        Do the grading step by step by going through each part of the ASSIGNMENT, STUDENT REPORT SUBMISSION, STUDENT CODE SUBMISSION, and STUDENT TEST CASES SUBMISSION. The STUDENT REPORT SUBMISSION contains student explanations. The STUDENT CODE SUBMISSION contains the student's code for their project. The STUDENT TEST CASES SUBMISSION is missing, and you should give the student no points for failing to submit it. Compare your grading step by step to the grading criteria. Use the RUBRIC for each bullet to grade upon. The answer should be formatted as follows in a single text block:

        CRITERIA: [go through each criteria and explain if the student has completed it]

        FEEDBACK: [what did the student do well and what could be improved (but isn't wrong) in plain text]

        FIXING: [Anything that is missing, incorrect or incomplete from the ASSIGNMENT]

        GRADE: [Each breakdown of points lost for missing parts of the rubric with explanation and use EVERY part of the rubric with points shown like x/y where x is points earned, y is points possible for each rubric item.]

        Here follows the assignment, grading criteria and student report submission, student code submission, and student test cases submission.

        ASSIGNMENT:
        \"\"\"
        {assignment}
        \"\"\"

        GRADING:
        \"\"\"
        {rubric}
        \"\"\"

        STUDENT REPORT SUBMISSION:
        \"\"\"
        {student_submission}
        \"\"\"

        STUDENT CODE SUBMISSION:
        \"\"\"
        {student_code}
        \"\"\"

        STUDENT TEST CASES SUBMISSION:
        \"\"\"
        
        \"\"\"

        Please use the following deducations and explain why you are deducting for each of these:

    Time complexity analysis - Functions
        − 1.67 pts
        Grading comment:
        missing variables descriptions

        − 1.67 pts
        Grading comment:
        missing justification

    Time complexity analysis - Main
        
        − 1.67 pts
        Grading comment:
        missing variables descriptions

        − 1.67 pts
        Grading comment:
        missing justification

    Bonus catch tests
        
        − 5 pts
        Grading comment:
        5 catch test cases are not provided 
    
    """
    ]
    for question in questions:
        print("Sending new request:", question)
        print(complete_text.remote(question))
            

