--Creates a trigger to log history for a given table
CREATE OR REPLACE FUNCTION history_create_trigger(tname text) RETURNS void
    AS $$
    BEGIN
        EXECUTE 'CREATE TRIGGER log_history AFTER INSERT OR UPDATE OR DELETE ON ' || tname || ' FOR EACH ROW EXECUTE PROCEDURE log_history();';
    END;
$$
    LANGUAGE plpgsql;
