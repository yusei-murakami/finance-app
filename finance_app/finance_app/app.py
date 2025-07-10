from flask import Flask, render_template, request, redirect
import csv
import os
from datetime import datetime, timedelta
import yfinance as yf

app = Flask(__name__)

DATA_DIR = "data"
EXPENSE_FILE = os.path.join(DATA_DIR, "income_expense.csv")
INVEST_FILE = os.path.join(DATA_DIR, "investment.csv")

# 初期化処理
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(EXPENSE_FILE):
    with open(EXPENSE_FILE, "w", encoding="utf-8") as f:
        f.write("date,type,category,amount\n")
if not os.path.exists(INVEST_FILE):
    with open(INVEST_FILE, "w", encoding="utf-8") as f:
        f.write("date,symbol,amount\n")

def read_csv(filename):
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(filename, row):
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)

def overwrite_csv(filename, rows, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

@app.route("/")
def index():
    income_expense = read_csv(EXPENSE_FILE)
    investments = read_csv(INVEST_FILE)
    return render_template("index.html", income_expense=income_expense, investments=investments)

@app.route("/add", methods=["POST"])
def add():
    row = {
        "date": request.form["date"],
        "type": request.form["type"],
        "category": request.form["category"],
        "amount": request.form["amount"]
    }
    write_csv(EXPENSE_FILE, row)
    return redirect("/")

@app.route("/add_investment", methods=["POST"])
def add_investment():
    row = {
        "date": request.form["date"],
        "symbol": request.form["symbol"],
        "amount": request.form["amount"]
    }
    write_csv(INVEST_FILE, row)
    return redirect("/")

@app.route("/delete_income_expense/<int:index>")
def delete_income_expense(index):
    items = read_csv(EXPENSE_FILE)
    if 0 < index <= len(items):
        items.pop(index - 1)
        overwrite_csv(EXPENSE_FILE, items, ["date", "type", "category", "amount"])
    return redirect("/")

@app.route("/delete_investment/<int:index>")
def delete_investment(index):
    items = read_csv(INVEST_FILE)
    if 0 < index <= len(items):
        items.pop(index - 1)
        overwrite_csv(INVEST_FILE, items, ["date", "symbol", "amount"])
    return redirect("/")

@app.route("/stock/<symbol>")
def stock(symbol):
    try:
        end = datetime.today()
        start = end - timedelta(days=30)
        df = yf.download(symbol, start=start, end=end)
        dates = df.index.strftime("%Y-%m-%d").tolist()
        prices = df["Close"].tolist()
    except Exception as e:
        dates, prices = [], []
    return render_template("stock.html", symbol=symbol, dates=dates, prices=prices)

if __name__ == "__main__":
    app.run(debug=True)
