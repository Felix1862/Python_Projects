"""
Investment Tracking Application

This application allows users to simulate a 25-year investment projection
with two providers: Oak and MansaX. It uses compound interest, optional
top-ups, withdrawal preferences, and lock-in periods to estimate how
investments grow over time.

Features:
- Validated user input for investment amounts
- Annual top-ups and withdrawals
- Lock-in period before withdrawals are allowed
- Combined summaries across both funds
- Uses live GBP/KES exchange rates (optional)

Author: Felix Kaz
License: MIT
"""

import sqlite3
from datetime import datetime
import requests

# Constants for interest rates
OAK_RATE = 0.1864
MANSAX_RATE = 0.1956

# SQLite setup
db = sqlite3.connect("investment_tracker.db")
cursor = db.cursor()

# Recreate MMF_Combined table
cursor.execute("DROP TABLE IF EXISTS MMF_Combined")
cursor.execute("""
    CREATE TABLE MMF_Combined (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        currency TEXT,
        provider_oak TEXT,
        provider_mansax TEXT,
        invest_oak REAL,
        invest_mansax REAL,
        start_month_oak TEXT,
        start_year_oak INTEGER,
        start_month_mansax TEXT,
        start_year_mansax INTEGER,
        investment_type TEXT,
        monthly_invest_months INTEGER,
        annual_topup_oak REAL,
        annual_topup_mansax REAL,
        investment_duration INTEGER,
        interest_withdraw_start_year INTEGER,
        oak_withdraw_amount REAL,
        mansax_withdraw_amount REAL
    )
""")
db.commit()


def validate_float_input(prompt):
    """
    Prompt the user for a positive float value.
    
    Args:
        prompt (str): Prompt message for input.
    
    Returns:
        float: Validated float input.
    """
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            print("Invalid input. Please enter a positive number.")


def validate_int_input(prompt, valid_options=None):
    """
    Prompt the user for a positive integer, optionally restricted to a set.
    
    Args:
        prompt (str): Prompt message.
        valid_options (list[int], optional): List of valid integers.
    
    Returns:
        int: Validated integer input.
    """
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                raise ValueError
            if valid_options and value not in valid_options:
                raise ValueError
            return value
        except ValueError:
            msg = "Invalid input."
            if valid_options:
                msg += f" Choose from {valid_options}."
            print(msg)


def validate_str_input(prompt, options=None):
    """
    Prompt the user for a string input, optionally validating against choices.
    
    Args:
        prompt (str): Prompt message.
        options (list[str], optional): Valid input options.
    
    Returns:
        str: Validated string input.
    """
    while True:
        value = input(prompt).strip().lower()
        if options and value not in options:
            print(f"Invalid input. Choose from {options}.")
        else:
            return value


def get_current_exchange_rate():
    """
    Fetch the current exchange rate from KES to GBP.

    Returns:
        float: Exchange rate or fallback value.
    """
    try:
        response = requests.get(
            "https://api.exchangerate.host/latest?base=KES&symbols=GBP"
        )
        return response.json()["rates"]["GBP"]
    except Exception as e:
        print("Error fetching exchange rate:", e)
        return 0.0058


def calculate_projection_25_years(principal, rate, topup, withdraw_amount, lock_years):
    """
    Calculate a 25-year projection of an investment with compound interest.
    
    Args:
        principal (float): Initial investment.
        rate (float): Annual interest rate.
        topup (float): Annual top-up contribution.
        withdraw_amount (float): Annual withdrawal after lock-in.
        lock_years (int): Number of years before withdrawal starts.
    
    Returns:
        list[dict]: Yearly breakdown of the investment growth.
    """
    projection = []
    balance = principal

    for year in range(1, 26):
        interest = balance * rate
        withdrawn = 0 if year <= lock_years else withdraw_amount
        balance += topup + interest
        if year > lock_years:
            balance -= withdrawn

        projection.append({
            "Year": year,
            "Interest": round(interest, 2),
            "Topup": round(topup, 2),
            "Withdrawn": round(withdrawn, 2),
            "Remaining": round(balance, 2)
        })

    return projection


def display_projection_summary(investment):
    """
    Display the 25-year investment summary for Oak and MansaX.
    
    Args:
        investment (dict): Contains amounts, top-ups, and withdrawals.
    """
    lock_years = validate_int_input(
        "How many years do you want to lock the funds "
        "before any withdrawal? (e.g., 3): "
    )
    print("\n--- 25-Year Projection Summary ---")

    oak_proj = []
    mansax_proj = []

    if investment['invest_oak'] > 0:
        oak_proj = calculate_projection_25_years(
            investment['invest_oak'],
            OAK_RATE,
            investment['annual_topup_oak'],
            investment['oak_withdraw_amount'],
            lock_years
        )

    if investment['invest_mansax'] > 0:
        mansax_proj = calculate_projection_25_years(
            investment['invest_mansax'],
            MANSAX_RATE,
            investment['annual_topup_mansax'],
            investment['mansax_withdraw_amount'],
            lock_years
        )

    for year in range(25):
        y = year + 1

        if oak_proj:
            label_oak = "(LOCKED)" if y <= lock_years else ""
            oak = oak_proj[year]
            print(
                f"Year {y:2} | Fund: Oak {label_oak} | Interest: "
                f"{oak['Interest']:,.2f} | Topup: {oak['Topup']:,.2f} | "
                f"Withdrawn: {oak['Withdrawn']:,.2f} | "
                f"Remaining: {oak['Remaining']:,.2f}"
            )

        if mansax_proj:
            label_mansax = "(LOCKED)" if y <= lock_years else ""
            mx = mansax_proj[year]
            print(
                f"Year {y:2} | Fund: MansaX {label_mansax} | Interest: "
                f"{mx['Interest']:,.2f} | Topup: {mx['Topup']:,.2f} | "
                f"Withdrawn: {mx['Withdrawn']:,.2f} | "
                f"Remaining: {mx['Remaining']:,.2f}"
            )

        if oak_proj and mansax_proj:
            net = oak_proj[year]['Interest'] + mansax_proj[year]['Interest']
            wd = oak_proj[year]['Withdrawn'] + mansax_proj[year]['Withdrawn']
            retained = net - wd
            print(
                f"     Combined Net Interest: {net:,.2f} | "
                f"Combined Withdrawn: {wd:,.2f} | "
                f"Retained Net Interest: {retained:,.2f}\n"
            )
        elif oak_proj or mansax_proj:
            print()


if __name__ == "__main__":
    print("\n--- Enter Investment Details ---")

    invest_oak = validate_float_input("Initial Oak investment (KES): ")
    invest_mansax = validate_float_input("Initial MansaX investment (KES): ")
    annual_topup_oak = validate_float_input("Annual top-up for Oak (KES): ")
    annual_topup_mansax = validate_float_input("Annual top-up for MansaX (KES): ")
    oak_withdraw_amount = validate_float_input("Annual withdrawal from Oak (KES): ")
    mansax_withdraw_amount = validate_float_input(
        "Annual withdrawal from MansaX (KES): "
    )

    user_investment = {
        'invest_oak': invest_oak,
        'invest_mansax': invest_mansax,
        'annual_topup_oak': annual_topup_oak,
        'annual_topup_mansax': annual_topup_mansax,
        'oak_withdraw_amount': oak_withdraw_amount,
        'mansax_withdraw_amount': mansax_withdraw_amount
    }

    display_projection_summary(user_investment)
