--Deletes the trigger to log history for a given table
CREATE OR REPLACE FUNCTION history_delete_trigger(tname text) RETURNS void
    AS $$
    BEGIN
        EXECUTE 'DROP TRIGGER log_history ON ' || tname || ';';
    END;
$$
    LANGUAGE plpgsql;
