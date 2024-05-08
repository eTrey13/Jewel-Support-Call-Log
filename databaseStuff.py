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



sql("""ALTER TABLE Treasurers
ADD otherContactInfo TEXT;""")


# Close the connection when you're done
connection.commit()
connection.close()