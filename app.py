from flask import Flask, render_template, request, redirect, url_for

from database import (
    initialize_database,
    add_expense,
    delete_expense,
    get_all_expenses,
    get_total_spending,
    get_monthly_spending,
    get_transaction_count,
    get_category_spending
)

from agent import run_agent


app = Flask(__name__)


# Initialize the database when Flask starts
initialize_database()


def create_category_breakdown(monthly_spending):
    """
    Create category breakdown data for the dashboard.

    The percentage is rounded to the nearest 5 so it can be
    represented using a predefined CSS class.
    """

    category_rows = get_category_spending()

    category_breakdown = []

    for row in category_rows:

        if monthly_spending > 0:
            percentage = (row["total"] / monthly_spending) * 100
        else:
            percentage = 0

        # Round percentage to nearest 5
        bar_percentage = round(percentage / 5) * 5

        # Keep the value between 0 and 100
        bar_percentage = max(0, min(100, bar_percentage))

        category_breakdown.append({
            "category": row["category"],
            "total": row["total"],
            "transactions": row["transactions"],
            "percentage": percentage,
            "bar_percentage": bar_percentage
        })

    return category_breakdown


def get_dashboard_data():
    """Get all data required by the dashboard."""

    expenses = get_all_expenses()
    total_spending = get_total_spending()
    monthly_spending = get_monthly_spending()
    transaction_count = get_transaction_count()

    category_breakdown = create_category_breakdown(
        monthly_spending
    )

    return {
        "expenses": expenses,
        "total_spending": total_spending,
        "monthly_spending": monthly_spending,
        "transaction_count": transaction_count,
        "category_breakdown": category_breakdown
    }


@app.route("/")
def home():
    """Display the main expense tracker page."""

    dashboard = get_dashboard_data()

    return render_template(
        "index.html",
        **dashboard
    )


@app.route("/add-expense", methods=["POST"])
def add_expense_route():
    """Save an expense submitted through the Add Expense form."""

    amount = float(request.form["amount"])
    category = request.form["category"]
    description = request.form["description"]
    expense_date = request.form["date"]

    add_expense(
        amount=amount,
        category=category,
        description=description,
        expense_date=expense_date
    )

    return redirect(url_for("home"))


@app.route("/delete-expense/<int:expense_id>", methods=["POST"])
def delete_expense_route(expense_id):
    """Delete an expense using its database ID."""

    delete_expense(expense_id)

    return redirect(url_for("home"))


@app.route("/chat", methods=["POST"])
def chat():
    """Send the user's message to the AI expense agent."""

    user_message = request.form["message"].strip()

    answer = run_agent(user_message)

    dashboard = get_dashboard_data()

    return render_template(
        "index.html",
        **dashboard,
        user_message="",
        agent_response=answer
    )


if __name__ == "__main__":
    app.run(debug=True)