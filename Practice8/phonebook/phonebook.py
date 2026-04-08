import psycopg2
import csv
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def setup_database(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook_entries (
                entry_id SERIAL PRIMARY KEY,
                contact_name VARCHAR(150) NOT NULL,
                phone_number VARCHAR(50) NOT NULL
            )
        """)
        conn.commit()

def show_all(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM phonebook_entries ORDER BY entry_id")
        return cur.fetchall()

def add_from_csv(conn, file_path):
    with conn.cursor() as cur:
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                cur.execute(
                    "INSERT INTO phonebook_entries (contact_name, phone_number) VALUES (%s, %s)",
                    (row[0].strip(), row[1].strip())
                )
        conn.commit()

def add_entry(conn, name, phone):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO phonebook_entries (contact_name, phone_number) VALUES (%s, %s)",
            (name, phone)
        )
        conn.commit()

def update_entry(conn, search_term, new_value, update_type="name"):
    query = (
        "UPDATE phonebook_entries SET contact_name = %s WHERE phone_number = %s"
        if update_type == "name" else
        "UPDATE phonebook_entries SET phone_number = %s WHERE contact_name = %s"
    )
    with conn.cursor() as cur:
        cur.execute(query, (new_value, search_term))
        conn.commit()

def search_records(conn, filter_type, query):
    with conn.cursor() as cur:
        if filter_type == "name":
            cur.execute("SELECT * FROM phonebook_entries WHERE contact_name ILIKE %s", (f"%{query}%",))
        else:
            cur.execute("SELECT * FROM phonebook_entries WHERE phone_number LIKE %s", (f"{query}%",))
        return cur.fetchall()

def delete_record(conn, delete_type, value):
    column = "contact_name" if delete_type == "name" else "phone_number"
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM phonebook_entries WHERE {column} = %s", (value,))
        conn.commit()

# Practice 8
def search_by_pattern(conn, pattern):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_by_pattern(%s)", (pattern,))
        return cur.fetchall()
def upsert_contact(conn, name, phone):
    with conn.cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
        conn.commit()
def insert_many_users(conn, users_list):
    names = [user[0] for user in users_list]
    phones = [user[1] for user in users_list]
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM insert_many_users(%s, %s)", (names, phones))
        conn.commit()
        return cur.fetchall()
def get_paginated(conn, limit, offset):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_paginated(%s, %s)", (limit, offset))
        return cur.fetchall()
def delete_by_identifier(conn, identifier):
    with conn.cursor() as cur:
        cur.execute("CALL delete_by_identifier(%s)", (identifier,))
        conn.commit()
def main():
    conn = get_connection()
    setup_database(conn)
    
    while True:
        print("\n| 1. Show All \n| 2. CSV Import \n| 3. Manual Add \n| 4. Update Name \n| 5. Update Phone \n| 6. Search Name \n| 7. Search Prefix \n| 8. Delete Name \n| 9. Delete Phone \n| 10. Search By Pattern \n| 11. Upsert \n| 12. Insert Many \n| 13. Pagination \n| 14. Delete by Identifier \n| 0. Exit")
        choice = input("\nSelect option: ")
        if choice == "1":
            results = show_all(conn)
            for r in results: print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
        elif choice == "2":
            add_from_csv(conn, input("CSV path: "))
            print("Imported.")
        elif choice == "3":
            add_entry(conn, input("Name: "), input("Phone: "))
            print("Added.")
        elif choice == "4":
            update_entry(conn, input("Target phone: "), input("New name: "), "name")
        elif choice == "5":
            update_entry(conn, input("Target name: "), input("New phone: "), "phone")
        elif choice == "6":
            for r in search_records(conn, "name", input("Name query: ")): print(r)
        elif choice == "7":
            for r in search_records(conn, "prefix", input("Phone prefix: ")): print(r)
        elif choice == "8":
            delete_record(conn, "name", input("Name to delete: "))
        elif choice == "9":
            delete_record(conn, "phone", input("Phone to delete: "))
        elif choice == "10":
            resulting = search_by_pattern(conn, input("Enter the pattern: "))
            if resulting:
                for r in resulting:
                    print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
            else:
                print("Nothing found.")
        elif choice == "11":
            upsert_contact(conn, input("Enter the name: "), input("Enter the phone: "))
        elif choice == "12":
            users = []
            print("Enter the data(! to stop):")
            while True:
                name = input("Name: ")
                if name == '!': 
                    break
                phone = input("Phone: ")
                users.append((name, phone))
            
            if users:
                errors = insert_many_users(conn, users)
                if errors:
                    print("\n Incorrect data:")
                    for e in errors: 
                        print(f"Name: {e[0]}, Phone: {e[1]}")
                else:
                    print("No incorrect data.")
        elif choice == "13":
            result = get_paginated(conn, int(input("Enter limit: ")), int(input("Enter offset: ")))
            for r in result:
                print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
        elif choice == "14":
            delete_by_identifier(conn, input("Enter name or phone: "))
        elif choice == "0":
            conn.close()
            break
        else:
            print("Invalid.")
if __name__ == "__main__":
    main()