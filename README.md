# Financial Assistant Application

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

A comprehensive, AI-powered financial analysis application designed to help users understand their credit profile, analyze loan affordability, plan their financial future, and receive personalized recommendations.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
  - [Financial Logic](#financial-logic)
  - [AI Integration](#ai-integration)
  - [Financial Algorithms and Formulas](#financial-algorithms-and-formulas)
- [Libraries and Dependencies](#libraries-and-dependencies)
- [Installation and Setup](#installation-and-setup)
- [Usage Guide](#usage-guide)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Financial Assistant Application is a state-of-the-art tool that combines financial analytics with artificial intelligence to provide users with personalized insights into their financial health. Designed with both simplicity and power in mind, it offers complex financial analysis through an intuitive interface.

The application serves as a comprehensive financial companion, capable of analyzing credit reports, calculating loan affordability, recommending suitable credit cards, and offering tailored financial advice through an AI-powered assistant.

## Features

- **Interactive Dashboard**: Visual summary of key financial metrics and indicators
- **Credit Score Analysis**: Detailed breakdown of factors affecting credit scores with improvement recommendations
- **EMI Affordability Calculator**: Advanced calculator with budget impact visualization
- **Loan Planning Tools**: Future loan scenario modeling with amortization schedules
- **Credit Card Recommendation Engine**: Personalized card suggestions based on spending patterns and preferences
- **AI Financial Advisor**: Natural language interface for personalized financial guidance
- **Debt Management Tools**: Strategies for optimal debt reduction and interest savings
- **Visual Data Representation**: Interactive charts and graphs for financial data visualization
- **Sample Data Integration**: Option to explore functionality with pre-loaded sample financial profiles

## Project Structure

The application has a simple, streamlined structure:

```
financial-assistant/
│
├── app.py                  # Main Streamlit application with all functionality
├── requirements.txt        # Dependencies list
└── sample_credit_reports.json  # Sample data for testing
```

All functionality is contained within the main `app.py` file, making it easy to understand and modify. The application uses a monolithic design where all components (UI, data processing, analysis, and AI integration) are defined in a single file for simplicity.

## Technical Details

### Financial Logic

The application implements several financial analysis modules directly in the main application file:

1. **Credit Score Analysis**
   - Analyzes factors affecting the credit score
   - Uses payment history to evaluate creditworthiness
   - Examines credit utilization ratios from credit card data
   - Considers the impact of recent credit inquiries

2. **EMI Affordability Assessment**
   - Calculates the debt-to-income ratio
   - Applies the 50-30-20 rule for budget allocation
   - Determines safe EMI amounts based on current debt obligations
   - Simulates various loan scenarios using the EMI calculator

3. **Credit Card Recommendation System**
   - Filters credit cards based on the user's credit score and income
   - Matches cards to user preferences (travel, shopping, fuel, etc.)
   - Ranks cards based on suitability for the user's profile
   - Provides detailed benefits analysis for each recommended card

### AI Integration

The application leverages OpenAI's GPT models to provide contextual financial advice:

- System prompts are crafted to simulate a financial advisor's expertise
- User financial data is processed and included in queries
- Response formatting ensures consistency and readability
- Error handling mechanisms ensure graceful fallbacks

Implementation example:
```python
def get_chatgpt_response(prompt):
    """Get response from ChatGPT API"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable financial advisor who specializes..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in API call: {str(e)}")
        return "I apologize, but I'm unable to provide an analysis at the moment. Please try again later."
```

### Financial Algorithms and Formulas

The application utilizes several financial formulas for its calculations:

#### 1. EMI (Equated Monthly Installment) Calculation

```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
```

Where:
- P = Principal loan amount
- r = Monthly interest rate (Annual rate ÷ 12 ÷ 100)
- n = Loan tenure in months

Implementation:
```python
def calculate_emi(principal, annual_interest_rate, tenure_years):
    """Calculate EMI for a loan"""
    monthly_interest_rate = annual_interest_rate / (12 * 100)
    tenure_months = tenure_years * 12
    emi = principal * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure_months) / (((1 + monthly_interest_rate) ** tenure_months) - 1)
    return emi
```

#### 2. Debt-to-Income Ratio (DTI)

```
DTI = (Total Monthly Debt Payments ÷ Monthly Gross Income) × 100
```

Implementation:
```python
def calculate_dti_ratio(total_emi, card_minimum_dues, income):
    """Calculate Debt-to-Income ratio"""
    monthly_debt = total_emi + card_minimum_dues
    dti_ratio = (monthly_debt / income) * 100 if income > 0 else 0
    return dti_ratio
```

#### 3. Credit Utilization Ratio

```
Credit Utilization Ratio = (Outstanding Balance ÷ Credit Limit) × 100
```

Implementation:
```python
def calculate_utilization(outstanding, limit):
    """Calculate credit utilization percentage"""
    return (outstanding / limit) * 100 if limit > 0 else 0
```

#### 4. Budget Allocation (50-30-20 Rule)

```
Essentials (Needs) = Monthly Income × 0.5
Wants = Monthly Income × 0.3
Savings/Debt Repayment = Monthly Income × 0.2
```

Implementation:
```python
def apply_budget_rule(income):
    """Apply 50-30-20 budget rule"""
    return {
        "essentials": income * 0.5,
        "wants": income * 0.3,
        "savings": income * 0.2
    }
```

## Libraries and Dependencies

The application uses the following Python libraries:

1. **Streamlit** (`streamlit`): For the web interface and UI components
2. **Pandas** (`pandas`): For data manipulation and analysis
3. **NumPy** (`numpy`): For numerical operations
4. **JSON** (`json`): For handling JSON data formats
5. **Plotly** (`plotly.express`, `plotly.graph_objects`): For interactive visualizations
6. **OpenAI** (`openai`): For AI-powered financial advice
7. **Datetime** (`datetime`): For date handling
8. **OS** (`os`): For environment variable management
9. **Dotenv** (`python-dotenv`): For loading environment variables
10. **Re** (`re`): For regular expression operations

## Installation and Setup

### Prerequisite Software

Before installing the application, ensure you have the following:

1. **Python 3.8 or higher**
   - Check your version: `python --version` or `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Pip (Python Package Installer)**
   - Usually included with Python installation
   - Verify with: `pip --version`

### Step-by-Step Installation

1. **Clone or Download the Repository**

   ```bash
   git clone https://github.com/nowitsidb/financial-assistant.git
   cd financial-assistant
   ```

   Alternatively, download and extract the ZIP file from the repository.

2. **Create and Activate Virtual Environment**

   **For Windows:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   venv\Scripts\activate
   ```

   **For macOS/Linux:**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   source venv/bin/activate
   ```

3. **Install Dependencies**

   Create a requirements.txt file with the following content:
   ```
   streamlit==1.20.0
   pandas==1.5.0
   numpy==1.22.0
   plotly==5.10.0
   openai==1.3.0
   python-dotenv==1.0.0
   ```

   Then install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the project root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   To obtain an OpenAI API key:
   1. Sign up at https://platform.openai.com/
   2. Navigate to API keys section
   3. Create a new secret key
   4. Copy the key (it will only be shown once)

5. **Run the Application**

   ```bash
   streamlit run app.py
   ```

   After running this command, the application should start and open in your default web browser at http://localhost:8501 (or a similar local URL as indicated in the terminal).

### Troubleshooting Common Issues

1. **OpenAI API Key Issues**
   - Error: "OpenAIError: The api_key client option must be set"
   - Solution: Ensure your .env file is in the correct location and contains the valid API key

2. **Module Not Found Errors**
   - Error: "ModuleNotFoundError: No module named 'X'"
   - Solution: Install the missing package using `pip install X`

## Usage Guide

### Preparing Your Data

The application accepts credit report data in JSON format with the following structure:

```json
{
  "credit_score": 750,
  "income": 150000,
  "loans": [
    {
      "type": "Home Loan",
      "lender": "HDFC Bank",
      "amount": 5000000,
      "current_balance": 3500000,
      "emi": 40000,
      "interest_rate": 7.5,
      "tenure": 240,
      "remaining_tenure": 180
    }
  ],
  "credit_cards": [
    {
      "issuer": "ICICI Bank",
      "limit": 300000,
      "outstanding": 50000,
      "minimum_due": 2500
    }
  ],
  "payment_history": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "inquiries": 2
}
```

### Navigating the Interface

The application interface is divided into several sections:

1. **Sidebar Navigation**
   - Main menu for section navigation
   - Sample data loading option
   - Quick help resources

2. **Credit Score Analysis**
   - Visual credit score gauge
   - Factor-by-factor breakdown
   - Improvement recommendations

3. **EMI Affordability**
   - Current debt obligations summary
   - EMI calculator with interactive sliders
   - Visual income allocation analysis

4. **Credit Card Recommendations**
   - Preference selection
   - Card comparison table
   - Detailed benefits analysis

5. **Financial Advisor**
   - Chat interface for financial questions
   - Common financial queries shortcut buttons
   - Personalized advice based on profile

### Interpreting Results

1. **Credit Score Interpretation**
   - 750+ = Excellent
   - 700-749 = Good
   - 650-699 = Fair
   - 600-649 = Poor
   - Below 600 = Very Poor

2. **Debt-to-Income Ratio Guidelines**
   - Below 30% = Excellent financial health
   - 30-40% = Good standing
   - 40-50% = Caution needed
   - Above 50% = Financial stress risk

## Contributing

Contributions to improve the application are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request
