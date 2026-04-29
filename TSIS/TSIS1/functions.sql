CREATE OR REPLACE FUNCTION search_by_pattern(pattern VARCHAR)
RETURNS TABLE(entry_id INT, contact_name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.entry_id, p.contact_name, p.phone_number 
    FROM phonebook_entries p
    WHERE p.contact_name ILIKE '%' || pattern || '%' 
       OR p.phone_number ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook_entries WHERE contact_name = p_name) THEN
        UPDATE phonebook_entries 
        SET phone_number = p_phone 
        WHERE contact_name = p_name;
    ELSE
        INSERT INTO phonebook_entries (contact_name, phone_number) 
        VALUES (p_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION insert_many_users(p_names VARCHAR[], p_phones VARCHAR[])
RETURNS TABLE(incorrect_name VARCHAR, incorrect_phone VARCHAR) AS $$
DECLARE
    i INT;
    v_name VARCHAR;
    v_phone VARCHAR;
BEGIN
    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];
        IF v_phone ~ '^\+?[0-9]{5,}$' THEN
            INSERT INTO phonebook_entries (contact_name, phone_number) 
            VALUES (v_name, v_phone);
        ELSE
            incorrect_name := v_name;
            incorrect_phone := v_phone;
            RETURN NEXT;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(entry_id INT, contact_name VARCHAR, phone_number VARCHAR) AS $$
BEGIN
    RETURN QUERY 
    SELECT p.entry_id, p.contact_name, p.phone_number 
    FROM phonebook_entries p
    ORDER BY p.entry_id
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_by_identifier(p_identifier VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook_entries 
    WHERE contact_name = p_identifier OR phone_number = p_identifier;
END;
$$;


CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN

    SELECT entry_id INTO v_contact_id
    FROM phonebook_entries
    WHERE contact_name = p_contact_name;


    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;



CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_group_id INTEGER;
BEGIN

    SELECT id INTO v_group_id 
    FROM groups 
    WHERE name = p_group_name;


    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) 
        VALUES (p_group_name) 
        RETURNING id INTO v_group_id;
    END IF;


    UPDATE phonebook_entries
    SET group_id = v_group_id
    WHERE contact_name = p_contact_name;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;
END;
$$;



CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS SETOF phonebook_entries
LANGUAGE plpgsql
AS $$
BEGIN
 
    RETURN QUERY
    SELECT DISTINCT pe.*
    FROM phonebook_entries pe
    LEFT JOIN phones p ON pe.entry_id = p.contact_id
    WHERE pe.contact_name ~* p_query      
       OR pe.phone_number ~* p_query
       OR pe.email ~* p_query
       OR p.phone ~* p_query;
END;
$$;