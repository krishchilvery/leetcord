import sqlite3 as sldb

class LeetcordClient:
    def __init__(self) -> None:
        self.con = sldb.connect('users.sqlite3')
        self.cur = self.con.cursor()
        self.create_guilds_table()
        self.create_channels_table()

    def create_channels_table(self):
        query = """CREATE TABLE IF NOT EXISTS channels(
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT,
            guild_id TEXT,
            time TIMESTAMP,
            subscribed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(guild_id) REFERENCES guilds(id) ON DELETE CASCADE
        )"""
        self.cur.execute(query)
        self.con.commit()
    
    def create_guilds_table(self):
        query = """CREATE TABLE IF NOT EXISTS guilds(
            id TEXT NOT NULL PRIMARY KEY,
            name TEXT,
            added_on DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
        self.cur.execute(query)
        self.con.commit()
    
    def add_guild(self, id, name):
        query = "INSERT OR REPLACE into guilds (id, name) VALUES (?, ?)"
        self.cur.execute(query, (id, name))
        self.con.commit()
    
    def delete_guild(self, id):
        query = f'DELETE FROM guilds WHERE id={id}'
        self.cur.execute(query)
        self.con.commit()

    def add_channel(self, id, name, guild_id, time):
        query = "INSERT OR REPLACE into channels (id, name, guild_id, time) VALUES (?, ?, ?, ?)"
        self.cur.execute(query, (id, name, guild_id, time))
        self.con.commit()
    
    def delete_channel(self, id):
        query = f'DELETE FROM channels WHERE id={id}'
        self.cur.execute(query)
        self.con.commit()
    
    def get_all_channels(self):
        query = "SELECT * FROM channels"
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data
    
    def get_channels_with_time(self, time):
        query = f'SELECT * FROM channels where time="{time}"'
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data
    
# https://discord.com/api/oauth2/authorize?client_id=943537860726906901&permissions=137439439952&scope=bot

if __name__=="__main__":
    ac = LeetcordClient()
    import datetime
    time = datetime.datetime(year=2020, month=1, day=1, hour=5, minute=0)
    # time = datetime.datetime.now()
    # time = "2020-01-01 05:00:00"
    data = ac.get_channels_with_time(time)
    print(data)