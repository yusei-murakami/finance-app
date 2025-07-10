from flask import Flask, render_template, request, redirect
import os
import sqlite3
from collections import defaultdict
import json

app = Flask(__name__)

# 必要なフォルダを自動作成
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# DB初期化
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY, date TEXT, amount INTEGER, category TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS investments (id INTEGER PRIMARY KEY, date TEXT, amount INTEGER)")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    # 収支データ読み込み
    c.execute("SELECT date, amount, category FROM transactions")
    transactions = c.fetchall()

    # 投資データ読み込み
    c.execute("SELECT date, amount FROM investments")
    investments = c.fetchall()
    conn.close()

    # 月別集計
    monthly_totals = defaultdict(int)
    for date, amount, _ in transactions:
        month = date[:7]
        monthly_totals[month] += amount

    bar_data = {
        "labels": list(monthly_totals.keys()),
        "datasets": [{
            "label": "月別収支",
            "data": list(monthly_totals.values()),
            "backgroundColor": "rgba(75, 192, 192, 0.6)"
        }]
    }

    # カテゴリ別支出
    category_totals = defaultdict(int)
    for _, amount, category in transactions:
        if amount < 0:
            category_totals[category] += -amount

    pie_data = {
        "labels": list(category_totals.keys()),
        "datasets": [{
            "data": list(category_totals.values()),
            "backgroundColor": [
                "red", "orange", "yellow", "green", "blue", "purple", "gray", "pink"
            ]
        }]
    }

    # 投資履歴
    investments.sort()
    dates = [d for d, _ in investments]
    amounts = [a for _, a in investments]
    line_data = {
        "labels": dates,
        "datasets": [{
            "label": "投資額",
            "data": amounts,
            "borderColor": "blue",
            "fill": False
        }]
    }

    return render_template("index.html", bar_data=json.dumps(bar_data),
                           pie_data=json.dumps(pie_data), line_data=json.dumps(line_data))

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    date = request.form["date"]
    amount = int(request.form["amount"])
    category = request.form["category"]
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, amount, category) VALUES (?, ?, ?)", (date, amount, category))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add_investment", methods=["POST"])
def add_investment():
    date = request.form["date"]
    amount = int(request.form["amount"])
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("INSERT INTO investments (date, amount) VALUES (?, ?)", (date, amount))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
