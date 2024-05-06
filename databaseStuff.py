import os
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash


db_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

# Create the engine
engine = create_engine(f'sqlite:///{db_file_path}')  # Set echo to True for debugging


# Create a connection
connection = engine.connect()

# Execute raw SQL queries
def sql(code, *args):
    for arg in args:
        if isinstance(arg, str):
            if arg == "":
                code = code.replace("?", "Null", 1)
            else:
                code = code.replace("?", "'" + arg + "'", 1)
        elif isinstance(arg, int):
            code = code.replace("?", str(arg), 1)
            #print(arg)
        else:
            print(arg, type(arg))
    return connection.execute(text(code))



sql(f"""INSERT INTO Users (username, email, admin, hash, password) VALUES 
('mylam', 'myla@matus.biz', 0, '{generate_password_hash('password')}', 'password'),
('trey', 'treyobed@matus.biz', 1, '{generate_password_hash('qwerty')}', 'qwerty');
""")

sql(f"""INSERT INTO Treasurers (name, phoneNumber, churchID) VALUES 
('Lindomar Fuentes', '978-837-9554', 3778),
('Jesse Alli', '234-855-4764', 349),
('Annette', '614-302-3185', 330),
('Rosy', '917-803-2032', 3727),
('Rosalinda Hernandez', '603-264-3909', 3789);
""")

sql(f"""INSERT INTO SupportCalls (treasurerID, agentID, date, startTime, endTime, totalTime, notes) VALUES 
(1, 1, '12-4-2024', '12:39', '13:01', 22, "Database & install supposedly corrupted by Windows update, sent new install & Feb backup"),
(1, 1, '12-4-2024', '16:17', '16:32', 15, "Emailed database backup, answered ?’s re backing up, set up backup to conf server, talked up ach transfer"),
(5, 1, '4-4-2024', '17:32', '18:00', 28, "Trouble with AG import. I think she didn’t complete the deposit and continued adding additional envelopes from another week. Not sure."),
(5, 1, '8-4-2024', '16:30', '17:04', 34, "English understanding issue"),
(5, 1, '22-4-2024', '14:17', '14:36', 19, "Needed to edit current deposit, know how to change bank account for deposit");
""")


# Close the connection when you're done
connection.commit()
connection.close()