import openai
import json
import time
import sys
import traceback
import re
import os
import ast
import unittest
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from mistralai import Mistral

# Load environment variables from .env file
load_dotenv()

# Load API keys from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')
anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
mistral_api_key = os.getenv('MISTRAL_API_KEY')
cohere_api_key = os.getenv('COHERE_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=anthropic_api_key)

# Initialize Mistral client
mistral_client = Mistral(api_key=mistral_api_key)

# separa los modelos si es que existe la api key
MODELS = []
if openai.api_key:
    MODELS.extend(["o4-mini", "o3", "gpt-4.1-2025-04-14", "gpt-4o"])
if anthropic_api_key:
    MODELS.extend(["claude-3-5-sonnet-20240620", "claude-3-7-sonnet-20250219"])
if mistral_api_key:
    MODELS.extend(["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "codestral-latest"])


# Load tasks
def load_tasks(filename, take_first=False):
    with open(filename, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
        if take_first:
            return [tasks[0]] if tasks else []
        return tasks

def generate_code(model, prompt):
    try:
        full_prompt = f"{prompt}\n\nPlease provide ONLY the Python code without additional explanations or Markdown code blocks"
        message = [{"role": "user", "content": full_prompt}]
        
        # add system message just for the models that need it
        if model in ["gpt-4o", "gpt-4o", "claude-3-5-sonnet-20240620", "claude-3-7-sonnet-20250219", "mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "codestral-latest"]:
            message.insert(0, {"role": "system", "content": "You are a helpful assistant for writing code."})
        
        if model.startswith("claude"):
            response = anthropic_client.messages.create(
                max_tokens=1024,
                messages=message,
                model=model
            )
            code = response.content[0].text.strip()
        elif model.startswith("codestral") or model.startswith("mistral"):
            response = mistral_client.chat.complete(model=model, messages=message)
            if response is not None:
                code = response.choices[0].message.content
            else:
                code = ""
        else:
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
    """
    Cleans the provided code by removing code block markers and extracting the function definition.

    Args:
        code (str): The input code as a string.

    Returns:
        str: The cleaned code string, starting from the function definition and stripped of leading/trailing whitespace.
    """
    # Remove code block markers
    code = re.sub(r"```python", "", code)
    code = re.sub(r"```", "", code)

    # Find the start of the function definition
    match = re.search(r"def\s+\w+\s*\(.*\):", code)
    if match:
        start = match.start()
        code = code[start:]

    return code.strip()

def are_semantically_equivalent(code1, code2):
    """
    Check if two code snippets are semantically equivalent by:
    1. Parsing both into AST
    2. Running both against a battery of tests
    3. Comparing their outputs for various inputs
    """
    # Parse into AST to compare structure
    try:
        ast1 = ast.parse(code1)
        ast2 = ast.parse(code2)
    except SyntaxError:
        return False
    
    # Execute against test cases in isolated environments
    def create_test_env(code):
        env = {}
        try:
            exec(code, {}, env)
            return env
        except Exception:
            return None
    
    env1 = create_test_env(code1)
    env2 = create_test_env(code2)
    
    if env1 is None or env2 is None:
        return False
    
    # Find callable objects (likely functions)
    funcs1 = {name: obj for name, obj in env1.items() if callable(obj) and not name.startswith('__')}
    funcs2 = {name: obj for name, obj in env2.items() if callable(obj) and not name.startswith('__')}
    
    if not funcs1 or not funcs2:
        return False
    
    # Generate a set of test inputs
    # For simplicity, assuming there's one main function with similar name
    # In real implementation, you'd need more sophisticated matching
    def find_matching_functions():
        # Try exact matches first
        exact_matches = set(funcs1.keys()).intersection(funcs2.keys())
        if exact_matches:
            return [(name, funcs1[name], funcs2[name]) for name in exact_matches]
        
        # Otherwise, use heuristics like:
        # 1. Main function is likely the last defined
        # 2. Or the one with the most complex signature
        return [(None, list(funcs1.values())[0], list(funcs2.values())[0])]
    
    matched_functions = find_matching_functions()
    
    # Test the functions with various inputs
    test_inputs = [
        None, 0, 1, -1, 100, 
        "", "a", "test", 
        [], [1, 2, 3], 
        {}, {"a": 1, "b": 2},
        True, False
    ]
    
    # For each matched function pair, test with various inputs
    for _, func1, func2 in matched_functions:
        try:
            for test_input in test_inputs:
                try:
                    # Try with single argument
                    result1 = func1(test_input)
                    result2 = func2(test_input)
                    if result1 != result2:
                        return False
                except TypeError:
                    # Try with no arguments
                    try:
                        result1 = func1()
                        result2 = func2()
                        if result1 != result2:
                            return False
                    except:
                        # Both failed similarly, consider it a pass for this input
                        pass
        except Exception:
            # If we encounter exceptions, the functions likely have different behaviors
            return False
    
    # If we got here, the functions seem equivalent
    return True

def generate_reference_solution(test_cases):
    """
    Generate a reference solution based on the test cases.
    This is a simple implementation that creates a function that handles the test cases.
    In a real scenario, you would have more sophisticated reference solutions.
    """
    # This is a very basic implementation - in practice, you would have better reference solutions
    if not test_cases:
        return "def solution(): pass"
    
    # Try to infer the function signature from the first test case
    first_case = test_cases[0]
    input_val = first_case["input"]
    
    if isinstance(input_val, (list, tuple)):
        # Multiple arguments
        args = ", ".join([f"arg{i}" for i in range(len(input_val))])
        func_def = f"def solution({args}):\n"
        
        # Create a simple mapping function based on test cases
        cases_str = []
        for case in test_cases:
            inputs = case["input"]
            expected = case["expected"]
            conditions = " and ".join([f"arg{i} == {repr(val)}" for i, val in enumerate(inputs)])
            cases_str.append(f"    if {conditions}:\n        return {repr(expected)}")
        
        func_body = "\n".join(cases_str)
        func_body += "\n    return None  # Default case"
        
    elif isinstance(input_val, dict):
        # Keyword arguments
        args = ", ".join([f"{k}=None" for k in input_val.keys()])
        func_def = f"def solution({args}):\n"
        
        # Create a simple mapping function based on test cases
        cases_str = []
        for case in test_cases:
            inputs = case["input"]
            expected = case["expected"]
            conditions = " and ".join([f"{k} == {repr(v)}" for k, v in inputs.items()])
            cases_str.append(f"    if {conditions}:\n        return {repr(expected)}")
        
        func_body = "\n".join(cases_str)
        func_body += "\n    return None  # Default case"
        
    else:
        # Single argument
        func_def = "def solution(x):\n"
        
        # Create a simple mapping function based on test cases
        cases_str = []
        for case in test_cases:
            input_val = case["input"]
            expected = case["expected"]
            cases_str.append(f"    if x == {repr(input_val)}:\n        return {repr(expected)}")
        
        func_body = "\n".join(cases_str)
        func_body += "\n    return None  # Default case"
    
    return func_def + func_body

def eval_function(code, test_cases):
    global_vars = {}
    try:
        exec(code, global_vars)
        func = None
        for name, obj in global_vars.items():
            if callable(obj):
                func = obj
                break
        if func is None:
            return False, "No function found in the generated code.", 0, False
        
        execution_time = 0
        for idx, caso in enumerate(test_cases, 1):
            input_val = caso["input"]
            expected = caso["expected"]
            try:
                start_time = time.time()
                if isinstance(input_val, (list, tuple)):
                    result = func(*input_val)
                elif isinstance(input_val, dict):
                    result = func(**input_val)
                else:
                    result = func(input_val)
                end_time = time.time()
                execution_time = end_time - start_time
                if result != expected:
                    return False, f"Failure in case #{idx}: input={input_val}, expected={expected}, got={result}", execution_time, False
            except Exception as e:
                tb = traceback.format_exc()
                return False, f"Error executing case #{idx}: {e}\n{tb}", 0, False
        
        # Evaluar semánticamente
        reference_solution = generate_reference_solution(test_cases)
        semantic_equivalence = are_semantically_equivalent(code, reference_solution)
        
        return True, "All test cases passed", execution_time, semantic_equivalence
    
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error executing code: {e}\n{tb}", 0, False

def main():
    take_first = '--take-first' in sys.argv
    TASKS = load_tasks('tasks.json', take_first)
    result = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_eval_{timestamp}.json"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    filepath = os.path.join(results_dir, filename)

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
            success, message, execution_time, semantic_equivalence = eval_function(generated_code, task["test_cases"])

            task_result = {
                "description": task["description"],
                "generated_code": generated_code,
                "success": success,
                "message": message,
                "execution_time": execution_time,
                "response_time": response_time,
                "semantic_equivalence": semantic_equivalence
            }
            model_result["task"].append(task_result)

            estado = "✅" if success else "❌"
            semantic_status = "✅" if semantic_equivalence else "❌"
            print(f"    Response Time: {response_time:.2f} seconds")
            print(f"    Result: {estado} - {message}") 
            print(f"    Execution Time: {execution_time:.2f} seconds")
            print(f"    Semantic Equivalence: {semantic_status}")
            print("-----------------------")
            time.sleep(1)

        result.append(model_result)
        print()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Evaluation completed. results saved in '{filepath}'.")

if __name__ == "__main__":
    main()
