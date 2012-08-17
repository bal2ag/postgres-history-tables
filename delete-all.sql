--Deletes history logging triggers for all tables
CREATE OR REPLACE FUNCTION history_delete_all() RETURNS void
    AS $$
    DECLARE
        r RECORD;
    BEGIN
        FOR r IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP
            EXECUTE 'DROP TRIGGER IF EXISTS log_history ON ' || r.table_name || ';';
        END LOOP;
    END;
$$
    LANGUAGE plpgsql;
