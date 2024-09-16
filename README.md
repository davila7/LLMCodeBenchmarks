# LLM Code Benchmarks

This script evaluates generative language models using predefined tasks and test cases. It utilizes the OpenAI and Anthropic APIs to generate Python code from task descriptions and then evaluates the accuracy of the generated code.

## Requirements

- Python 3.7+
- Packages: `openai`, `anthropic`, `streamlit`, `python-dotenv`

## Installation

1. Clone the repository.
2. Install the required packages:
    ```bash
    pip install openai anthropic python-dotenv
    ```
3. Create a `.env` file in the project's root directory with your API keys:
    ```
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    ```

## Usage

1. Define the tasks in a `tasks.json` file in the following format:
    ```json
    [
        {
            "description": "Task description",
            "test_cases": [
                {
                    "input": "input",
                    "expected": "expected output"
                }
            ]
        }
    ]
    ```
2. Run the script:
    ```bash
    python run_test.py [--take-first]
    ```
    - `--take-first`: Optional. If included, only the first task from the `tasks.json` file will be taken.

## Results

The evaluation results are saved in a JSON file in the `results` directory with a name based on the date and time of execution.

Run: `streamlit run results.py` to visualize the results dashbord.


## Example

```bash
python run_test.py
```

License
This project is licensed under the MIT License.
