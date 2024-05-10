from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from helpers import sortByID

db = SQLAlchemy()

# matches the functionality of the function I used before
def dbExecute(sqlCode, *args):
    result = None

    # If we only have the sql code, run it.
    # If we have multiple arguments, if we have one dict we can just pass it, otherwise, we need to change the ? to using a dict we create.
    if len(args) != 0:
        if type(args[0]) == dict:
            result = db.session.execute(text(sqlCode), args[0])
        else:
            d = {}
            for i in range(len(args)):
                sqlCode = sqlCode.replace("?", ":named" + str(i), 1)
                d["named" + str(i)] = args[i]
            result = db.session.execute(text(sqlCode), d)
    else:
        result = db.session.execute(text(sqlCode))

    try:
        # Get all rows. Will fail if was an insert statement which will trigger the except clause.
        # Converts array of rows where each row is an array to an array where rows are dicts to easily access specific columns
        keys = list(result.keys())
        rows = result.fetchall()
        toReturn = []
        for row in rows:
            obj = {}
            for i in range(len(keys)):
                obj[keys[i]] = row[i]
            toReturn.append(obj)

        return toReturn
    except Exception as e:
        db.session.commit()

def getObjectOfConferencesEachWithArrayOfItsChurches():
    churches = dbExecute("""SELECT c.*, 
                            con.name AS conferenceName,
                            con.id AS conferenceID
                            FROM Churches c, Conferences con
                            WHERE c.conferenceID = con.id;""")

    # Initialize an empty dictionary to store arrays of objects for each conference ID
    conferences = {}

    # Iterate over the objects array
    for church in churches:
        conference_id = church['conferenceID']
        
        # If the conference ID is not already a key in the dictionary, add it with an empty array
        if conference_id not in conferences:
            conferences[conference_id] = []
        
        # Append the object to the array corresponding to its conference ID
        conferences[conference_id].append(church)
    
    return conferences

def getChurchIdFromChurchAndConferenceName(conference, church):
    church = dbExecute("""SELECT c.id AS id
                            FROM Churches c, Conferences con
                            WHERE c.conferenceID = con.id 
                            AND c.name = ? AND con.name = ?;""", church, conference)
    if church:
        return church[0]["id"]
    else:
        return None
    
def getConferenceIdFromConferenceName(conference):
    conference = dbExecute("SELECT id FROM Conferences WHERE name = ?", conference)
    if conference:
        return conference[0]["id"]
    else:
        return None

def getSupportCallsWithOptionalFilters(filterType, filterID, month=None):
    """Function to get calls with optional filter.

    Args:
        filterType (str): Filter type. Accepted values are "none", "conference", "treasurer" or "agent".
        filterType (numeric str): ID to filter by
    """
    if filterType == "church":
        filterType = "ch.id"
    elif filterType == "conference":
        filterType = "con.id"
    elif filterType == "agent":
        filterType = "u.id"
    else:
        filterType = "''"

    if filterType == "''":
        filterID = ""
    if not month:
        month = ""

    calls = dbExecute(f"""SELECT sc.*, 
                        con.name AS conferenceName,
                        ch.name AS churchName,
                        u.username AS agentName,
                        t.name AS treasurerName,
                        t.phoneNumber AS treasurerPhone,
                        con.id AS conferenceID,
                        ch.id AS churchID
                        FROM SupportCalls sc, Conferences con, Churches ch, Treasurers t, users u
                        WHERE ch.conferenceID = con.id AND sc.treasurerID = t.id AND t.churchID = ch.id AND sc.agentID = u.id 
                        AND {filterType} = ? AND ("{month}" = "" OR sc.date LIKE "%{month}%");""", filterID)
    
    calls.sort(key=sortByID, reverse=True)

    return calls

def getSupportCallsTotalTimeWithOptionalFilters(filterType, filterID, month=None):
    """Function to get calls with optional filter.

    Args:
        filterType (str): Filter type. Accepted values are "none", "conference", "treasurer" or "agent".
        filterType (numeric str): ID to filter by
    """
    if filterType == "church":
        filterType = "ch.id"
    elif filterType == "conference":
        filterType = "con.id"
    elif filterType == "agent":
        filterType = "u.id"
    else:
        filterType = ""

    if filterType == "":
        filterID = ""
  
    sumTotalTime = dbExecute(f"""SELECT 
                        SUM(sc.totalTime) AS sumTotalTime
                        FROM SupportCalls sc, Conferences con, Churches ch, Treasurers t, users u
                        WHERE ch.conferenceID = con.id AND sc.treasurerID = t.id AND t.churchID = ch.id AND sc.agentID = u.id 
                        AND {filterType} = ? AND ("{month}" = "" OR sc.date LIKE "%{month}%");""", filterID)[0]["sumTotalTime"]
    if not sumTotalTime:
        sumTotalTime = 0
    return sumTotalTime

