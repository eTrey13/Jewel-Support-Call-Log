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



sql("DELETE FROM SupportCalls")
sql("DELETE FROM Treasurers")


sql("UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'SupportCalls'")
sql("UPDATE SQLITE_SEQUENCE SET seq = 0 WHERE name = 'Treasurers'")

sql(f"""INSERT INTO Treasurers (name, phoneNumber, churchID) VALUES 
('Lindomar Fuentes', '(978) 837-9554', 3778),
('Jesse Alli', '(234) 855-4764', 349),
('Annette', '(614) 302-3185', 330),
('Rosy Aldonate', '(917) 803-2032', 3727),
('Rosalinda Hernandez', '(603) 264-3909', 3789),
('Bonnie', '(909) 234-5144', 5557),
('LaTonya', '(614) 558-0580', 319),
('Teresa Strickland', '(615) 389-8225', 2728);
""")

sql(f"""INSERT INTO SupportCalls (treasurerID, agentID, date, startTime, endTime, totalTime, notes) VALUES 
(1, 1, '12-04-2024', '12:39', '13:01', 22, "Database & install supposedly corrupted by Windows update, sent new install & Feb backup"),
(1, 1, '12-04-2024', '16:17', '16:32', 15, "Emailed database backup, answered ?’s re backing up, set up backup to conf server, talked up ach transfer"),
(5, 1, '04-04-2024', '17:32', '18:00', 28, "Trouble with AG import. I think she didn’t complete the deposit and continued adding additional envelopes from another week. Not sure."),
(5, 1, '08-04-2024', '16:30', '17:04', 34, "English understanding issue"),
(5, 1, '22-04-2024', '14:17', '14:36', 19, "Needed to edit current deposit, know how to change bank account for deposit"),
(6, 1, '25-03-2024', '14:22', '14:35', 13, "Corrupted database"),
(6, 1, '31-03-2024', '16:11', '16:27', 16, "Database messed up again, giving error when reconciling. I asked for bank statement to duplicate error. It balanced w no error."),
(7, 1, '27-03-2024', '16:43', '17:11', 28, "Question re combining names, rolled date back to Jan so can enter checks (has been using QB for checks, Jewel for deposits)"),
(6, 1, '08-04-2024', '14:22', '14:34', 12, "Talked to Mom re upgrade issue, sent Universal 9.0 bc her database was already upgraded"),
(5, 1, '01-05-2024', '13:48', '16:10', 142, "Reconciliation trouble - remittance was $1 off, forgot another transaction, needed to upgrade, undoing rec caused Jewel bug of marking other transactions cleared that shouldn’t have been. Discovered fin rep is off from bank, although bank rec is ok."),
(8, 1, '07-05-2024', '13:42', '14:03', 21, "Beginning checking balance off, walked through month-end closing");
""")

# Close the connection when you're done
connection.commit()
connection.close()