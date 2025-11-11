import json
import requests

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
    payload = json.dumps({
        "model": model if model else self.default_model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    })
    try:
      response = requests.post(
          url=self.api_endpoint,
          headers=headers,
          data=payload,
      )
      response.raise_for_status()
      return response.json()
    except requests.exceptions.RequestException as e:
      print(f"Error: {e}")
      return None
    
def get_api_key():
  with open('.env', 'r') as file:
    api_key = file.read().strip()

    return api_key.split('\n')[0].split('=')[1].strip('"')

openrouter_api = "https://openrouter.ai/api/v1/chat/completions"
openrouter_key = get_api_key()
opnrtr = AiClient(openrouter_api, openrouter_key, "minimax/minimax-m2:free")

def run_prompt_chain(customer_query):
    intermediate_outputs = []
    
    # 1. Interpret the Customer’s Intent
    prompt1 = f"""
    You are an empathetic bank support assistant. Analyze the customer query below and
    provide a concise, single-paragraph summary of their core intent. Focus purely on
    understanding the problem, not on solving it yet. Preserve key details like dates,
    amounts, or specific items mentioned.

    ```
    {customer_query}
    ```
    """
    
    response = opnrtr.call_with_prompt(prompt1)
    summary = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(summary)
    
    # 2. Map the query to possible categories
    prompt2 = f"""
    Based on the summarized intent: '{summary}', identify between 1 and 3 of the most
    relevant categories from the provided list.

    The categories are:
    [Account Opening, Billing Issue, Account Access, Transaction Inquiry, Card Services, Account Statement, Loan Inquiry, General Information].
    List the categories separated by a comma.
    """
    
    response = opnrtr.call_with_prompt(prompt2)
    categories = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(categories)
    
    # 3. Choose the most appropriate category
    prompt3 = f"""
    From the list of possible categories: '{categories}', and considering the original
    summarized intent: '{summary}', select the single most appropriate category that
    the bank needs to address. Your response must be only the category name, with no
    extra text or punctuation.
    """

    response = opnrtr.call_with_prompt(prompt3)
    appropriate_category = response["choices"][0]["message"]["content"]

    intermediate_outputs.append(appropriate_category)
    
    # 4. Extract additional details
    prompt4 = f"""
    The customer query has been classified as '{appropriate_category}'.
    Review the summarized intent: '{summary}'. Based on this category, what critical
    piece(s) of information are still missing from the customer's query that a bank
    representative would need to solve the issue? (e.g., specific transaction date,
    amount, account number, card type, exact error message). If no further details are
    immediately needed, respond with 'None needed'.
    """

    response = opnrtr.call_with_prompt(prompt4)
    missing_information = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(missing_information)
    
    # 5. Generate a short response
    prompt5 = f"""
    You are a bank support assistant. The customer’s intent is: '{summary}'.
    The final category is: '{appropriate_category}'. The missing information
    required is: '{missing_information}'.

    Draft a short, empathetic, and professional response to the customer.
    Your response should first acknowledge their problem and then, depending
    on the information from Stage 4, either state that you are now preparing
    to help or politely request the missing details before proceeding. Keep the 
    response under 50 words.
    """

    response = opnrtr.call_with_prompt(prompt5)
    short_response = response["choices"][0]["message"]["content"]
    intermediate_outputs.append(short_response)
    
    return intermediate_outputs


if __name__ == "__main__":
    customer_query = input("Enter your query: ").split()

    results = run_prompt_chain(customer_query)
    print(results)