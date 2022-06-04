from databases import Database
from config import DB_URL
database = Database(DB_URL)
await database.connect()
query = "CREATE TABLE messages (id SERIAL PRIMARY KEY,telegram_id INTEGER NOT NULL,text text NOT NULL);"
await database.execute(query=query)