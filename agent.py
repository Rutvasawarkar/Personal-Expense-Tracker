import os
import json
from datetime import date, datetime

from dotenv import load_dotenv
from openai import OpenAI

from database import (
    get_spending_summary,
    add_expense
)


# Load variables from .env
load_dotenv()


# Get API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY was not found. "
        "Make sure it is present in your .env file."
    )


# Create OpenAI client
client = OpenAI(api_key=api_key)


# Today's date from Python
TODAY = date.today().isoformat()


# Tools available to the AI agent
tools = [

    # ---------------------------------------------------------
    # TOOL 1: Get spending summary
    # ---------------------------------------------------------

    {
        "type": "function",
        "name": "get_spending_summary",
        "description": (
            "Retrieve the user's actual spending from the expense "
            "database. Use this when the user asks how much they "
            "spent, asks about a category, or asks about spending "
            "during a specific period. All amounts are in INR."
        ),
        "parameters": {
            "type": "object",

            "properties": {

                "category": {
                    "type": [
                        "string",
                        "null"
                    ],
                    "description": (
                        "Expense category. Use exactly one of: "
                        "Food, Travel, Shopping, Bills, Entertainment, "
                        "Education, Other. "
                        "Use null when asking about all categories."
                    )
                },

                "period": {
                    "type": "string",
                    "enum": [
                        "all",
                        "this_month",
                        "today"
                    ],
                    "description": (
                        "Use 'this_month' for the current month, "
                        "'today' for today's expenses, and 'all' "
                        "when there is no time restriction."
                    )
                }

            },

            "required": [
                "category",
                "period"
            ],

            "additionalProperties": False
        }
    },


    # ---------------------------------------------------------
    # TOOL 2: Add a new expense
    # ---------------------------------------------------------

    {
        "type": "function",
        "name": "add_expense",
        "description": (
            "Add a new expense to the user's SQLite expense database. "
            "Use this when the user explicitly states that they spent "
            "money or wants to record an expense. "
            "All amounts are in Indian Rupees (INR)."
        ),
        "parameters": {
            "type": "object",

            "properties": {

                "amount": {
                    "type": "number",
                    "description": (
                        "Amount spent in Indian Rupees. "
                        "Must be greater than 0."
                    )
                },

                "category": {
                    "type": "string",
                    "enum": [
                        "Food",
                        "Travel",
                        "Shopping",
                        "Bills",
                        "Entertainment",
                        "Education",
                        "Other"
                    ],
                    "description": "Category of the expense."
                },

                "description": {
                    "type": "string",
                    "description": (
                        "Short description of what the user spent "
                        "the money on."
                    )
                },

                "expense_date": {
                    "type": "string",
                    "description": (
                        "Date of the expense in YYYY-MM-DD format. "
                        f"Today's date is {TODAY}. "
                        "Use today's date when the user says today."
                    )
                }

            },

            "required": [
                "amount",
                "category",
                "description",
                "expense_date"
            ],

            "additionalProperties": False
        }
    }

]


def validate_expense_data(
    amount,
    category,
    description,
    expense_date
):
    """Validate data before saving an agent-created expense."""

    # Check amount
    if amount <= 0:
        raise ValueError("Expense amount must be greater than 0.")

    # Check category
    valid_categories = {
        "Food",
        "Travel",
        "Shopping",
        "Bills",
        "Entertainment",
        "Education",
        "Other"
    }

    if category not in valid_categories:
        raise ValueError("Invalid expense category.")

    # Check description
    if not description.strip():
        description = "Expense"

    # Check date format
    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "Expense date must be in YYYY-MM-DD format."
        )

    return description.strip()


def execute_add_expense(arguments):
    """Execute the add_expense tool."""

    amount = float(arguments["amount"])
    category = arguments["category"]
    description = arguments["description"]
    expense_date = arguments["expense_date"]

    description = validate_expense_data(
        amount,
        category,
        description,
        expense_date
    )

    # Save to SQLite
    add_expense(
        amount=amount,
        category=category,
        description=description,
        expense_date=expense_date
    )

    return {
        "success": True,
        "message": "Expense successfully added.",
        "amount": amount,
        "currency": "INR",
        "currency_symbol": "₹",
        "category": category,
        "description": description,
        "date": expense_date
    }


def run_agent(user_message):
    """Run the AI expense agent."""

    response = client.responses.create(

        model="gpt-5.6-luna",

        instructions=(
            "You are a personal expense tracking assistant. "

            "The user's actual expenses are stored in a SQLite database. "

            "All monetary values are in Indian Rupees (INR). "
            "Always use the ₹ symbol when displaying money. "

            "You have two tools: "
            "get_spending_summary for reading expense data and "
            "add_expense for recording a new expense. "

            "When the user asks about existing spending, "
            "ALWAYS use get_spending_summary. "

            "When the user explicitly says they spent money or "
            "asks you to record an expense, use add_expense. "

            f"Today's date is {TODAY}. "
            "When the user says today, use today's date. "

            "For category questions, use null when no category "
            "is specified. Never use 'All categories' as a category. "

            "Never invent expense data."
        ),

        input=user_message,

        tools=tools
    )


    # Check whether the model called a tool
    for item in response.output:

        if item.type != "function_call":
            continue


        # -----------------------------------------------------
        # Spending summary tool
        # -----------------------------------------------------

        if item.name == "get_spending_summary":

            arguments = json.loads(item.arguments)

            category = arguments.get("category")
            period = arguments.get("period", "all")

            result = get_spending_summary(
                category=category,
                period=period
            )

            final_response = client.responses.create(

                model="gpt-5.6-luna",

                instructions=(
                    "Answer the user's question using the database "
                    "result provided. "

                    "All monetary values are in Indian Rupees. "
                    "Always use the ₹ symbol. "

                    "Do not change, invent, or estimate the numbers. "

                    "Keep the answer concise and clear."
                ),

                input=[
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    }
                ],

                previous_response_id=response.id
            )

            return final_response.output_text


        # -----------------------------------------------------
        # Add expense tool
        # -----------------------------------------------------

        if item.name == "add_expense":

            arguments = json.loads(item.arguments)

            try:

                result = execute_add_expense(arguments)

            except ValueError as error:

                result = {
                    "success": False,
                    "message": str(error)
                }


            final_response = client.responses.create(

                model="gpt-5.6-luna",

                instructions=(
                    "Tell the user what happened using the tool result. "

                    "If the expense was successfully added, confirm "
                    "the amount, category, description, and date. "

                    "All monetary values are in Indian Rupees. "
                    "Always use the ₹ symbol. "

                    "Do not claim an expense was added if success is false. "

                    "Keep the response concise."
                ),

                input=[
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps(result)
                    }
                ],

                previous_response_id=response.id
            )

            return final_response.output_text


    # No tool was needed
    return response.output_text


if __name__ == "__main__":

    question = input("Ask the expense agent: ")

    answer = run_agent(question)

    print("\nAgent:")
    print(answer)