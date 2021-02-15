# Web app UI
import sqlite3, config
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from datetime import date

app = FastAPI()
templates = Jinja2Templates(directory="templates") # configuring HTML templates dirctory - display logic

@app.get("/") # all get request will be routed to the index function - / route is the base route - / decorator
def index(request: Request):
    stock_filter = request.query_params.get('filter', False)

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row  # it should return as a sqlite obj - row factory
    cursor = connection.cursor()  # obj to select all stocks currently available

    # to see which stocks are already in db
    if stock_filter == 'new_closing_highs':
        cursor.execute("""
        SELECT * FROM (
            SELECT symbol, name, stock_id, max(close), date
            FROM stock_price JOIN stock ON stock.id = stock_price.stock_id
            GROUP BY stock_id
            ORDER BY symbol
        ) WHERE date = ?
        """, (date.today().isoformat(),)) 
    else:
        cursor.execute("""
            SELECT id, symbol, name FROM stock ORDER BY symbol
        """)

    rows = cursor.fetchall()  # cron job for scheduleing

    return templates.TemplateResponse("index.html", {"request": request, "stocks": rows}) # this accepts a dictionary

@app.get("/stock/{symbol}")
def stock_detail(request: Request, symbol):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row  # it should return as a sqlite obj
    cursor = connection.cursor()  # obj to select all stocks currently available

    # to see which stocks are already in db
    cursor.execute("""
        SELECT id, symbol, name FROM stock WHERE symbol = ? 
    """, (symbol,))

    row = cursor.fetchone()  # cron job for scheduleing

    cursor.execute("""
        SELECT * FROM stock_price WHERE stock_id = ? ORDER BY date DESC
    """, (row['id'],))

    prices = cursor.fetchall()

    return templates.TemplateResponse("stock_detail.html", {"request": request, "stock": row, "bars": prices})
