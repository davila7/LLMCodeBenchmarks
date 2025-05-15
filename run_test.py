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
# if openai.api_key:
#     MODELS.extend(["o4-mini", "o3", "gpt-4.1-2025-04-14", "gpt-4o"])
# if anthropic_api_key:
#     MODELS.extend(["claude-3-5-sonnet-20240620", "claude-3-7-sonnet-20250219"])
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
    Check if two code snippets are semantically equivalent and return detailed metrics.
    
    Returns:
        tuple: (is_equivalent, similarity_data)
            - is_equivalent (bool): True if codes are semantically equivalent
            - similarity_data (dict): Detailed metrics about the similarity
    """
    similarity_data = {
        "structural_similarity": 0.0,  # 0-1 score for AST structure similarity
        "behavioral_similarity": 0.0,  # 0-1 score for runtime behavior similarity
        "function_match_score": 0.0,   # 0-1 score for function signature matching
        "test_cases_passed": 0,        # Number of test cases with identical behavior
        "total_test_cases": 0,         # Total number of test cases tried
        "differences": [],             # List of notable differences
        "overall_score": 0.0           # Weighted average of all metrics
    }
    
    # Parse into AST to compare structure
    try:
        ast1 = ast.parse(code1)
        ast2 = ast.parse(code2)
    except SyntaxError as e:
        similarity_data["differences"].append(f"Syntax error: {str(e)}")
        similarity_data["overall_score"] = 0.0
        return False, similarity_data
    
    # Compare AST structures
    structural_score, ast_details = compare_ast_structures_with_score(ast1, ast2)
    similarity_data["structural_similarity"] = structural_score
    if ast_details.get("differences"):
        similarity_data["differences"].extend(ast_details["differences"])
    
    # Execute against test cases in isolated environments
    def create_test_env(code):
        env = {}
        try:
            exec(code, {}, env)
            return env
        except Exception as e:
            similarity_data["differences"].append(f"Execution error: {str(e)}")
            return None
    
    env1 = create_test_env(code1)
    env2 = create_test_env(code2)
    
    if env1 is None or env2 is None:
        similarity_data["overall_score"] = structural_score * 0.5  # Only structure counts
        return False, similarity_data
    
    # Find callable objects (likely functions)
    funcs1 = {name: obj for name, obj in env1.items() if callable(obj) and not name.startswith('__')}
    funcs2 = {name: obj for name, obj in env2.items() if callable(obj) and not name.startswith('__')}
    
    if not funcs1 or not funcs2:
        similarity_data["differences"].append("One or both code snippets don't define any functions")
        similarity_data["overall_score"] = structural_score * 0.5
        return False, similarity_data
    
    # Calculate function match score
    common_names = set(funcs1.keys()).intersection(set(funcs2.keys()))
    function_match_score = len(common_names) / max(len(funcs1), len(funcs2))
    similarity_data["function_match_score"] = function_match_score
    
    # Generate a set of test inputs
    test_inputs = [
        None, 0, 1, -1, 100, 
        "", "a", "test", 
        [], [1, 2, 3], 
        {}, {"a": 1, "b": 2},
        True, False
    ]
    
    # Find matching functions
    def find_matching_functions():
        # Try exact matches first
        exact_matches = [(name, funcs1[name], funcs2[name]) for name in common_names]
        
        # If no exact matches, try to match by position
        if not exact_matches and funcs1 and funcs2:
            exact_matches = [(None, list(funcs1.values())[0], list(funcs2.values())[0])]
            
        return exact_matches
    
    matched_functions = find_matching_functions()
    
    # Test behavioral similarity
    test_cases_passed = 0
    total_test_cases = 0
    
    for name, func1, func2 in matched_functions:
        func_name = name if name else "anonymous_function"
        
        for test_input in test_inputs:
            total_test_cases += 1
            try:
                # Try with single argument
                result1 = func1(test_input)
                try:
                    result2 = func2(test_input)
                    if result1 == result2:
                        test_cases_passed += 1
                    else:
                        similarity_data["differences"].append(
                            f"Function '{func_name}' returns different results for input {repr(test_input)}: "
                            f"{repr(result1)} vs {repr(result2)}"
                        )
                except Exception:
                    similarity_data["differences"].append(
                        f"Function '{func_name}' in second code fails for input {repr(test_input)}"
                    )
            except TypeError:
                # Try with no arguments
                try:
                    result1 = func1()
                    try:
                        result2 = func2()
                        if result1 == result2:
                            test_cases_passed += 1
                        else:
                            similarity_data["differences"].append(
                                f"Function '{func_name}' returns different results with no args: "
                                f"{repr(result1)} vs {repr(result2)}"
                            )
                    except Exception:
                        # Both failed, but differently
                        pass
                except Exception:
                    # Both failed with TypeError, consider it a pass
                    test_cases_passed += 1
            except Exception:
                # Skip this test case
                total_test_cases -= 1
    
    # Calculate behavioral similarity
    behavioral_similarity = test_cases_passed / total_test_cases if total_test_cases > 0 else 0.0
    similarity_data["behavioral_similarity"] = behavioral_similarity
    similarity_data["test_cases_passed"] = test_cases_passed
    similarity_data["total_test_cases"] = total_test_cases
    
    # Calculate overall score (weighted average)
    similarity_data["overall_score"] = (
        structural_score * 0.4 +
        behavioral_similarity * 0.5 +
        function_match_score * 0.1
    )
    
    # Determine if they are semantically equivalent
    # You can adjust the threshold as needed
    # Examples:
    # - 0.95 for strict equivalence
    # - 0.85 for relaxed equivalence
    # - 0.75 for loose 
    # - 0.65 for very 
    # - 0.55 for very loose equivalence
    is_equivalent = similarity_data["overall_score"] > 0.75  # Threshold for equivalence
    
    return is_equivalent, similarity_data

def compare_ast_structures_with_score(ast1, ast2):
    """
    Compare two AST structures and return a similarity score and details.
    
    Returns:
        tuple: (similarity_score, details)
            - similarity_score (float): 0-1 score of structural similarity
            - details (dict): Additional information about the comparison
    """
    details = {"differences": []}
    
    # Get the main function definitions from both ASTs
    funcs1 = [node for node in ast1.body if isinstance(node, ast.FunctionDef)]
    funcs2 = [node for node in ast2.body if isinstance(node, ast.FunctionDef)]
    
    # If number of functions differs significantly
    if abs(len(funcs1) - len(funcs2)) > 1:
        details["differences"].append(
            f"Different number of functions: {len(funcs1)} vs {len(funcs2)}"
        )
    
    # If no functions found, compare the entire body
    if not funcs1 and not funcs2:
        node_similarity, node_details = compare_ast_nodes_with_score(ast1.body, ast2.body)
        if node_details.get("differences"):
            details["differences"].extend(node_details["differences"])
        return node_similarity, details
    
    # Try to match functions by name
    matched_pairs = []
    unmatched1 = []
    unmatched2 = list(funcs2)
    
    for func1 in funcs1:
        matched = False
        for i, func2 in enumerate(unmatched2):
            if func1.name == func2.name:
                matched_pairs.append((func1, func2))
                unmatched2.pop(i)
                matched = True
                break
        if not matched:
            unmatched1.append(func1)
    
    # If there are unmatched functions, try to match them by position
    if unmatched1 and unmatched2 and len(unmatched1) == len(unmatched2):
        for i in range(len(unmatched1)):
            matched_pairs.append((unmatched1[i], unmatched2[i]))
        unmatched1 = []
        unmatched2 = []
    
    # Calculate function match score
    total_funcs = max(len(funcs1), len(funcs2))
    matched_funcs = len(matched_pairs)
    function_match_ratio = matched_funcs / total_funcs if total_funcs > 0 else 1.0
    
    # Record unmatched functions
    for func in unmatched1:
        details["differences"].append(f"Function '{func.name}' only in first code")
    for func in unmatched2:
        details["differences"].append(f"Function '{func.name}' only in second code")
    
    # Compare each matched pair
    similarity_scores = []
    
    for func1, func2 in matched_pairs:
        # Compare function signatures
        sig_similarity, sig_details = compare_function_signatures_with_score(func1, func2)
        if sig_details.get("differences"):
            details["differences"].extend(sig_details["differences"])
        
        # Compare function bodies
        body_similarity, body_details = compare_ast_nodes_with_score(func1.body, func2.body)
        if body_details.get("differences"):
            details["differences"].extend(body_details["differences"])
        
        # Combined similarity for this function pair
        func_similarity = (sig_similarity * 0.3) + (body_similarity * 0.7)
        similarity_scores.append(func_similarity)
    
    # Calculate overall structural similarity
    if similarity_scores:
        # Weight by function match ratio
        structure_similarity = (sum(similarity_scores) / len(similarity_scores)) * function_match_ratio
    else:
        structure_similarity = 0.0
    
    return structure_similarity, details

def compare_function_signatures_with_score(func1, func2):
    """Compare function signatures and return a similarity score"""
    details = {"differences": []}
    
    # Compare argument counts
    args1 = func1.args
    args2 = func2.args
    
    # Basic parameter count comparison
    if len(args1.args) != len(args2.args):
        details["differences"].append(
            f"Function '{func1.name}' has different parameter count: "
            f"{len(args1.args)} vs {len(args2.args)}"
        )
        param_similarity = min(len(args1.args), len(args2.args)) / max(len(args1.args), len(args2.args)) if max(len(args1.args), len(args2.args)) > 0 else 1.0
    else:
        param_similarity = 1.0
    
    # More detailed signature comparison could be added here
    
    return param_similarity, details

def compare_ast_nodes_with_score(nodes1, nodes2):
    """
    Compare two lists of AST nodes and return a similarity score.
    """
    details = {"differences": []}
    
    # If lengths differ significantly
    if abs(len(nodes1) - len(nodes2)) > 2:
        details["differences"].append(f"Different node count: {len(nodes1)} vs {len(nodes2)}")
    
    # Normalize and classify nodes
    def classify_node(node):
        if isinstance(node, ast.Assign):
            return "assignment"
        elif isinstance(node, (ast.If, ast.IfExp)):
            return "conditional"
        elif isinstance(node, (ast.For, ast.While)):
            return "loop"
        elif isinstance(node, ast.Return):
            return "return"
        elif isinstance(node, ast.Expr):
            return "expression"
        else:
            return type(node).__name__
    
    # Count node types in both bodies
    counts1 = {}
    counts2 = {}
    
    for node in nodes1:
        node_type = classify_node(node)
        counts1[node_type] = counts1.get(node_type, 0) + 1
    
    for node in nodes2:
        node_type = classify_node(node)
        counts2[node_type] = counts2.get(node_type, 0) + 1
    
    # Compare counts of different node types
    all_node_types = set(counts1.keys()) | set(counts2.keys())
    type_similarities = []
    
    for node_type in all_node_types:
        count1 = counts1.get(node_type, 0)
        count2 = counts2.get(node_type, 0)
        
        # Calculate similarity for this node type
        if max(count1, count2) > 0:
            type_similarity = min(count1, count2) / max(count1, count2)
        else:
            type_similarity = 1.0
        
        # Record significant differences
        if abs(count1 - count2) > 1:
            # Special case for assignments
            if node_type == "assignment" and abs(count1 - count2) <= 3:
                type_similarity = 0.8  # Minor penalty
            else:
                details["differences"].append(
                    f"Different number of {node_type} nodes: {count1} vs {count2}"
                )
        
        type_similarities.append(type_similarity)
    
    # Calculate overall node similarity
    if type_similarities:
        node_similarity = sum(type_similarities) / len(type_similarities)
    else:
        node_similarity = 0.0
    
    return node_similarity, details


def compare_ast_structures(ast1, ast2):
    """
    Compare two AST structures for semantic equivalence.
    Returns True if the structures are semantically equivalent, False otherwise.
    """
    # Get the main function definitions from both ASTs
    funcs1 = [node for node in ast1.body if isinstance(node, ast.FunctionDef)]
    funcs2 = [node for node in ast2.body if isinstance(node, ast.FunctionDef)]
    
    # If number of functions differs significantly, they're likely not equivalent
    if abs(len(funcs1) - len(funcs2)) > 1:
        return False
    
    # If no functions found, compare the entire body
    if not funcs1 and not funcs2:
        return compare_ast_nodes(ast1.body, ast2.body)
    
    # Try to match functions by name
    matched_pairs = []
    for func1 in funcs1:
        for func2 in funcs2:
            if func1.name == func2.name:
                matched_pairs.append((func1, func2))
                break
    
    # If no matches by name, try to match the "main" functions
    # (assuming the first/only function is the main one)
    if not matched_pairs and funcs1 and funcs2:
        matched_pairs = [(funcs1[0], funcs2[0])]
    
    # Compare each matched pair
    for func1, func2 in matched_pairs:
        # Compare function signatures
        if not compare_function_signatures(func1, func2):
            return False
        
        # Compare function bodies
        if not compare_ast_nodes(func1.body, func2.body):
            return False
    
    return True

def compare_function_signatures(func1, func2):
    """Compare function signatures for compatibility"""
    # Compare argument counts
    args1 = func1.args
    args2 = func2.args
    
    # Check if both have similar parameter structure
    # This is a simplified check - a more thorough one would look at defaults, etc.
    if len(args1.args) != len(args2.args):
        return False
    
    # Check if both have similar return structure
    # This would require type inference which is complex
    # For now, we'll skip this check
    
    return True

def compare_ast_nodes(nodes1, nodes2):
    """
    Compare two lists of AST nodes for semantic equivalence.
    This is a simplified version that checks for structural similarity.
    """
    # If lengths differ significantly, they're likely not equivalent
    if abs(len(nodes1) - len(nodes2)) > 2:  # Allow some flexibility
        return False
    
    # Normalize and classify nodes
    def classify_node(node):
        if isinstance(node, ast.Assign):
            return "assignment"
        elif isinstance(node, (ast.If, ast.IfExp)):
            return "conditional"
        elif isinstance(node, (ast.For, ast.While)):
            return "loop"
        elif isinstance(node, ast.Return):
            return "return"
        elif isinstance(node, ast.Expr):
            return "expression"
        else:
            return type(node).__name__
    
    # Count node types in both bodies
    counts1 = {}
    counts2 = {}
    
    for node in nodes1:
        node_type = classify_node(node)
        counts1[node_type] = counts1.get(node_type, 0) + 1
    
    for node in nodes2:
        node_type = classify_node(node)
        counts2[node_type] = counts2.get(node_type, 0) + 1
    
    # Compare counts of different node types
    # Allow some flexibility - functions might be implemented differently
    # but still be semantically equivalent
    for node_type in set(counts1.keys()) | set(counts2.keys()):
        count1 = counts1.get(node_type, 0)
        count2 = counts2.get(node_type, 0)
        
        # If counts differ significantly, they're likely not equivalent
        if abs(count1 - count2) > 1:  # Allow some flexibility
            # Special case: assignments might be combined or split
            if node_type == "assignment" and abs(count1 - count2) <= 3:
                continue
            return False
    
    # If we get here, the structures are similar enough
    # that they might be semantically equivalent
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
            return False, "No function found in the generated code.", 0, False, {}
        
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
                    return False, f"Failure in case #{idx}: input={input_val}, expected={expected}, got={result}", execution_time, False, {}
            except Exception as e:
                tb = traceback.format_exc()
                return False, f"Error executing case #{idx}: {e}\n{tb}", 0, False, {}
        
        # Evaluar semánticamente
        reference_solution = generate_reference_solution(test_cases)
        is_equivalent, semantic_data = are_semantically_equivalent(code, reference_solution)
        
        return True, "All test cases passed", execution_time, is_equivalent, semantic_data
    
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"Error executing code: {e}\n{tb}", 0, False, {}

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
            success, message, execution_time, semantic_equivalence, semantic_data = eval_function(generated_code, task["test_cases"])
            estado = "✅" if success else "❌"
            semantic_status = "✅" if semantic_equivalence else "❌"
            
            task_result = {
                "description": task["description"],
                "test_cases": task["test_cases"],
                "generated_code": generated_code,
                "success": success,
                "message": message,
                "execution_time": execution_time,
                "response_time": response_time,
                "semantic_equivalence": semantic_equivalence,
                "semantic_metrics": semantic_data,
                "semantic_status": semantic_status,
            }
            model_result["task"].append(task_result)

            print(f"    Response Time: {response_time:.2f} seconds")
            print(f"    Execution Time: {execution_time:.2f} seconds")
            print(f"    Result: {estado} - {message}") 
            print("Semantic Analysis:")
            print(f"    Behavioral Similarity: {semantic_data['behavioral_similarity']}")
            print(f"    Structural Similarity: {semantic_data['structural_similarity']}")
            print(f"    Function Match Score: {semantic_data['function_match_score']}")
            print(f"    Overall Score: {semantic_data['overall_score']}")
            print(f"    Test Cases Passed: {semantic_data['test_cases_passed']}")
            print(f"    Total Test Cases: {semantic_data['total_test_cases']}")
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
