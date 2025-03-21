import streamlit as st
import re
import pandas as pd
import numpy as np
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Financial Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load API key for OpenAI
load_dotenv()  # Load environment variables from .env file

# Explicitly set API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client with API key
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    client = None

# Functions for JSON processing and information extraction
def extract_credit_info(credit_data):
    """Extract credit information from the JSON data"""
    # Simply return the data as it's already in the right format
    return credit_data

# Functions for ChatGPT integration
def get_chatgpt_response(prompt):
    """Get response from ChatGPT API"""
    if client is None:
        return "OpenAI client is not available. Please check your API key configuration."
        
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable financial advisor who specializes in credit analysis and personal finance for Indian customers. You provide detailed, data-driven advice with calculations and reasoning. Format your responses in bullet points with clear headers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        st.error(f"Error in API call: {error_msg}")
        
        # Handle common API errors
        if "API key" in error_msg:
            return "Unable to connect to OpenAI API. Please check your API key configuration."
        elif "rate limit" in error_msg.lower():
            return "OpenAI API rate limit exceeded. Please try again later."
        else:
            return "I apologize, but I'm unable to provide an analysis at the moment. Please try again later."

def analyze_credit_score(credit_info):
    """Analyze credit score and provide recommendations"""
    # Create a safe copy of credit_info with default values for None
    safe_info = {
        'credit_score': credit_info.get('credit_score', 700),
        'income': credit_info.get('income', 50000),
        'loans': credit_info.get('loans', []),
        'credit_cards': credit_info.get('credit_cards', []),
        'payment_history': credit_info.get('payment_history', [0] * 12),
        'inquiries': credit_info.get('inquiries', 0)
    }
    
    # Ensure no None values
    for key in safe_info:
        if safe_info[key] is None:
            if key in ['credit_score']:
                safe_info[key] = 700
            elif key in ['income']:
                safe_info[key] = 50000
            elif key in ['loans', 'credit_cards', 'payment_history']:
                safe_info[key] = []
            elif key in ['inquiries']:
                safe_info[key] = 0
    
    prompt = f"""
    As a financial advisor, analyze this credit profile and explain why the credit score is at its current level, what benefits it provides, and what financial products/services the person might qualify for:
    
    Credit Score: {safe_info['credit_score']}
    Monthly Income: ₹{safe_info['income']}
    Number of Active Loans: {len(safe_info['loans'])}
    Active Credit Cards: {len(safe_info['credit_cards'])}
    Payment History (0=on time, 1=30 days late, 2=60 days late): {safe_info['payment_history']}
    Recent Credit Inquiries (last 6 months): {safe_info['inquiries']}
    
    Please structure your response with clear headings and bullet points. Include:
    1. Why their score is what it is (factors that might be helping or hurting)
    2. What this credit score qualifies them for in the Indian market
    3. How they could improve their score if needed
    4. Make your explanations very detailed, with clear reasoning
    """
    return get_chatgpt_response(prompt)

def analyze_emi_affordability(credit_info):
    """Analyze EMI affordability and provide recommendations"""
    # Create safe copies with default values
    loans = credit_info.get('loans', [])
    credit_cards = credit_info.get('credit_cards', [])
    income = credit_info.get('income', 50000)
    
    if income is None:
        income = 50000
    
    total_emi = sum(loan.get('emi', 0) for loan in loans)
    card_minimum_dues = sum(card.get('minimum_due', 0) for card in credit_cards)
    monthly_debt = total_emi + card_minimum_dues
    debt_to_income_ratio = (monthly_debt / income) * 100 if income > 0 else 0
    
    # Make safe copies for the JSON
    safe_loans = []
    for loan in loans:
        if loan is None:
            continue
        safe_loan = {
            "type": loan.get("type", "Loan"),
            "lender": loan.get("lender", "Unknown"),
            "amount": loan.get("amount", 0),
            "current_balance": loan.get("current_balance", 0),
            "emi": loan.get("emi", 0),
            "interest_rate": loan.get("interest_rate", 0),
            "tenure": loan.get("tenure", 0),
            "remaining_tenure": loan.get("remaining_tenure", 0)
        }
        safe_loans.append(safe_loan)
    
    safe_cards = []
    for card in credit_cards:
        if card is None:
            continue
        safe_card = {
            "issuer": card.get("issuer", "Unknown"),
            "limit": card.get("limit", 0),
            "outstanding": card.get("outstanding", 0),
            "minimum_due": card.get("minimum_due", 0)
        }
        safe_cards.append(safe_card)
    
    prompt = f"""
    As a financial advisor, analyze this person's EMI affordability and provide detailed advice:
    
    Monthly Income: ₹{income:,}
    Current Monthly EMI Payments: ₹{total_emi:,}
    Credit Card Minimum Dues: ₹{card_minimum_dues:,}
    Total Monthly Debt Obligations: ₹{monthly_debt:,}
    Debt-to-Income Ratio: {debt_to_income_ratio:.2f}%
    
    Loan Details:
    {json.dumps(safe_loans, indent=2)}
    
    Credit Card Details:
    {json.dumps(safe_cards, indent=2)}
    
    Please provide:
    1. A detailed analysis of whether their current EMIs are affordable based on the 50-30-20 rule or other financial principles
    2. How much additional EMI they could safely take on, if any
    3. Step-by-step calculations showing how you arrived at your recommendation
    4. Specific suggestions for managing their current debt more effectively
    5. Clear reasoning why they should follow your advice, backed by financial principles
    6. Use ₹ symbol for all currency values
    7. Include a breakdown of how their income should be allocated (essential expenses, debt, savings, etc.)
    
    Format your response with clear headings and bullet points.
    """
    return get_chatgpt_response(prompt)

def recommend_credit_cards(credit_info, preferences):
    """Recommend credit cards based on user profile and preferences"""
    # Get safe values with defaults
    credit_score = credit_info.get('credit_score', 700)
    income = credit_info.get('income', 50000)
    credit_cards = credit_info.get('credit_cards', [])
    
    # Handle None values
    if credit_score is None:
        credit_score = 700
    if income is None:
        income = 50000
    if credit_cards is None:
        credit_cards = []
    
    preference_str = ", ".join(preferences) if preferences else "general purpose"
    
    prompt = f"""
    As a financial advisor in India, recommend appropriate credit cards for a person with this profile:
    
    Credit Score: {credit_score}
    Monthly Income: ₹{income:,}
    Existing Credit Cards: {len(credit_cards)}
    Preferences: {preference_str}
    
    Please recommend 3-5 specific credit cards that would be suitable for this person. For each card, provide:
    1. Card name and issuer (use real Indian banks like HDFC, ICICI, SBI, Axis, etc.)
    2. Annual fee in ₹
    3. Key benefits (rewards, cashback percentages, airport lounge access, etc.)
    4. Why this particular card is a good match for their profile
    5. Any welcome offers or bonuses
    
    Format your response with clear headings and bullet points for readability.
    Include detailed reasons for each recommendation based on their income and credit profile.
    """
    return get_chatgpt_response(prompt)

def provide_financial_advice(credit_info, user_query):
    """Provide personalized financial advice based on user query"""
    # Get safe values with defaults
    credit_score = credit_info.get('credit_score', 700)
    income = credit_info.get('income', 50000)
    loans = credit_info.get('loans', [])
    credit_cards = credit_info.get('credit_cards', [])
    
    # Handle None values
    if credit_score is None:
        credit_score = 700
    if income is None:
        income = 50000
    if loans is None:
        loans = []
    if credit_cards is None:
        credit_cards = []
    
    # Make safe copies for the JSON
    safe_loans = []
    for loan in loans:
        if loan is None:
            continue
        safe_loan = {
            "type": loan.get("type", "Loan"),
            "lender": loan.get("lender", "Unknown"),
            "amount": loan.get("amount", 0),
            "current_balance": loan.get("current_balance", 0),
            "emi": loan.get("emi", 0),
            "interest_rate": loan.get("interest_rate", 0),
            "tenure": loan.get("tenure", 0),
            "remaining_tenure": loan.get("remaining_tenure", 0)
        }
        safe_loans.append(safe_loan)
    
    safe_cards = []
    for card in credit_cards:
        if card is None:
            continue
        safe_card = {
            "issuer": card.get("issuer", "Unknown"),
            "limit": card.get("limit", 0),
            "outstanding": card.get("outstanding", 0),
            "minimum_due": card.get("minimum_due", 0)
        }
        safe_cards.append(safe_card)
    
    prompt = f"""
    As a financial advisor, respond to this query from someone with the following financial profile in India:
    
    Credit Score: {credit_score}
    Monthly Income: ₹{income:,}
    Loans: {json.dumps(safe_loans, indent=2)}
    Credit Cards: {json.dumps(safe_cards, indent=2)}
    
    User's Question: "{user_query}"
    
    Please provide specific, personalized advice that:
    1. Directly addresses their question with Indian financial context
    2. Includes calculations where relevant (using ₹)
    3. Explains the reasoning behind your recommendation
    4. Considers their overall financial situation
    5. Provides clear action steps they can take
    6. Mentions relevant financial products or services in India
    
    Format your response with clear headings and bullet points.
    Include specific numbers and calculations to support your advice.
    """
    return get_chatgpt_response(prompt)

# Generate sample credit card database
def generate_credit_card_database():
    """Generate a database of sample credit cards"""
    cards = []
    
    # Travel cards
    cards.append({
        "name": "HDFC Diners Club Black",
        "issuer": "HDFC Bank",
        "annual_fee": 10000,
        "income_requirement": 1500000,
        "credit_score_requirement": 750,
        "category": "travel",
        "benefits": ["10X reward points on travel & dining", "Unlimited airport lounge access worldwide", 
                    "Buy 1 Get 1 movie tickets", "Golf privileges", "Milestone benefits up to ₹40,000"],
        "welcome_offer": "10,000 welcome points worth ₹10,000"
    })
    
    cards.append({
        "name": "SBI Card ELITE",
        "issuer": "SBI Card",
        "annual_fee": 4999,
        "income_requirement": 900000,
        "credit_score_requirement": 720,
        "category": "travel",
        "benefits": ["12 complimentary domestic airport lounge visits", "8 international airport lounge visits", 
                    "4 reward points per ₹100 spent", "1% fuel surcharge waiver", "Golf privileges"],
        "welcome_offer": "5,000 welcome points worth ₹5,000"
    })
    
    # More card entries (truncated for brevity)
    # Add more cards as needed from the original code
    
    return cards

def get_suitable_cards(credit_score, monthly_income, preferences, card_database):
    """Filter credit cards based on user's profile and preferences with robust NoneType handling"""
    # Handle None inputs
    if credit_score is None:
        credit_score = 700
    if monthly_income is None:
        monthly_income = 50000
    
    annual_income = monthly_income * 12
    suitable_cards = []
    
    for card in card_database:
        # Get card requirements with defaults
        card_score_req = card.get("credit_score_requirement", 0)
        card_income_req = card.get("income_requirement", 0)
        card_category = card.get("category", "")
        
        # Filter by credit score and income requirements
        if card_score_req <= credit_score and card_income_req <= annual_income:
            # Add card if there are no specific preferences or if card matches preferences
            if not preferences or card_category in preferences:
                suitable_cards.append(card)
    
    # Sort by most suitable (higher income/credit score requirements first as they typically have better benefits)
    suitable_cards.sort(key=lambda x: (x.get("income_requirement", 0), x.get("credit_score_requirement", 0)), reverse=True)
    
    # Return top 5 cards or all if less than 5
    return suitable_cards[:5]

def visualize_credit_score(credit_score):
    """Create a gauge chart for credit score visualization"""
    if credit_score is None:
        credit_score = 700
        
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=credit_score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Credit Score"},
        gauge={
            "axis": {"range": [300, 900], "tickwidth": 1, "tickcolor": "darkblue"},
            "bar": {"color": "darkblue"},
            "bgcolor": "white",
            "borderwidth": 2,
            "bordercolor": "gray",
            "steps": [
                {"range": [300, 550], "color": "red"},
                {"range": [550, 650], "color": "orange"},
                {"range": [650, 750], "color": "yellow"},
                {"range": [750, 900], "color": "green"}
            ],
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="white",
        font={"color": "darkblue", "family": "Arial"}
    )
    
    return fig

def visualize_debt_to_income(credit_info):
    """Create a visualization for debt-to-income ratio"""
    try:
        # Safely get loan and card lists
        loans = credit_info.get("loans", [])
        if loans is None:
            loans = []
            
        credit_cards = credit_info.get("credit_cards", [])
        if credit_cards is None:
            credit_cards = []
        
        # Safely calculate total EMI
        total_emi = 0
        for loan in loans:
            if loan is None:
                continue
            emi = loan.get("emi")
            if emi is not None and isinstance(emi, (int, float)):
                total_emi += emi
        
        # Safely calculate card dues
        card_minimum_dues = 0
        for card in credit_cards:
            if card is None:
                continue
            min_due = card.get("minimum_due")
            if min_due is not None and isinstance(min_due, (int, float)):
                card_minimum_dues += min_due
        
        monthly_debt = total_emi + card_minimum_dues
        
        # Ensure income is a number, not None
        income = credit_info.get("income")
        if income is None or not isinstance(income, (int, float)) or income <= 0:
            income = 50000  # Default value for display
        
        # Calculate recommended allocation using 50-30-20 rule
        essentials = income * 0.5
        wants = income * 0.3
        savings = income * 0.2
        
        # Create stacked bar chart
        fig = go.Figure()
        
        # Current allocation
        fig.add_trace(go.Bar(
            x=["Current Allocation"],
            y=[monthly_debt],
            name="Debt Payments",
            marker_color="#FF5722"
        ))
        fig.add_trace(go.Bar(
            x=["Current Allocation"],
            y=[income - monthly_debt],
            name="Remaining Income",
            marker_color="#E0E0E0"
        ))
        
        # Recommended allocation
        fig.add_trace(go.Bar(
            x=["Recommended Allocation"],
            y=[essentials],
            name="Essentials (50%)",
            marker_color="#2196F3"
        ))
        fig.add_trace(go.Bar(
            x=["Recommended Allocation"],
            y=[wants],
            name="Wants (30%)",
            marker_color="#4CAF50"
        ))
        fig.add_trace(go.Bar(
            x=["Recommended Allocation"],
            y=[savings],
            name="Savings (20%)",
            marker_color="#FFC107"
        ))
        
        fig.update_layout(
            title="Income Allocation Analysis",
            barmode="stack",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=80, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font={"color": "darkblue", "family": "Arial"}
        )
        
        return fig
    except Exception as e:
        # Return an empty figure if there's any error
        print(f"Error creating debt visualization: {str(e)}")
        fig = go.Figure()
        fig.update_layout(
            title="Income Allocation Analysis (Error Loading)",
            height=400
        )
        return fig

def load_sample_data():
    """Load sample data for demonstration"""
    sample_data = {
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
            },
            {
                "type": "Personal Loan",
                "lender": "ICICI Bank",
                "amount": 500000,
                "current_balance": 300000,
                "emi": 15000,
                "interest_rate": 12.0,
                "tenure": 36,
                "remaining_tenure": 24
            }
        ],
        "credit_cards": [
            {
                "issuer": "ICICI Bank",
                "limit": 300000,
                "outstanding": 50000,
                "minimum_due": 2500
            },
            {
                "issuer": "SBI Card",
                "limit": 200000,
                "outstanding": 30000,
                "minimum_due": 1500
            }
        ],
        "payment_history": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "inquiries": 2
    }
    return sample_data

# Main application UI
def main():
    # Initialize all variables
    income = 0
    credit_score = 0
    total_emi = 0
    card_minimum_dues = 0
    monthly_debt = 0
    debt_to_income_ratio = 0
    
    # Sidebar content
    with st.sidebar:
        st.title("Assistant")
        
        st.markdown("---")
        
        # Navigation options directly in sidebar
        nav_option = st.radio(
            "Navigation",
            ["Home", "Credit Score Analysis", "EMI Affordability", "Card Recommendations", "Financial Advisor"]
        )
        
        st.markdown("---")
        
        # Sample data options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample Report"):
                st.session_state.credit_info = load_sample_data()
                st.success("Sample report loaded successfully!")
                st.rerun()
        
        with col2:
            if st.button("Show Sample JSON"):
                if "show_sample_json" not in st.session_state:
                    st.session_state.show_sample_json = True
                else:
                    st.session_state.show_sample_json = True
                st.rerun()
                
        # Display sample JSON if button was clicked
        if "show_sample_json" in st.session_state and st.session_state.show_sample_json:
            st.subheader("Sample Credit Report Format (JSON)")
            sample_json = {
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
            st.code(json.dumps(sample_json, indent=2), language="json")
            
            # Add a button to hide the sample JSON
            if st.button("Hide Sample JSON"):
                st.session_state.show_sample_json = False
                st.rerun()
        
        st.markdown("---")
        
        st.subheader("How to Use")
        st.markdown("""
        1. Upload your credit report (JSON)
        2. Review your credit score analysis
        3. Check your EMI affordability
        4. Get credit card recommendations
        5. Ask questions to our AI financial advisor
        """)
    
    # Main content
    st.title("Financial Assistant")
    
    # Initialize session state
    if "credit_info" not in st.session_state:
        st.session_state.credit_info = None
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "card_preferences" not in st.session_state:
        st.session_state.card_preferences = []
    
    # File upload section on the right
    col1, col2 = st.columns([7, 3])
    
    with col2:
        st.subheader("📄 Upload Credit Report")
        uploaded_file = st.file_uploader("Upload your credit report (JSON format)", type="json")
        
        if uploaded_file is not None:
            st.success("File uploaded successfully!")
            if st.button("🔍 Analyze Report", type="primary"):
                with st.spinner("Analyzing your credit report..."):
                    try:
                        # Read JSON from uploaded file
                        credit_data = json.load(uploaded_file)
                        
                        # Extract credit information
                        credit_info = extract_credit_info(credit_data)
                        
                        # Store in session state
                        st.session_state.credit_info = credit_info
                        
                        # Clear previous analyses when a new report is uploaded
                        if "credit_score_analysis" in st.session_state:
                            del st.session_state.credit_score_analysis
                        if "emi_analysis" in st.session_state:
                            del st.session_state.emi_analysis
                        if "card_recommendations" in st.session_state:
                            del st.session_state.card_recommendations
                        
                        st.session_state.chat_history = []
                        
                        st.success("Credit report analyzed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing credit report: {str(e)}")
    
    with col1:
        # Coming Soon Features Section
        st.info("🔜 **Coming Soon Features**")
        cols = st.columns(4)
        with cols[0]:
            st.write("🔄 **Direct CIBIL Integration**")
            st.write("One-click connectivity with Transunion CIBIL report")
        with cols[1]:
            st.write("📄 **PDF Support**")
            st.write("Upload credit reports in PDF format")
        st.caption("*We're currently in beta phase, working hard to bring you these exciting new features!*")
    
    # Display main content based on navigation selection
    if nav_option == "Home" and st.session_state.credit_info is None:
        # Welcome message
        st.header("Welcome to Financial Assistant")
        
        # Key features
        st.subheader("Key Features")
        cols = st.columns(4)
        
        with cols[0]:
            st.write("### 📊 Credit Analysis")
            st.write("Understand what factors are affecting your credit score and how to improve it")
        
        with cols[1]:
            st.write("### 💰 EMI Calculator")
            st.write("Plan your loans with our advanced EMI calculator and affordability analysis")
        
        with cols[2]:
            st.write("### 💳 Card Recommendations")
            st.write("Get personalized credit card suggestions based on your financial profile")
        
        with cols[3]:
            st.write("### 🤖 AI Financial Advisor")
            st.write("Get expert financial advice tailored to your specific financial situation")
        
        # Sample JSON structure
        st.subheader("Sample Credit Report Format (JSON)")
        sample_json = {
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
        st.code(json.dumps(sample_json, indent=2), language="json")
    
    # Check if credit info is available and display appropriate content
    elif st.session_state.credit_info:
        credit_info = st.session_state.credit_info
        
        # Summary card with key metrics if we're on the home page
        if nav_option == "Home":
            st.subheader("📊 Financial Summary")
            cols = st.columns(4)
            
            with cols[0]:
                credit_score = credit_info.get('credit_score')
                if credit_score is not None:
                    st.metric("Credit Score", f"{credit_score}", 
                             delta="Excellent" if credit_score >= 750 else 
                             "Good" if credit_score >= 700 else
                             "Fair" if credit_score >= 650 else "Poor")
                else:
                    st.metric("Credit Score", "N/A", delta="Unknown")
            
            with cols[1]:
                income = credit_info.get('income', 0)
                if income:
                    st.metric("Monthly Income", f"₹{income:,}")
                else:
                    st.metric("Monthly Income", "N/A")
            
            with cols[2]:
                loans = credit_info.get('loans', [])
                if loans is None:
                    loans = []
                total_emi = sum(loan.get("emi", 0) for loan in loans if loan is not None)
                st.metric("Total Monthly EMIs", f"₹{total_emi:,}")
            
            with cols[3]:
                credit_cards = credit_info.get('credit_cards', [])
                if credit_cards is None:
                    credit_cards = []
                card_minimum_dues = sum(card.get("minimum_due", 0) for card in credit_cards if card is not None)
                monthly_debt = total_emi + card_minimum_dues
                income = credit_info.get('income', 0)
                if income is None or not isinstance(income, (int, float)) or income <= 0:
                    income = 1  # Avoid division by zero
                debt_to_income_ratio = (monthly_debt / income) * 100 if income > 0 else 0
                st.metric("Debt-to-Income Ratio", f"{debt_to_income_ratio:.1f}%", 
                         delta="Healthy" if debt_to_income_ratio <= 40 else 
                         "Moderate" if debt_to_income_ratio <= 60 else "High", 
                         delta_color="normal" if debt_to_income_ratio <= 40 else 
                         "off" if debt_to_income_ratio <= 60 else "inverse")
        
        # Credit Score Analysis Tab
        if nav_option == "Credit Score Analysis":
            st.header("Credit Score Analysis")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Credit score gauge
                credit_score = credit_info.get("credit_score", 0)
                if credit_score is not None:
                    fig = visualize_credit_score(credit_score)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Display credit score analysis from ChatGPT
                if "credit_score_analysis" not in st.session_state:
                    with st.spinner("Analyzing your credit score..."):
                        st.session_state.credit_score_analysis = analyze_credit_score(credit_info)
                
                # Analysis box
                st.subheader("AI Credit Score Analysis")
                st.write(st.session_state.credit_score_analysis)
                
                # Add a "Refresh Analysis" button
                if st.button("🔄 Refresh Credit Score Analysis"):
                    with st.spinner("Refreshing credit score analysis..."):
                        st.session_state.credit_score_analysis = analyze_credit_score(credit_info)
                        st.rerun()
        
        # EMI Affordability Tab
        elif nav_option == "EMI Affordability":
            st.header("EMI Affordability Analysis")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Visualizations
                fig = visualize_debt_to_income(credit_info)
                st.plotly_chart(fig, use_container_width=True)
                
                # EMI calculator
                st.subheader("EMI Calculator")
                loan_amount = st.slider("Loan Amount (₹)", 10000, 10000000, 1000000, step=10000)
                interest_rate = st.slider("Interest Rate (%)", 5.0, 20.0, 10.0, step=0.1)
                loan_tenure = st.slider("Loan Tenure (Years)", 1, 30, 5)
                
                # Calculate EMI
                monthly_interest_rate = interest_rate / (12 * 100)
                tenure_months = loan_tenure * 12
                emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure_months) / (((1 + monthly_interest_rate) ** tenure_months) - 1)
                
                st.metric("Calculated Monthly EMI", f"₹{emi:,.2f}")
                
                # Calculate total interest payable
                total_payment = emi * tenure_months
                total_interest = total_payment - loan_amount
                
                st.metric("Total Interest Payable", f"₹{total_interest:,.2f}")
            
            with col2:
                # Display EMI affordability analysis from ChatGPT
                if "emi_analysis" not in st.session_state:
                    with st.spinner("Analyzing your EMI affordability..."):
                        st.session_state.emi_analysis = analyze_emi_affordability(credit_info)
                
                # Enhanced styled box for the EMI analysis
                st.subheader("AI EMI Affordability Analysis")
                st.write(st.session_state.emi_analysis)
                
                # Add a "Refresh Analysis" button
                if st.button("🔄 Refresh EMI Analysis"):
                    with st.spinner("Refreshing EMI analysis..."):
                        st.session_state.emi_analysis = analyze_emi_affordability(credit_info)
                        st.rerun()
        
        # Card Recommendations Tab
        elif nav_option == "Card Recommendations":
            st.header("Credit Card Recommendations")
            
            # Card preference selection
            st.subheader("What are your credit card preferences?")
            preferences = st.multiselect(
                "Select your preferences (you can select multiple)",
                ["travel", "shopping", "fuel", "premium", "lifestyle", "business", "starter", "secured", "student"],
                default=st.session_state.card_preferences
            )
            
            preference_changed = st.session_state.card_preferences != preferences
            
            # Update session state
            st.session_state.card_preferences = preferences
            
            # Generate credit card database
            card_database = generate_credit_card_database()
            
            # Get suitable cards
            suitable_cards = get_suitable_cards(credit_info.get("credit_score"), credit_info.get("income"), preferences, card_database)
            
            # Display cards
            if suitable_cards:
                st.subheader("Recommended Cards Based on Your Profile")
                
                for card in suitable_cards:
                    with st.expander(f"{card['name']} by {card['issuer']}"):
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            st.write(f"**{card['issuer']}**")
                            st.write(f"**Annual Fee:** ₹{card['annual_fee']:,}")
                            st.write(f"**Min. Credit Score:** {card['credit_score_requirement']}")
                            st.write(f"**Min. Annual Income:** ₹{card['income_requirement']:,}")
                            if card['welcome_offer'] != "None":
                                st.write(f"**Welcome Offer:** {card['welcome_offer']}")
                        
                        with col2:
                            st.write("**Key Benefits:**")
                            for benefit in card['benefits']:
                                st.write(f"- {benefit}")
            
                # Get detailed AI recommendations
                if "card_recommendations" not in st.session_state or preference_changed:
                    with st.spinner("Getting personalized card recommendations..."):
                        st.session_state.card_recommendations = recommend_credit_cards(credit_info, preferences)
                
                st.subheader("Detailed Analysis and Recommendations")
                st.write(st.session_state.card_recommendations)
                
                # Add a "Refresh Recommendations" button
                if st.button("🔄 Refresh Card Recommendations"):
                    with st.spinner("Refreshing card recommendations..."):
                        st.session_state.card_recommendations = recommend_credit_cards(credit_info, preferences)
                        st.rerun()
            else:
                st.warning("Based on your credit profile, we couldn't find suitable credit cards. Please improve your credit score or income to qualify for credit cards.")
        
        # Financial Advisor Tab
        elif nav_option == "Financial Advisor":
            st.header("Personal Finance Manager")
            
            # Display chat history
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant", avatar="🤖").write(message["content"])
            
            # Chat input
            user_question = st.chat_input("Ask me anything about your financial situation...")
            
            if user_question:
                # Add user message to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Display user message immediately
                st.chat_message("user").write(user_question)
                
                # Get AI response
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner("Getting financial advice..."):
                        try:
                            ai_response = provide_financial_advice(credit_info, user_question)
                            st.write(ai_response)
                            
                            # Add AI response to chat history
                            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                        except Exception as e:
                            error_message = f"Sorry, I couldn't generate financial advice at the moment. Error: {str(e)}"
                            st.error(error_message)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_message})
            
            # Predefined financial questions
            st.subheader("Common Financial Questions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💰 Should I pay off my debt or invest?"):
                    query = "Should I pay off my debt or invest my extra money?"
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    with st.spinner("Getting financial advice..."):
                        ai_response = provide_financial_advice(credit_info, "Should I pay off my debt or invest my extra money? Please do the math based on my current loans and income.")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                
                if st.button("🏠 How much house can I afford?"):
                    query = "How much house can I afford based on my income and current EMIs?"
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    with st.spinner("Getting financial advice..."):
                        ai_response = provide_financial_advice(credit_info, "How much house can I afford based on my income and current EMIs? What would be my maximum affordable home loan amount?")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
            
            with col2:
                if st.button("📈 How can I improve my credit score?"):
                    query = "How can I improve my credit score quickly?"
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    with st.spinner("Getting financial advice..."):
                        ai_response = provide_financial_advice(credit_info, "How can I improve my credit score quickly? Give me specific steps based on my current credit profile.")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
                
                if st.button("💳 Should I take a personal loan?"):
                    query = "Is it a good idea for me to take a personal loan right now?"
                    st.session_state.chat_history.append({"role": "user", "content": query})
                    with st.spinner("Getting financial advice..."):
                        ai_response = provide_financial_advice(credit_info, "Is it a good idea for me to take a personal loan right now based on my financial situation? What amount would be safe for me to borrow?")
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()

if __name__ == "__main__":
    main()
