# Code Evaluation with OpenAI Models

This project evaluates the performance of various OpenAI models on predefined coding tasks. The script generates code using different models, executes the code, and checks the results against test cases.

## Prerequisites

- Python 3.6+
- OpenAI Python client library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/code-evaluation.git
    cd code-evaluation
    ```

2. Install the required packages:
    ```sh
    pip install openai
    ```

3. Set your OpenAI API key in `main.py`:
    ```python
    openai.api_key = 'your_api_key_here'
    ```

## Usage

Run the script:
```sh
python main.py
```

## The script will:

- Generate code for each task using different models.
- Clean the generated code.
- Evaluate the code against predefined test cases.
- Save the results in a JSON file with a timestamp.

## Tasks
From file tasks.json


Model name
- Task description
- Generated code
- Success status
- Message
- Execution time
- Response time

## Example
```Json
Insert code

{
    "model": "gpt-4",
    "task": [
        {
            "description": "Write a Python function that reverses a string.",
            "generated_code": "def reverse_string(s):\n    return s[::-1]",
            "success": true,
            "message": "All test cases passed",
            "execution_time": 0.0001,
            "response_time": 1.23
        },
        ...
    ]
}
```

## License
This project is licensed under the MIT License.