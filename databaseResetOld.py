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


sql("PRAGMA foreign_keys = ON;")


sql("DROP TABLE SupportCalls;")
sql("DROP TABLE Treasurers;")
sql("DROP TABLE Churches;")
sql("DROP TABLE Conferences;")
sql("DROP TABLE Users;")



sql("""-- Create the Conferences table
CREATE TABLE Conferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    supported INTEGER DEFAULT 1 CHECK (supported IN (0, 1)),
    eAdventistID TEXT UNIQUE
);
""")
sql("""-- Create the Churches table
CREATE TABLE Churches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conferenceID INTEGER NOT NULL,
    name TEXT,
    notes TEXT,
    eAdventistID TEXT UNIQUE,
    FOREIGN KEY (conferenceID) REFERENCES Conferences(id)
);
""")
sql("""-- Create the Treasurers table
CREATE TABLE Treasurers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    churchID INTEGER NOT NULL,
    name TEXT,
    phoneNumber TEXT,
    email TEXT,
    needSpanish INTEGER DEFAULT 0 CHECK (needSpanish IN (0, 1)),
    FOREIGN KEY (churchID) REFERENCES Churches(id)
);
""")
sql("""-- Create the SupportCalls table
CREATE TABLE SupportCalls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    treasurerID INTEGER NOT NULL,
    agentID INTEGER NOT NULL,
    date TEXT,
    startTime TEXT,
    endTime TEXT,
    totalTime TEXT,
    notes TEXT,
    visible INTEGER DEFAULT 1 CHECK (visible IN (0, 1)),
    FOREIGN KEY (treasurerID) REFERENCES Treasurers(id),
    FOREIGN KEY (agentID) REFERENCES Users(id)
);
""")
sql('''-- Create the Users table
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    hash VARCHAR(64) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email TEXT,
    admin INTEGER DEFAULT 0 CHECK (admin IN (0, 1)),
    phone TEXT
);
''')


conferences = ["Alaska Conference of SDA", "Alberta Conference", "Allegheny East Conference Corporation", "Allegheny West Conference", "Arizona Conference Corporation", "Arkansas-Louisiana Conference", "Bermuda Conference", "British Columbia Conference", "Carolina Conference, Inc.", "Central California Conference", "Central States Conference of SDA", "Chesapeake Conference of SDA", "Dakota Conference", "Florida Conference", "Georgia-Cumberland Conference", "Greater New York Conference of SDA", "Guam-Micronesia Mission", "Gulf States Conference of SDA", "Hawaii Conference", "Idaho Conference of SDA", "Illinois Conference", "Indiana Conference", "Iowa-Missouri Conference", "Kansas-Nebraska Conference", "Kentucky-Tennessee Conference", "Lake Region Conference", "Manitoba-Saskatchewan Conference", "Maritime Conf. of the SDA Church Inc.", "Michigan Conference", "Minnesota Conference", "Montana Conf of Seventh-day Adventists", "Mountain View Conference", "Nevada-Utah Conference", "New Jersey Conf of SDAs, Inc.", "New York Conference", "Northeastern Conference of SDA", "Northern California Conference of SDA", "Northern New England Conference", "Ohio Conference", "Oklahoma Conference", "Ontario Conference", "Oregon Conference of SDA", "Pennsylvania Conference", "Potomac Conference Corporation", "Quebec Conference", "Rocky Mountain Conference", "SDA Church in Newfoundland and Labrador", "South Atlantic Conference", "South Central Conference", "Southeastern California Conference", "Southeastern Conference", "Southern California Conference", "Southern New England Conference", "Southwest Region Conference", "Texas Conference", "Texico Conference", "Upper Columbia Conference of SDA", "Washington Conference of SDA", "Wisconsin Conference"]
for conference in conferences:
    sql(f"INSERT INTO Conferences (name) VALUES ('{conference}')")
churches1 = ["Anchorage Community SDA Church", "Anchorage Korean SDA Church", "Anchorage Northside SDA Church", "Anchorage Spanish SDA Church", "Arctic Seventh-day Adventist Church", "Craig SDA Church", "Delta Junction SDA Church", "Dillingham SDA Church", "Eagle River SDA Church", "Fairbanks SDA Church", "Gambell SDA Church", "Hillside O'Malley SDA Church", "Juneau SDA Church", "Ketchikan SDA Church", "Kodiak SDA Church", "Midnight Son SDA Church", "Nome SDA Church", "North Pole SDA Church", "Palmer SDA Church", "Samoan SDA Church", "Savoonga SDA Church", "Sitka SDA Church", "Sunshine SDA Church", "The Second Mile Adventist Church", "Tok SDA Church", "Valdez SDA Church", "Wasilla SDA Church", "Wrangell SDA Church"]
for church in churches1:
    sql(f"INSERT INTO Churches (name, conferenceID) VALUES (\"{church}\", 1)")
churches2 = ["Alpha & Omega SDA Church", "Beacon of Hope", "Berea SDA Church", "Berean SDA Church", "Berean SDA Church", "Bethany SDA Church", "Bethel SDA Church", "Bethel SDA Church", "Bethel SDA Church", "Bethesda SDA Church", "Blessed Hope SDA Church", "Calvary SDA Church", "Central SDA Church", "Cincinnati Central Hispanic", "Columbus All Nations SDA Church", "Columbus Brazilian SDA Church", "Dale Wright Memorial SDA Church", "Dayton's Church of SDA", "El Buen Pastor", "El Camino A Cristo SDA Church", "Emmanuel SDA Church", "Ephesus SDA Church", "Ethan Temple SDA Church", "Ethnan Temple", "Fruit of the Spirit SDA Church", "Glenville Present Truth SDA Church", "Gospel Tabernacle SDA Church", "Grace Community SDA Church", "Greater Faith SDA Church", "Greater New Hope Community SDA", "Hillcrest SDA Church", "Hillside SDA Church", "Hilltop Community Worship Center", "Hope Community SDA Church", "Iglesia Adventista Latina de Columbus", "La Esperanza", "Manantial de Vida Hispanic SDA", "Maranatha SDA Church", "Melrose SDA Church", "Miracle of Faith SDA Church", "Mount Zion SDA Church", "New Life SDA Church", "Ohio Central Korean SDA Church", "Park Street Seventh-day Adventist Church", "Parkwood Seventh-Day Adventist Church", "Philadelphie SDA Church", "Shiloh Cincinnati", "Shiloh SDA Church", "Smyrna SDA Church", "South Fountain Avenue SDA Church", "Southeast SDA Church", "Temple Emmanuel SDA Church", "Temple of Praise SDA Church", "Three Angels Message SDA Church", "Tobiah SDA Church", "Victory SDA Church", "Westside SDA Church"]
for church in churches2:
    sql(f"INSERT INTO Churches (name, conferenceID) VALUES (\"{church}\", 4)")
churches3 = ["Agape SDA Church of Richmond Hill", "Alfa & Omega SDA Church", "Amazing Grace SDA Church", "Amsterdam Hispanic SDA Church", "Antioch SDA Church", "Apocalipsis 14 Hispanic SDA Church", "Beacon Light Tabernacle SDA Church", "Ben-Emmanuel SDA Church", "Beraca SDA Church", "Berea SDA Church", "Berea SDA Church", "Beth Elohim SDA Church", "Bethanie French SDA Church", "Bethany SDA Church", "Bethel Hispanic SDA Church", "Bethel SDA Church", "Bethesda SDA Church", "Bethlehem SDA Worship Center", "Beulah SDA Church", "Blessed Hope SDA Church", "Breath of Life SDA Church", "Brewster Hispanic SDA Church", "Bridgeport Tabernacle SDA Church", "Brockton Hispanic SDA Church", "Brockton Portuguese SDA Church", "Brockton Temple SDA Church", "Bronx SDA Church", "Brooklyn Faith SDA Church", "Brooklyn Temple SDA Church", "Brownsville Seventh-day Adventist Church", "Buffalo Hispanic SDA Church", "Calvary First Nigerian SDA Church", "Calvary SDA Church", "Cambridge SDA Church", "Canaan SDA Church", "Canarsie SDA Church", "Capernaum SDA Church", "Capital City SDA Church", "Central Islip SDA Church", "Charity SDA Church", "Chelsea Hispanic SDA Church", "Christian Fellowship SDA Church", "City Tabernacle SDA Church", "Community Tabernacle of Praise SDA", "Community Worship Center SDA Church", "Coney Island SDA Church", "Cornerstone Hispanic SDA Church", "Cornerstone SDA Church", "Corona SDA Church", "Cypress Hills Hispanic SDA Church", "Danbury Hispanic SDA Church", "Danbury Luso-Brasileira SDA Church", "Dorchester Portuguese SDA Church", "East New York SDA Church", "Eben-Ezer French SDA Church", "Ebenezer SDA Church", "Eden SDA Church", "El Buen Pastor SDA Church", "El Faro Hispanic SDA Church", "El Siloe SDA Church", "Elim SDA Church", "Ellenville SDA Church", "Elmont Temple SDA Church", "Emmanuel French SDA Church", "Emmanuel SDA Church", "Emmanuel Temple SDA Church", "Emmaus SDA Church", "Ephese SDA Church", "Ephesus SDA Church", "Ephraim French SDA Church", "Esmirna Hispanic SDA Church", "Everett Hispanic SDA Church", "Faith SDA Church", "Faro de Luz SDA Church", "First Rochester Hispanic SDA Church", "First SDA Church of White Plains", "Flatbush SDA Church", "Friendship SDA Church", "Galilee SDA Church", "Gethsemane SDA Church", "Golgotha SDA Church", "Gordon Heights SDA Church", "Gosen SDA Church", "Goshen Temple SDA Church", "Hanson Place SDA Church", "Haverhill Hispanic SDA Church", "Hebron SDA Church", "Heritage SDA Church", "Hermon SDA Church", "Hope SDA Church", "Horeb SDA Church", "Hunts Point SDA Church", "Hyde Park SDA Church", "Immanuel SDA Church", "Indian Orchard SDA Church", "Jamaica Hispanic SDA Church", "Jamaica SDA Church", "Jerusalem Hispanic SDA Church", "Kerith SDA Church", "Kingsboro Temple SDA Church", "Kingston SDA Church", "Lawrence Hispanic SDA Church", "Le Phare SDA Church", "Lebanon SDA Church", "Lighthouse Tabernacle SDA Church", "Linden SDA Church", "Living Manna of Northeastern Conference", "Luz de Lawrence SDA Church", "Macedonia SDA Church", "Mahanaim SDA Church", "Majestic Heights SDA Church", "Mamre SDA Church", "Manchester Hispanic SDA Church", "Maranatha French SDA Church", "Maranatha Hispanic SDA Church", "Methuen SDA Church", "Mid-Hudson French SDA Church", "Mitspa French SDA Church", "Mont Des Oliviers SDA Church", "Monte Sinai Hispanic SDA Church", "Morija SDA Church", "Mount Carmel SDA Church", "Mount Moriah SDA Church", "Mount Sinai SDA Church", "Mount Vernon SDA Church", "Mount Zion SDA Church", "Mount of Blessing SDA Church", "Mount of Olives SDA Church", "Mt. Olive SDA Church", "New Bedford Hispanic SDA Church", "New Brighton Community SDA Church", "New Dimension SDA Church", "New Ebenezer SDA Church", "New England Portuguese SDA Church", "New Hope Fellowship SDA Church", "New Jerusalem SDA Church", "New Life SDA Church", "New Rochelle SDA Church", "Newburgh Tabernacle SDA Church", "Norwalk SDA Church", "Oasis Hill SDA Church", "Omega SDA Church", "Peekskill-Cortlandt SDA Church", "Philadelphie SDA Church", "Pioneer Memorial SDA Church", "Primera Hispanic SDA Church", "Providence Hispanic SDA Church", "Queensboro Temple SDA Church", "Real Truth SDA Church", "Riverdale Avenue SDA Church", "Rochester Outreach Community SDA Church", "Rogers Avenue SDA Church", "Salem Hispanic SDA Church", "Schilo French SDA Church", "Shalom SDA Church", "Sharon SDA Church", "Shekinah French SDA Church", "Shelter Rock SDA Church", "Shiloh SDA Church - Brooklyn", "Shiloh SDA Church - Springfield", "Sichem SDA Church", "Sinai French SDA Church", "Sion SDA Church", "Smyrne French SDA Church", "Solid Rock SDA Church", "South Brooklyn SDA Church", "South Ozone Park SDA Church", "Spring Valley SDA Church", "Springfield Hispanic SDA Church", "Staten Island SDA Church", "Stuyvesant Heights SDA Church", "Taunton Portuguese SDA Church", "Temple Salem SDA Church", "The First Rosedale SDA Church", "The River of Life SDA Church", "The Waymark SDA Church", "Three Angels Hispanic SDA Church", "Trinity Temple SDA Church", "Victory Fellowship Worship Center of SDA", "Voice of Hope SDA Church", "Waterbury Luso-Brasileira SDA Church", "Westbury Hispanic SDA Church", "Willis Avenue SDA Church"]
for church in churches3:
    sql(f"INSERT INTO Churches (name, conferenceID) VALUES (\"{church}\", 36)")


sql(f"""INSERT INTO Users (username, email, admin, hash, password) VALUES 
('mylam', 'myla@matus.biz', 0, '{generate_password_hash('password')}', 'password'),
('trey', 'treyobed@matus.biz', 1, '{generate_password_hash('qwerty')}', 'qwerty');
""")

sql(f"""INSERT INTO Treasurers (name, phoneNumber, churchID) VALUES 
('Lindomar Fuentes', '978-837-9554', 187),
('Jesse Alli', '234-855-4764', 80),
('Annette', '614-302-3185', 61),
('Rosy', '917-803-2032', 136),
('Rosalinda Hernandez', '603-264-3909', 198);
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