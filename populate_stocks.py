import sqlite3, config
import alpaca_trade_api as tradeapi

connection = sqlite3.connect(config.DB_FILE)

connection.row_factory = sqlite3.Row # query, it should return as a sqlite obj

cursor = connection.cursor() # obj to select all stocks currently available

# cursor.execute('DELETE FROM stock') 

# quiery to see which stocks are already in db
cursor.execute("""
	SELECT symbol, name FROM stock
""")

# cron job for scheduleing
rows = cursor.fetchall()

symbols = [row['symbol'] for row in rows] # looping over the row list and get a list of symbols

# this is how you create an Alpaca API client: API KEY + API SECRET
api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, base_url=config.API_URL)

assets = api.list_assets() # API method - will get a list of assets symbols - updated by Alpaca

# db table with stocks - call the ALPACA API
for asset in assets:
	try:
		if asset.status == 'active' and asset.tradable and asset.symbol not in symbols:  # filtered out all inactive and untradable assets
			print(f"Added a new stock {asset.symbol} {asset.name}")
			cursor.execute("INSERT INTO stock (symbol, name, exchange) VALUES (?, ?, ?)", (asset.symbol, asset.name, asset.exchange))
	except Exception as e:
		print(asset.symbol)
		print(e)

connection.commit()

