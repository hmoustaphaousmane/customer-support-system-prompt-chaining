import requests
import sys
from dotenv import load_dotenv
import os

load_dotenv()


class AiClient:
    def __init__(self, api_endpoint, api_key, default_model):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.default_model = default_model

    def call_with_prompt(self, prompt, system_prompt="", model=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model if model else self.default_model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }

        if system_prompt:
            payload["messages"].insert(
                0, {"role": "system", "content": system_prompt})

        try:
            print(f"Making API call to: {self.api_endpoint}")
            print(f"Using model: {payload['model']}")

            response = requests.post(
                url=self.api_endpoint,
                headers=headers,
                json=payload,
            )

            print(f"Response status code: {response.status_code}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response content: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None


def get_api_key():
    try:
        with open('.env', 'r') as file:
            api_key = file.read().strip()
            return api_key.split('\n')[0].split('=')[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        print("Error: .env file not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading API key: {e}")
        sys.exit(1)


def run_prompt_chain(customer_query):
    # Initialize API client
    openrouter_api = "https://openrouter.ai/api/v1/chat/completions"
    # openrouter_key = get_api_key()
    openrouter_key = os.getenv("OPEN_ROUTER_KEY")

    # Try different model names - OpenRouter format might be different
    # Common free models on OpenRouter:
    model_options = [
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-9b-it:free",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]

    for model in model_options:
        opnrtr = AiClient(openrouter_api, openrouter_key, model)
        response = opnrtr.call_with_prompt("test")
        if response:
            break


    intermediate_outputs = []

    # 1. Interpret the Customer's Intent
    print("\nStage 1: Interpreting customer intent...")
    prompt1 = f"""
    You are an empathetic bank support assistant. Analyze the customer query
    below and provide a concise, single-paragraph summary of their core intent.
    Focus purely on understanding the problem, not on solving it yet. Preserve
    key details like dates, amounts, or specific items mentioned.

    Customer Query:
    ```
    {customer_query}
    ```
    """

    response = opnrtr.call_with_prompt(prompt1)
    if response is None:
        print("Error: Failed to get response from API in Stage 1")
        return None

    summary = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(summary)
    # print(f"Summary: {summary}")

    # 2. Map the query to possible categories
    print("\nStage 2: Mapping to categories...")
    prompt2 = f"""
    Based on the summarized intent: '{summary}', identify between 1 and 3 of the
    most relevant categories from the provided list.
    The categories are: Account Opening, Billing Issue, Account Access,
    Transaction Inquiry, Card Services, Account Statement, Loan Inquiry, General
    Information.

    List the categories separated by a comma.
    Example Output Format: Category A, Category B
    """

    response = opnrtr.call_with_prompt(prompt2)
    if response is None:
        print("Error: Failed to get response from API in Stage 2")
        return None

    categories = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(categories)
    # print(f"Categories: {categories}")

    # 3. Choose the most appropriate category
    print("\nStage 3: Selecting most appropriate category...")
    prompt3 = f"""
    From the list of possible categories: '{categories}', and considering the
    original summarized intent: '{summary}', select the single most appropriate
    category that the bank needs to address. Your response must be only the
    category name, with no extra text or punctuation.
    Allowed Categories: Account Opening, Billing Issue, Account Access,
    Transaction Inquiry, Card Services, Account Statement, Loan Inquiry,
    General Information
    """

    response = opnrtr.call_with_prompt(prompt3)
    if response is None:
        print("Error: Failed to get response from API in Stage 3")
        return None

    appropriate_category = response["choices"][0]["message"]["content"].strip()
    intermediate_outputs.append(appropriate_category)
    # print(f"Selected Category: {appropriate_category}")

    # 4. Extract additional details
    print("\nStage 4: Identifying missing information...")
    prompt4 = f"""
    The customer query has been classified as '{appropriate_category}'.
    Review the summarized intent: '{summary}'. Based on this category, what
    critical piece(s) of information are still missing from the customer's query
    that a bank representative would need to solve the issue? (e.g., specific
    transaction date, amount, account number, card type, exact error message).
    If no further details are immediately needed, respond with 'None needed'.

    Example Output Format (list items separated by comma):
    [Transaction Date, Amount, Last 4 digits of card]
    """

    response = opnrtr.call_with_prompt(prompt4)
    if response is None:
        print("Error: Failed to get response from API in Stage 4")
        return None

    missing_information = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(missing_information)
    # print(f"Missing Information: {missing_information}")

    # 5. Generate a short response
    print("\nStage 5: Generating customer response...")
    prompt5 = f"""
    You are a bank support assistant. The customer's intent is: '{summary}'.
    The final category is: '{appropriate_category}'. The missing information
    required is: '{missing_information}'.

    Draft a short, empathetic, and professional response to the customer. Your
    response should first acknowledge their problem and then, depending on the
    information from Stage 4, either state that you are now preparing to help
    or politely request the missing details before proceeding. Keep the response
    under 50 words.
    """

    response = opnrtr.call_with_prompt(prompt5)
    if response is None:
        print("Error: Failed to get response from API in Stage 5")
        return None

    short_response = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(short_response)
    # print(f"Customer Response: {short_response}")

    return intermediate_outputs


if __name__ == "__main__":
    if len(sys.argv) > 1:
        customer_query = ' '.join(sys.argv[1:])
    else:
        customer_query = input("Enter your query: ")

    results = run_prompt_chain(customer_query)

    if results:
        print(f"\n{'='*79}")
        print("FINAL RESULTS:")
        print('='*79)
        for i, result in enumerate(results, 1):
            print(f"\nStage {i}: {result}")
    else:
        print("\nFailed to complete prompt chain due to API errors.")
