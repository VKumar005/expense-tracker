import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Main Page (Dashboard) ---
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY date DESC")
    all_expenses = c.fetchall()
    
    # 1. Determine Date (User Selection or Today)
    selected_date = request.args.get('date') 
    
    if not selected_date:
        selected_date = datetime.now().strftime('%Y-%m-%d')
    
    # Calculate derived month and year
    selected_month = selected_date[:7] 
    selected_year = selected_date[:4]

    # Initialize variables
    total_expense = 0
    daily_expense = 0
    monthly_expense = 0
    yearly_expense = 0
    
    daily_dict = {}
    monthly_dict = {}
    yearly_dict = {}

    for row in all_expenses:
        expense_date = row[1]
        category = row[2]
        amount = row[4]
        
        total_expense += amount
        
        # 2. DAILY Logic (Matches selected date)
        if expense_date == selected_date:
            daily_expense += amount
            if category in daily_dict:
                daily_dict[category] += amount
            else:
                daily_dict[category] = amount

        # 3. MONTHLY Logic (Matches Month of selected date)
        if expense_date.startswith(selected_month):
            monthly_expense += amount
            if category in monthly_dict:
                monthly_dict[category] += amount
            else:
                monthly_dict[category] = amount

        # 4. YEARLY Logic (Matches Year of selected date)
        if expense_date.startswith(selected_year):
            yearly_expense += amount
            if category in yearly_dict:
                yearly_dict[category] += amount
            else:
                yearly_dict[category] = amount

    conn.close()
    
    return render_template('index.html', 
                           expenses=all_expenses, 
                           total=total_expense, 
                           daily=daily_expense, 
                           monthly=monthly_expense, 
                           yearly=yearly_expense,
                           daily_labels=list(daily_dict.keys()),
                           daily_values=list(daily_dict.values()),
                           monthly_labels=list(monthly_dict.keys()),
                           monthly_values=list(monthly_dict.values()),
                           yearly_labels=list(yearly_dict.keys()),
                           yearly_values=list(yearly_dict.values()),
                           selected_date=selected_date 
                           )

# --- Add Expense Route ---
@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    category = request.form['category']
    description = request.form['description']
    amount = request.form['amount']
    
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
              (date, category, description, amount))
    conn.commit()
    conn.close()
    return redirect(f'/?date={date}')

# --- Delete Expense Route ---
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    # host='0.0.0.0' allows access from mobile phone on same Wi-Fi
    app.run(debug=True, host='0.0.0.0')