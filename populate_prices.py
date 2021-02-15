import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE) # connect to db

connection.row_factory = sqlite3.Row # I want sqlite3 objects to return from a query

cursor = connection.cursor() # cursor obj

cursor.execute("""
    SELECT id, symbol, name FROM stock
""")

rows = cursor.fetchall() # fetch price data and store Alpaca Market API data

# [row['symbol'] for row in rows] - DUPE
symbols = [] # start as empty and let it append
stock_dict = {}
for row in rows:
    symbol = row['symbol'] # looping over the rows
    symbols.append(symbol)
    stock_dict[symbol] = row['id'] # the value would be the number (1, 2, 3) of the id - look up table - look up the symbols and easiely save ids

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

chunk_size = 200 # out of 9000 assets
for i in range(0, len(symbols), chunk_size): # paginating - loop through 200 at a time
    print(i)
    print(i+chunk_size)
    symbol_chunk = symbols[i:i+chunk_size] # Chunk of symbols: 0 -> 200, 201 -> 400
    print(symbol_chunk)
    barsets = api.get_barset(symbol_chunk, 'day') # list of 200 symbols

    for symbol in barsets:
        print(f"processing symbol {symbol}")
        for bar in barsets[symbol]:
            stock_id = stock_dict[symbol] # stock_id == foreign key reference - get the stock id
            cursor.execute("""
                INSERT INTO stock_price (stock_id, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, bar.t.date(), bar.o, bar.h, bar.l, bar.c, bar.v)) # You can do subquery from db: SELECT id FROM stock WHERE *
            # stock_id = foreign key 

connection.commit()
