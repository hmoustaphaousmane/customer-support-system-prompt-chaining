# customer-support-system-prompt-chaining

A multi-stage prompt chaining system for analyzing and routing customer support queries using AI. The system interprets customer intent, categorizes requests, identifies missing information, and generates appropriate responses.

## Features

- **Intent Analysis**: Understands the core customer problem
- **Smart Categorization**: Maps queries to relevant support categories
- **Information Extraction**: Identifies missing details needed to resolve issues
- **Automated Response**: Generates empathetic, professional customer responses
- **Multi-Model Support**: Works with various free LLM models via OpenRouter

## Prerequisites

- Python 3.12 or higher
- OpenRouter API key (free tier available)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/hmoustaphaousmane/customer-support-system-prompt-chaining.git
   cd customer-support-system-prompt-chaining
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Required packages:
   - `requests==2.32.5` - HTTP library for API calls
   - `python-dotenv==1.2.1` - Environment variable management

4. **Set up your API key**

   a. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   b. Get your OpenRouter API key:
   - Visit [OpenRouter](https://openrouter.ai/)
   - Sign up for a free account
   - Generate an API key from your dashboard

   c. Edit `.env` and add your key:

   ```bash
   OPEN_ROUTER_KEY=your_api_key_here
   ```

## Usage

### Interactive Mode

Run the script without arguments to enter interactive mode:

```bash
python prompt-chain.py
```

Then enter your customer query when prompted.

### Command Line Mode

Pass the customer query directly as an argument:

```bash
python prompt-chain.py "I was charged twice for my Netflix subscription last month"
```

### Example Queries

```bash
# Billing issue
python prompt-chain.py "Why was I charged $50 on March 15th? I don't recognize this transaction"

# Account access
python prompt-chain.py "I can't log into my account. It says my password is incorrect"

# Card services
python prompt-chain.py "My credit card was declined at the store today"

# Transaction inquiry
python prompt-chain.py "I need a copy of my transaction history for tax purposes"
```

## How It Works

The system processes queries through 5 stages:

1. **Interpret the customer’s intent** — Understand what the customer is asking or reporting.
2. **Map the query to possible categories** — Suggest one or more categories that might apply.
3. **Choose the most appropriate category** — Select the best matching category.
4. **Extract additional details** — Identify any extra information needed to address the request (e.g., transaction date, amount, card type, etc.).
5. **Generate a short response** — Produce a suitable reply to the customer based on the chosen category.

### Supported Categories

- Account Opening
- Billing Issue
- Account Access
- Transaction Inquiry
- Card Services
- Account Statement
- Loan Inquiry
- General Information

## Configuration

### Using Different Models

The script tries multiple free models in sequence. You can modify the `model_options` list in `main.py`:

```python
model_options = [
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free"
]
```

### Adjusting Temperature

Modify the temperature parameter in the `AiClient` class to control response creativity:

```python
payload = {
    "temperature": 0.3,  # Lower = more consistent, Higher = more creative
}
```

## Troubleshooting

### API Connection Issues

If you see connection errors:

- Verify your API key is correct in `.env`
- Check your internet connection
- Ensure OpenRouter service is operational

### Model Availability

If a model fails to respond:

- The script automatically tries alternative models
- Check OpenRouter documentation for current free model availability
- Consider using a paid model for better reliability

### Import Errors

If you see module not found errors:

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```
