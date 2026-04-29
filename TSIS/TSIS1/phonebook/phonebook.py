import psycopg2
import csv
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
import json
from datetime import date, datetime

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
def setup_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER REFERENCES phonebook_entries(entry_id) ON DELETE CASCADE,
                phone VARCHAR(20) NOT NULL,
                type VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                 id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            )
        """)
        conn.commit()
def show_all(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM phonebook_entries ORDER BY entry_id")
        return cur.fetchall()
    
def export_to_json(conn, filename="contacts.json"):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT pe.entry_id, pe.contact_name, pe.phone_number, pe.email, pe.birthday, g.name
            FROM phonebook_entries pe
            LEFT JOIN groups g ON pe.group_id = g.id
        """)
        entries = cur.fetchall()

        cur.execute("SELECT contact_id, phone, type FROM phones")
        phones_data = cur.fetchall()
        phones_by_contact = {}
        for p in phones_data:
            cid, num, ptype = p
            if cid not in phones_by_contact:
                phones_by_contact[cid] = []
            phones_by_contact[cid].append({"phone": num, "type": ptype})
        contacts = []
        for row in entries:
            eid, name, main_phone, email, bday, group_name = row
            contacts.append({
                "name": name,
                "main_phone": main_phone,
                "email": email,
                "birthday": bday,
                "group": group_name,
                "additional_phones": phones_by_contact.get(eid, [])
            })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4, default=str)
    print(f"Exported to {filename}.")
def import_from_json(conn, filename="contacts.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print("JSON file not found.")
        return

    with conn.cursor() as cur:
        for contact in contacts:
            name = contact.get("name")
            main_phone = contact.get("main_phone")
            email = contact.get("email")
            bday = contact.get("birthday")
            group_name = contact.get("group")
            add_phones = contact.get("additional_phones", [])
            
            cur.execute("SELECT entry_id FROM phonebook_entries WHERE contact_name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                choice = input(f"Contact '{name}' already exists. (S)kip or (O)verwrite? ").strip().upper()
                if choice == 'S':
                    continue
                elif choice == 'O':
                    entry_id = existing[0]
                    
                    group_id = None
                    if group_name:
                        cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (group_name,))
                        grp = cur.fetchone()
                        group_id = grp[0] if grp else cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,)) or cur.fetchone()[0]

                    cur.execute("""
                        UPDATE phonebook_entries
                        SET phone_number = %s, email = %s, birthday = %s, group_id = %s
                        WHERE entry_id = %s
                    """, (main_phone, email, bday, group_id, entry_id))

                    cur.execute("DELETE FROM phones WHERE contact_id = %s", (entry_id,))
                    for p in add_phones:
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                    (entry_id, p.get("phone"), p.get("type")))
            else:
                group_id = None
                if group_name:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (group_name,))
                    grp = cur.fetchone()
                    group_id = grp[0] if grp else cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,)) or cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO phonebook_entries (contact_name, phone_number, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s) RETURNING entry_id
                """, (name, main_phone, email, bday, group_id))
                
                new_id = cur.fetchone()[0]
                for p in add_phones:
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (new_id, p.get("phone"), p.get("type")))
        
        conn.commit()
        print("JSON import complete.")
def add_from_csv(conn, file_path):
    with conn.cursor() as cur:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                if len(row) < 6:
                    continue                                
                name, phone, email, bday, group_name, phone_type = [item.strip() for item in row]
                email = email if email else None
                bday = bday if bday else None
                group_name = group_name if group_name else None
                phone_type = phone_type if phone_type else None
                group_id = None
                if group_name:
                    cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (group_name,))
                    grp_res = cur.fetchone()
                    if grp_res:
                        group_id = grp_res[0]
                    else:
                        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                        group_id = cur.fetchone()[0]

                cur.execute("""
                    INSERT INTO phonebook_entries (contact_name, phone_number, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s, %s) RETURNING entry_id
                """, (name, phone, email, bday, group_id))
                
                entry_id = cur.fetchone()[0]

                if phone_type:
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (entry_id, phone, phone_type)
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

def filter_by_group(conn, group):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM phonebook_entries WHERE group_id = %s", (group,))
        return cur.fetchall()
def search_by_email(conn, target):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM phonebook_entries WHERE email LIKE %s", (f"%{target}%",))
        return cur.fetchall()
def sort_by_input(conn, target):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM phonebook_entries ORDER BY {target}")
        return cur.fetchall()
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
def add_additional_phone(conn, contact_name, phone, phone_type):
    with conn.cursor() as cur:
        try:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, phone_type))
            conn.commit()
            print(f"Success: Added {phone_type} phone ({phone}) to '{contact_name}'.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e.pgerror}")

def assign_to_group(conn, contact_name, group_name):
    with conn.cursor() as cur:
        try:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
            conn.commit()
            print(f"Success: Moved '{contact_name}' to group '{group_name}'.")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e.pgerror}")

def search_all_fields(conn, query_string):
    with conn.cursor() as cur:
        try:
            cur.execute("SELECT * FROM search_contacts(%s)", (query_string,))
            results = cur.fetchall()
            
            if not results:
                print(f"No contacts matched the query: '{query_string}'")
            else:
                print(f"--- Search Results for '{query_string}' ---")
                for r in results:
                    print(f"ID: {r[0]} | Name: {r[1]} | Main Phone: {r[2]} | Email: {r[3]} | Birthday: {r[4]} | Group ID: {r[5]}")
            
            return results
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e.pgerror}")
            return []
def main():
    conn = get_connection()
    setup_database(conn)
    setup_table(conn)
    while True:
        print("\n| 1. Show All \n| 2. CSV Import \n| 3. Manual Add \n| 4. Update Name \n| 5. Update Phone \n| 6. Search Name \n| 7. Search Prefix \n| 8. Delete Name \n| 9. Delete Phone \n| 10. Search By Pattern \n| 11. Upsert \n| 12. Insert Many \n| 13. Pagination \n| 14. Delete by Identifier \n| 15. Select by group \n| 16. Search by email \n| 17. Sort By Input \n| 0. Exit")
        choice = input("\nSelect option: ")
        if choice == "1":
            results = show_all(conn)
            for r in results: print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]} | Email: {r[3]} | Birthday: {r[4]} | Group Id: {r[5]}")
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
            
            limit = int(input("Enter limit: "))
            offset = int(input("Enter offset "))
            result = get_paginated(conn, limit, offset)
            for r in result:
                print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
            while True: 
                navigation = input("next/prev/quit: ").strip().lower()
                if navigation == "next":
                    limit += 1
                    offset += 1
                    result = get_paginated(conn, limit,offset)
                    for r in result:
                        print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
                elif navigation == "prev":
                    if limit > 0 and offset > 0:
                        limit -= 1
                        offset -= 1
                    result = get_paginated(conn, limit, offset)
                    for r in result:
                        print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")
                else:
                    break


        elif choice == "14":
            delete_by_identifier(conn, input("Enter name or phone: "))
        elif choice == "15":
            selected_group_id = int(input("Enter the group id:"))
            results = filter_by_group(conn, selected_group_id)
            for r in results: 
                print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]} | Email: {r[3]} | Birthday: {r[4]} | Group Id: {r[5]}")
        elif choice == "16":
            target_email = input("Enter the target email: ")
            results = search_by_email(conn, target_email)
            for r in results: 
                print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]} | Email: {r[3]} | Birthday: {r[4]} | Group Id: {r[5]}")
        elif choice == "17":
            target = input("Enter sorting target: ")
            results = sort_by_input(conn, target)
            for r in results: 
                print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]} | Email: {r[3]} | Birthday: {r[4]} | Group Id: {r[5]}")
        elif choice == "18":
            file_name = input("Enter file name:")
            export_to_json(conn, file_name)
        elif choice == "19":
            contact_name = input("Enter the exact contact name: ")
            phone = input("Enter the new phone number: ")
            phone_type = input("Enter the phone type (home, work, mobile): ").lower()
            
            if phone_type not in ['home', 'work', 'mobile']:
                print("Invalid type. Must be 'home', 'work', or 'mobile'.")
            else:
                add_additional_phone(conn, contact_name, phone, phone_type)

        elif choice == "20":
            contact_name = input("Enter the exact contact name: ")
            group_name = input("Enter the target group name: ")
            assign_to_group(conn, contact_name, group_name)

        elif choice == "21":
            query_string = input("Enter search term (name, phone, or email): ")
            search_all_fields(conn, query_string)
        elif choice == "0":
            conn.close()
            break
        else:
            print("Invalid.")
if __name__ == "__main__":
    main()