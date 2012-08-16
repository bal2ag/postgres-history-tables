--
-- This trigger functions can be bound on any table. It creates a new table
-- history.<SCHEMA>_<TABLENAME> with two additional columns:
--
--  hist_ts timestamp DEFAULT NOW()
--  hist_op character(6)
--
-- "hist_ts" is the timestamp when the change has been occured. "hist_op"
-- is the DB operation which has caused the trigger (INSERT, UPDATE, DELETE).
--
-- The code tries to use some caching, when the original table
-- has been changed, ensure you change the log table accordently
-- and kill any running sessions.
--
-- 2009/08/06 - Thomas Liske <liske@ibh.de>
-- 
-- Changes made by Bryan Landau (bal2ag@virginia.edu) to allow for per-table
-- enabling of history logging
CREATE OR REPLACE FUNCTION log_history() RETURNS trigger
    AS $$

    my $htblname = $_TD->{table_name}.'_hist';

    unless(defined($_SHARED{'pl_log_history_texists'})) {
        elog(DEBUG, "Preparing 'pl_log_history_texists'.");

        $_SHARED{'pl_log_history_texists'} =
         spi_prepare("SELECT schemaname FROM pg_tables WHERE tablename=\$1", 'text')
    }

    my $sth = spi_query_prepared($_SHARED{'pl_log_history_texists'}, $htblname);
    unless(defined(spi_fetchrow($sth))) {
        elog(NOTICE, "Creating history table for '$_TD->{table_name}'.");

        spi_exec_query("CREATE TABLE $htblname (LIKE $_TD->{table_name});");
        spi_exec_query("ALTER TABLE $htblname ADD COLUMN hist_ts timestamp DEFAULT NOW();");
        spi_exec_query("ALTER TABLE $htblname ADD COLUMN hist_op character(6);");
    }

    my $use = 'new';
    $use = 'old' if($_TD->{event} eq 'DELETE');

    my $plshared = "pl_log_history_insert#$_TD->{table_name}";
    unless(defined($_SHARED{$plshared})) {
        elog(NOTICE, "Preparing '$plshared'.");

        $rv = spi_exec_query('SELECT a.attname,pg_catalog.format_type(a.atttypid,a.atttypmod) AS atttype FROM '.
                             'pg_catalog.pg_attribute a WHERE '.
                             'a.attnum>0 AND NOT a.attisdropped AND a.attrelid=('.
                             ' SELECT c.oid FROM pg_catalog.pg_class c LEFT JOIN'.
                             ' pg_catalog.pg_namespace n ON n.oid = c.relnamespace'.
                             " WHERE c.relname = '$_TD->{table_name}' AND n.nspname = '$_TD->{table_schema}' AND".
                             ' pg_catalog.pg_table_is_visible(c.oid));');

        my @colnames;
        my @colparams;
        my @coltypes;
        my $i = 1;
        foreach my $row (@{$rv->{rows}}) {
            push(@colnames, $row->{attname});
            push(@colparams, '$'.$i);
            push(@coltypes, $row->{atttype});
            $i++;
        }
        push(@colnames, 'hist_op');
        push(@colparams, '$'.$i);
        push(@coltypes, 'character(6)');
        my $query = "INSERT INTO $htblname (\"";
        $query .= join('","', @colnames);
        $query .= '") VALUES (';
        $query .= join(',', @colparams);
        $query .= ');';

        $_SHARED{$plshared} = spi_prepare($query, @coltypes);
        $_SHARED{$plshared."#names"} = \@colnames;
    }

    if(defined($_SHARED{$plshared})) {
        $_TD->{$use}{hist_op} = $_TD->{event};
        my @cols;
        foreach my $col (@{$_SHARED{$plshared."#names"}}) {
            push(@cols, $_TD->{$use}{$col});
        }

        spi_exec_prepared($_SHARED{$plshared}, @cols);
    }
    else {
        elog(WARNING, 'Could not log history due plan is undefined!');
    }

    return;
$$
    LANGUAGE plperl;
