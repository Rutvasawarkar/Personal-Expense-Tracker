import sqlite3
from pathlib import Path
from datetime import date


# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Database folder
DATA_DIR = BASE_DIR / "data"

# Database file
DB_PATH = DATA_DIR / "expenses.db"


def get_connection():
    """Create and return a connection to the SQLite database."""

    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # Allows columns to be accessed using their names
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the expenses table if it doesn't already exist."""

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_expense(amount, category, description, expense_date):
    """Add a new expense to the database."""

    connection = get_connection()

    connection.execute("""
        INSERT INTO expenses (
            amount,
            category,
            description,
            date
        )
        VALUES (?, ?, ?, ?)
    """, (
        amount,
        category,
        description,
        expense_date
    ))

    connection.commit()
    connection.close()


def delete_expense(expense_id):
    """Delete an expense using its ID."""

    connection = get_connection()

    connection.execute("""
        DELETE FROM expenses
        WHERE id = ?
    """, (expense_id,))

    connection.commit()
    connection.close()


def get_all_expenses():
    """Return all expenses, newest first."""

    connection = get_connection()

    expenses = connection.execute("""
        SELECT
            id,
            amount,
            category,
            description,
            date
        FROM expenses
        ORDER BY date DESC, id DESC
    """).fetchall()

    connection.close()

    return expenses


def get_total_spending():
    """Return total spending across all expenses."""

    connection = get_connection()

    result = connection.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
    """).fetchone()

    connection.close()

    return result["total"]


def get_monthly_spending():
    """Return spending for the current month."""

    current_month = date.today().strftime("%Y-%m")

    connection = get_connection()

    result = connection.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE substr(date, 1, 7) = ?
    """, (current_month,)).fetchone()

    connection.close()

    return result["total"]


def get_transaction_count():
    """Return the total number of transactions."""

    connection = get_connection()

    result = connection.execute("""
        SELECT COUNT(*) AS count
        FROM expenses
    """).fetchone()

    connection.close()

    return result["count"]


def get_category_spending():
    """
    Return spending grouped by category for the current month.

    Results are sorted from highest spending to lowest spending.
    """

    current_month = date.today().strftime("%Y-%m")

    connection = get_connection()

    results = connection.execute("""
        SELECT
            category,
            COALESCE(SUM(amount), 0) AS total,
            COUNT(*) AS transactions
        FROM expenses
        WHERE substr(date, 1, 7) = ?
        GROUP BY category
        ORDER BY total DESC
    """, (current_month,)).fetchall()

    connection.close()

    return results


def get_spending_summary(category=None, period="all"):
    """
    Get total spending and transaction count.

    category:
        Food, Travel, Shopping, Bills, Entertainment,
        Education, Other, or None for all categories.

    period:
        all
        this_month
        today
    """

    # Normalize category values from the AI
    if category:
        normalized_category = category.strip().lower()

        if normalized_category in {
            "",
            "all",
            "all categories",
            "all category",
            "none",
            "null"
        }:
            category = None

        else:
            category_map = {
                "food": "Food",
                "travel": "Travel",
                "shopping": "Shopping",
                "bills": "Bills",
                "entertainment": "Entertainment",
                "education": "Education",
                "other": "Other"
            }

            category = category_map.get(
                normalized_category,
                category.strip()
            )

    connection = get_connection()

    conditions = []
    parameters = []

    # Category filter
    if category:
        conditions.append("category = ?")
        parameters.append(category)

    # Date filter
    if period == "this_month":

        current_month = date.today().strftime("%Y-%m")

        conditions.append("substr(date, 1, 7) = ?")
        parameters.append(current_month)

    elif period == "today":

        today = date.today().isoformat()

        conditions.append("date = ?")
        parameters.append(today)

    elif period != "all":

        period = "all"

    # Base query
    query = """
        SELECT
            COALESCE(SUM(amount), 0) AS total,
            COUNT(*) AS transactions
        FROM expenses
    """

    # Add conditions if needed
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    result = connection.execute(
        query,
        parameters
    ).fetchone()

    connection.close()

    return {
        "currency": "INR",
        "currency_symbol": "₹",
        "category": category or "All categories",
        "period": period,
        "total": result["total"],
        "transactions": result["transactions"]
    }