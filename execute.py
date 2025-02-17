# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests",
#     "typing"
# ]
# ///
import requests
import subprocess
import os
from datetime import datetime
import re
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
def extract_email_sender(input_path="./data/email.txt", output_path="./data/email-sender.txt"):
    # Read the email content from the file
   proxy_url="http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
   with open(input_path, 'r', encoding='utf-8') as f:
        email_content = f.read()
   auth_token =os.environ["AIPROXY_TOKEN"]
   payload = {
        "model": "gpt-4o-mini",
        "messages": [
          {"role": "system", "content": "You are an assistant skilled at extracting information from emails."},
          {"role": "user", "content": f"Extract the sender's email address from the following email content and              respond with just the email address, nothing else:\n\n{email_content}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

   response = requests.post(
            proxy_url,
            headers={"Content-Type": "application/json",

            "Authorization": f"Bearer {auth_token}"},
            data=json.dumps(payload)
        )
   #email_address = response['choices'][0]['message']['content'].strip()
   #print(response.text)
   response_json = response.json()
   email_address=content = response_json["choices"][0]["message"]["content"]
   with open(output_path, 'w', encoding='utf-8') as f:
        f.write(email_address + '\n')

   print(f"Extracted email address: {email_address}")
   return email_address
def create_markdown_index(docs_dir="./data/docs", output_path="./data/docs/index.json"):
    try:
        docs_path = Path(docs_dir)
        index = {}

        # Find all .md files recursively
        md_files = docs_path.rglob("*.md")

        for md_file in md_files:
            # Extract the first H1 title from each file
            title = None
            with md_file.open('r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("# "):  # H1 in Markdown
                        title = line.strip("# ").strip()
                        break

            # Only add to index if a title is found
            if title:
                relative_path = md_file.relative_to(docs_path)
                index[str(relative_path)] = title

        # Write index to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=4)

        print(f"Markdown index created successfully at {output_path}")
        return "Markdown index created successfully at" + output_path
    except Exception as e:
        print(f"An error occurred: {e}")



def extract_recent_log_lines(logs_dir="./data/logs", output_file="./data/logs-recent.txt"):
    try:
        logs_path = Path(logs_dir)

        # Collect all .log files and sort by modified time (descending)
        log_files = sorted(
            logs_path.glob("*.log"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        # Take the 10 most recent files
        recent_files = log_files[:10]

        # Extract the first line of each file
        first_lines = []
        for log_file in recent_files:
            with log_file.open('r') as f:
                first_line = f.readline().strip()
                first_lines.append(first_line)

        # Write the lines to the output file
        with open(output_file, 'w') as f:
            for line in first_lines:
                f.write(line + '\n')

        print(f"Extracted first lines from the 10 most recent .log files into {output_file}")
        return "Extracted first lines from the 10 most recent .log files into" + output_file
    except Exception as e:
        print(f"An error occurred: {e}")

def sort_contacts(input_path="./data/contacts.json", output_path="./data/contacts-sorted.json"):
    try:
        # Read the contacts JSON file
        with open(input_path, 'r') as f:
            contacts = json.loads(f.read())

        # Sort the contacts by last_name, then first_name
        contacts_sorted = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))

        # Write the sorted contacts to a new JSON file
        with open(output_path, 'w') as f:
            json.dump(contacts_sorted, f, indent=4)

        print(f"Sorted contacts have been written to {output_path}")
        return "Sorted contacts have been written to"+output_path
    except Exception as e:
        print(f"An error occurred: {e}")

def count_day_of_week(day_of_week, input_file="./data/dates.txt", output_file="./data/dates-wednesdays.txt"):
    try:
        # Read dates from file
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # Normalize and parse dates into datetime objects
        date_objects = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                # Try multiple date formats
                date = parse_date(line)
                date_objects.append(date)
            except ValueError as e:
                print(f"Skipping invalid date '{line}': {e}")

        # Count occurrences of the specified day of the week
        day_count = sum(1 for date in date_objects if date.strftime('%A').lower() == day_of_week.lower())

        # Write the result to output file
        with open(output_file, 'w') as f:
            f.write(str(day_count) + '\n')
        outputStr= "Counted"+ str(day_count) + "occurrences of"+ day_of_week +"."
        print(f"Counted {day_count} occurrences of {day_of_week}.")
        return outputStr

    except Exception as e:
        print(f"An error occurred: {e}")


def parse_date(date_string):
    """Helper to parse a date string with multiple formats."""
    date_formats = [
        "%Y/%m/%d %H:%M:%S",
        "%b %d, %Y",
        "%Y-%m-%d",
        "%d-%b-%Y"
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            pass

    # If no format works, raise an error
    raise ValueError(f"Date format not recognized: {date_string}")


def format_mdfile(file_path="/data/format.md"):
    try:
        # Ensure .venv exists
        if not os.path.exists(".venv"):
            subprocess.run(["uv", "venv", ".venv"], check=True)

        # Activate virtual environment (bash-like activation)
        activate_venv = ".venv/bin/activate"
        if not os.path.exists(activate_venv):
            raise FileNotFoundError(f"Virtual environment activation script not found: {activate_venv}")

        # Format markdown with Prettier using npx
        subprocess.run(["npx", "prettier@3.4.2", "--write", file_path], check=True)

        print(f"Formatted {file_path} successfully.")
        return "Formatted"+file_path+"successfully."
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error formatting {file_path}: {e}")

def calculate_sales(output_path="/data/ticket-sales-gold.txt"):
    output_path = Path(output_path)
    db_path = Path("/data/ticket-sales.db")
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to calculate total sales for "Gold" ticket type
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    result = cursor.fetchone()

    # Extract the total sales value (handle NULL case)
    total_sales = result[0] if result[0] is not None else 0

    # Write the result to the output file
    with output_path.open('w') as f:
        f.write(str(total_sales))

    # Close the database connection
    conn.close()
    return "sales written to "+str(output_path)

def function_gpt(user_input: str, tools: list[Dict[str, Any]]) -> Dict[str, Any]:
    proxy_url="http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    auth_token =os.environ["AIPROXY_TOKEN"]
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": user_input},

        ],
        "tools": tools,
    "tool_choice": "auto",
    "max_tokens": 500,
    "temperature": 0.7
    }

    response = requests.post(
            proxy_url,
            headers={"Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"},
            data=json.dumps(payload)
        )
    response_json = response.json()
    print (str(response_json))
    return response.json()["choices"][0]["message"]

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_email_sender",
            "description": "Extract sender email from a specific file in directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "input file path hardcoded to ./data/email.txt"
                    }
                },
                "required": ["input_path"],
                "additionalProperties": False
                },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_day_of_week",
            "description": "To count the occurances of a specific day of a week in a file with various dates",
            "parameters": {
                "type": "object",
                "properties": {
                    "day_of_week": {
                        "type": "string",
                        "description": "day of week"
                    },
                    "input_file": {
                        "type": "string",
                        "description": "input file path hardcoded to ./data/dates.txt"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "output  file path in ./data/ folder with dynamuc name as day-<day-fod-week>.txt"
                    }
                },
                "required": ["day_of_week","input_file","output_file"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sales",
            "description": "calculate sales of provided item from sqllite db",
            "parameters": {
                "type": "object",
                "properties": {
                    "output_path": {
                        "type": "string",
                        "description": "output  file path of sales of prompted item ticket type  having the format of data/ticket-sales-<item>.txt. Example: for gold it will be data/ticket-sales-gold.txt "
                    }
                },
                "required": ["output_path"],
                "additionalProperties": False
                },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_markdown_index",
            "description": "Reads markdown .md file and provides index betweeen markdown files and  headings",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "input folder  path hardcoded to ./data/docs"
                    }
                },
                "required": ["input_path"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_recent_log_lines",
            "description": "extract log file and pareses first line from recent 10 log files and writes to logs-recent  ",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "input folder  path hardcoded to ./data/logs"
                    }
                },
                "required": ["input_path"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sort_contacts",
            "description": "read contacts file and writes first and last names in sorted oder",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "input file  path hardcoded to ./data/contacts.json"
                    }
                },
                "required": ["input_path"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "format_mdfile",
            "description": "format md file using prettier",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "input file  path hardcoded to /data/format.md"
                    }
                },
                "required": ["file_path"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

]
#function_gpt("The file /data/dates.txt contains a list of dates, one per line. Count the number of Wednesdays in the list, and write just the number to /data/dates-wednesdays.txt", [tools])
# Run the function
#format_markdown_with_uv()
#count_day_of_week("Wednesday")
#sort_contacts()
#extract_recent_log_lines()
#create_markdown_index()
#extract_email_sender()
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
)
@app.get("/read")
async def read_file(path: str):
    # Check if the file exists
    base_dir = Path("/data").resolve()
    target_path = (base_dir / path).resolve()

    # Check if the target path is within /data
    if not target_path.is_relative_to(base_dir):
        raise HTTPException(status_code=403, detail="Access denied: Path is outside /data directory.")

    if os.path.exists(path) and os.path.isfile(path):
        # Open the file and return its content
        with open(path, 'r') as file:
            content = file.read()
        return PlainTextResponse(content=content, status_code=200)
    else:
        # File not found, return 404 with empty body
        raise HTTPException(status_code=404, detail="File not found")
@app.post("/run")
async def run_task(task: Optional[str] = None):
    if task is None:
        return {"error": "Task description is required"}
    response=function_gpt(task,tools)
    print("response=" + str(response))
    tool_calls = response.get('tool_calls', [])

    for tool_call in tool_calls:
        function_name = tool_call['function']['name']
        arguments_json = tool_call['function']['arguments']
        arguments = json.loads(arguments_json)

    # Invoke the corresponding function dynamically
        function_executed=False
        if function_name == 'count_day_of_week':
            print("in day of week function")
            result = count_day_of_week(**arguments)
            function_executed=True
            print(f"Function Result: {result}")
        else:
            print(f"Unknown function: {function_name}")

        if function_name == 'calculate_sales':
            result = calculate_sales(**arguments)
            function_executed=True
        function_map = {
            "extract_email_sender": extract_email_sender,
            "create_markdown_index": create_markdown_index,
            "extract_recent_log_lines": extract_recent_log_lines,
            "sort_contacts": sort_contacts,
            "format_mdfile": format_mdfile
        }
        print ("***function name"+function_name)
        if function_executed == False:
           if function_name in function_map:
            result = function_map[function_name]()
           else:
            result = f"Function '{function_name}' not found"
        #extract_recent_log_lines()

        return {"results": result}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
