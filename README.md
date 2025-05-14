# LLM Code Benchmarks

This script evaluates generative language models using predefined tasks and test cases. It utilizes the OpenAI and Anthropic APIs to generate Python code from task descriptions and then evaluates the accuracy of the generated code.

## Run the test
Run the test and see how the models perform on the given tasks.
![Screenshot 2025-05-14 at 13 47 48](https://github.com/user-attachments/assets/b3c5aa57-1c88-4505-9cc9-64e37556a4ab)

# Result panel
Run the streamlit app to see the results of the models on the given tasks.

<img width="1328" alt="Screenshot 2025-05-14 at 13 57 03" src="https://github.com/user-attachments/assets/a3b1cf46-d52d-4f3d-90ab-a246dd30e46a" />

<img width="1026" alt="Screenshot 2025-05-14 at 13 50 21" src="https://github.com/user-attachments/assets/a797bc75-2a8b-473f-9f14-8c189761657b" />

<img width="1026" alt="Screenshot 2025-05-14 at 13 55 57" src="https://github.com/user-attachments/assets/9caf64e7-3eb1-4538-a37b-ee9b3baac81e" />

## Requirements

- Python 3.7+
- Packages: `openai`, `anthropic`, `mistralai`, `streamlit`, `python-dotenv`

## Installation

1. Clone the repository.
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
3. Create a `.env` file in the project's root directory with your API keys:
    ```
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    MISTRAL_API_KEY=your_mistral_key
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


License
This project is licensed under the MIT License.
