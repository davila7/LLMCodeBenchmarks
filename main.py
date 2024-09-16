import openai
import json
import time
import sys
import traceback
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Models to test
MODELS = [
    # "o1-preview",
    # "o1-mini",
    # "gpt-4o-mini",
    # "gpt-4o",
    # "gpt-4",
    "gpt-3.5-turbo"
]

# Load tasks
def load_tasks(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_code(model, prompt):
    try:
        full_prompt = f"{prompt}\n\nPlease provide ONLY the Python code without additional explanations or Markdown code blocks"
        message = [{"role": "user", "content": full_prompt}]
        
        if model in ["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-3.5-turbo"]:
            message.insert(0, {"role": "system", "content": "You are a helpful assistant for writing code."})
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=message
        )
        code = response.choices[0].message['content'].strip()
        return code
    except Exception as e:
        print(f"Error: {model}: {e}")
        return ""

def clean_code(code):
    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)
    match = re.search(r"def\s+\w+\s*\(.*\):", code)
    if match:
        start = match.start()
        code = code[start:]
    return code.strip()

def eval_function(code, test_cases):
    local_vars = {}
    try:
        exec(code, {}, local_vars)
        func = None
        for name, obj in local_vars.items():
            if callable(obj):
                func = obj
                break
        if func is None:
            return False, "No function found in the generated code.", 0
        
        for idx, caso in enumerate(test_cases, 1):
            input_val = caso["input"]
            expected = caso["expected"]
            try:
                start_time = time.time()
                result = func(input_val)
                end_time = time.time()
                execution_time = end_time - start_time
                if result != expected:
                    return False, f"Failure in case #{idx}: input={input_val}, expected={expected}, got={result}", execution_time
            except Exception as e:
                tb = traceback.format_exc()
                return False, f"Error executing case #{idx}: {e}\n{tb}", 0
        
        return True, "All test cases passed", execution_time
    
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error executing code: {e}\n{tb}", 0

def main():
    TASKS = load_tasks('tasks.json')
    result = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_eval_{timestamp}.json"

    for model in MODELS:
        print()
        print(f"Evaluating model: {model}")
        model_result = {"model": model, "task": []}

        for idx, task in enumerate(TASKS, 1):
            print(f"  Task {idx}: {task['description']}")
            prompt = task["description"]
            
            start_time = time.time()
            generated_code = generate_code(model, prompt)
            end_time = time.time()
            response_time = end_time - start_time
            
            generated_code = clean_code(generated_code)
            success, message, execution_time = eval_function(generated_code, task["test_cases"])

            task_resul = {
                "description": task["description"],
                "generated_code": generated_code,
                "success": success,
                "message": message,
                "execution_time": execution_time,
                "response_time": response_time
            }
            model_result["task"].append(task_resul)

            estado = "✅" if success else "❌"
            print(f"    Response Time: {response_time:.2f} seconds")
            print(f"    Result: {estado} - {message}") 
            print(f"    Execution Time: {execution_time:.2f} seconds")
            print("-----------------------")
            time.sleep(1)

        result.append(model_result)
        print()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Evaluation completed. results saved in '{filename}'.")

if __name__ == "__main__":
    main()
