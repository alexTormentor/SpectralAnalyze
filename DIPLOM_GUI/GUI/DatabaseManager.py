from Modules import sqlite3


class DatabaseManager:
    def __init__(self, database_name):
        self.database_name = database_name

    def execute_query(self, query):
        conn = sqlite3.connect(self.database_name)
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data

    def fetch_receiver_data(self):
        query = "SELECT Type, Diaphr, Diameter, Resist, DarkResist, CoeffAmpl, Length, DarkProv, Width, SizePh, Delta, Power FROM Receiver"
        return self.execute_query(query)

    def fetch_plot_data(self):
        query = "SELECT type FROM Plots"
        return self.execute_query(query)
