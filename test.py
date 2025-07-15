from tinydb import Query, TinyDB


db_groups = TinyDB("db/groups.json")
username = 'jsrujan'
room_id = '53410313-3a45-48e2-ac4f-744c135d62a7'
db = Query()
check_name = db_groups.search(
    (db.room_id == room_id)
)

users = check_name[0]

if username in users['group_members']:
    print("Exists")
