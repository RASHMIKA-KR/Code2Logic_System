import google.generativeai as genai
import os

genai.configure(api_key='AIzaSyDIP2mXBZOEbmw40qy5rn0OjXHxBxztAm8')

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[])

example_pseudo = """
OUTPUT "are we insane?"
INPUT ans
IF ans = "yes" THEN
    OUTPUT "correct"
ELSE
    OUTPUT "incorrect"
ENDIF
"""

rules_and_syntax = """
Rules
STOP and START not need to be added

Indents don't affect the program, so nothing has to be indented, and incorrect indentation is allowed

The capitalization of the keywords is extremely important. If an error occurs, double check if you have capitalized the keywords like "TO" and "FOR" properly

ELSE IF is not available, but nested IFs are possible

The ENDIF, NEXT var, and ENDWHILE blocks are mandatory

Syntax Guide
Input and Output:
INPUT x
OUTPUT x
INPUT X
OUTPUT var
OUTPUT "hello"
IF statements:
IF condition THEN
ELSE
ENDIF
IF x < 3 THEN
  OUTPUT X
ELSE
  OUTPUT x*2
ENDIF
The else statement is optional (ENDIF is still necessary)

IF x < 3 THEN
 OUTPUT X
ENDIF
Process-type blocks:
x = x + 1
y = x / 2
While loops:
WHILE condition DO
ENDWHILE
WHILE x < 5 DO
  OUTPUT x
ENDWHILE
For loops:
FOR var <- start TO end
NEXT var
FOR i <- 1 TO 5
  OUTPUT i
NEXT i
"""


def generate_pseudocode(file_content):
    convo = model.start_chat(history=[])
    convo.send_message(
        f"Write pseudocode for the code:\n\n{file_content}\n\nfollowing {rules_and_syntax} and considering the following as example pseudocode ---{example_pseudo}"
    )
    return convo.last.text
import os

def process_directory(directory):
    pseudo_dir = os.path.join(os.path.dirname(__file__), '..', 'pseudo')
    os.makedirs(pseudo_dir, exist_ok=True)

    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                file_content = file.read()
                generated_pseudo = generate_pseudocode(file_content)

                with open(os.path.join(pseudo_dir, f'pseudo_{filename}'), 'w') as pseudo_file:
                    pseudo_file.write(generated_pseudo)

directory_path = os.path.join(os.path.dirname(__file__), '..', 'codes')
process_directory(directory_path)
