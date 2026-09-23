import os
import json
from datetime import date, datetime

from dotenv import load_dotenv
from openai import OpenAI

from database import (
    get_spending_summary,
    add_expense
)


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()


# ---------------------------------------------------------
# OpenRouter API key
# ---------------------------------------------------------
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY was not found. "
        "Make sure it is present in your .env file "
        "and in Render environment variables."
    )


# ---------------------------------------------------------
# Create OpenAI-compatible client for OpenRouter
# ---------------------------------------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


# ---------------------------------------------------------
# Free OpenRouter model router
# ---------------------------------------------------------
# OpenRouter automatically selects an available free model.
# The free router supports tool calling.
MODEL = "openrouter/free"


# ---------------------------------------------------------
# Today's date from Python
# ---------------------------------------------------------
TODAY = date.today().isoformat()


# ---------------------------------------------------------
# Tools available to the AI agent
# ---------------------------------------------------------
tools = [

    # -----------------------------------------------------
    # TOOL 1: Get spending summary
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
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
                        "type": ["string", "null"],
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
        }
    },


    # -----------------------------------------------------
    # TOOL 2: Add a new expense
    # -----------------------------------------------------
    {
        "type": "function",
        "function": {
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
    }

]


# ---------------------------------------------------------
# Validate agent-created expense data
# ---------------------------------------------------------
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
    if not isinstance(description, str):
        description = "Expense"

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


# ---------------------------------------------------------
# Execute add_expense tool
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# Execute requested tool
# ---------------------------------------------------------
def execute_tool(tool_name, arguments):
    """Run the requested backend tool safely."""

    if tool_name == "get_spending_summary":

        category = arguments.get("category")
        period = arguments.get("period", "all")

        result = get_spending_summary(
            category=category,
            period=period
        )

        return {
            "success": True,
            "data": result
        }

    if tool_name == "add_expense":

        try:
            return execute_add_expense(arguments)

        except (ValueError, KeyError, TypeError) as error:
            return {
                "success": False,
                "message": str(error)
            }

    return {
        "success": False,
        "message": f"Unknown tool: {tool_name}"
    }


# ---------------------------------------------------------
# Run the AI expense agent
# ---------------------------------------------------------
def run_agent(user_message):
    """Run the AI expense agent using OpenRouter."""

    messages = [
        {
            "role": "system",
            "content": (
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

                "Never invent expense data. "

                "For financial figures, rely on the database tool result. "
                "Do not calculate or estimate totals yourself. "

                "If the user clearly asks to record multiple separate "
                "expenses, you may make multiple add_expense tool calls."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    # -----------------------------------------------------
    # Tool-calling loop
    # -----------------------------------------------------
    # Allows the agent to handle one or multiple tool calls.
    # -----------------------------------------------------
    for _ in range(3):

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

        except Exception as error:
            print(f"OpenRouter API error: {error}")

            return (
                "The AI service is temporarily unavailable. "
                "Please try again."
            )

        message = response.choices[0].message

        # -------------------------------------------------
        # No tool call = final answer
        # -------------------------------------------------
        if not message.tool_calls:

            return message.content or (
                "I couldn't generate a response. Please try again."
            )

        # -------------------------------------------------
        # Add assistant tool-call message
        # -------------------------------------------------
        assistant_tool_calls = []

        for tool_call in message.tool_calls:
            assistant_tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
            )

        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": assistant_tool_calls
            }
        )

        # -------------------------------------------------
        # Execute every requested tool
        # -------------------------------------------------
        for tool_call in message.tool_calls:

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError:
                result = {
                    "success": False,
                    "message": (
                        "Invalid tool arguments generated by the model."
                    )
                }

            else:
                result = execute_tool(
                    tool_name=tool_call.function.name,
                    arguments=arguments
                )

            # -------------------------------------------------
            # Send tool result back to the model
            # -------------------------------------------------
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                }
            )

    return (
        "The agent reached its tool-processing limit. "
        "Please try a simpler request."
    )


# ---------------------------------------------------------
# Direct terminal testing
# ---------------------------------------------------------
if __name__ == "__main__":

    question = input("Ask the expense agent: ")

    answer = run_agent(question)

    print("\nAgent:")
    print(answer)