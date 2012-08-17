postgres-history-tables
=======================

This project contains a command-line utility, history-manager.py, that serves as
a thin wrapper for managing history tables for a postgres database. A history
table tracks all changes made to the table with which it is associated, keeping
all of the original table's columns and adding a timestamp and action taken
column. This allows one to easily track changes made to postgres tables in a
database.

Requirements
============

There are a few preliminary steps that you need to do before this script can
work. First, you need to (obviously) have postgres installed. Additionally, you
need the plperl package for postgres:

    sudo apt-get install postgresql-plperl-\<version_num\>

And you need to install it on the database. From the command line:

    createlang [connection options] plperl [dbname]

Or from psql, while logged into the database as a superuser:

    CREATE LANGUAGE plperl;

Finally, to configure the script, you need to change the value of the DB_ARGS
string to the command line args you would normally use with psql to connect to
your database (-U, -d flags are probably the minimum). Keep in mind that the
user you use needs to have function and trigger creation privileges on the
database.

Usage
=====

python history-manager.py [options]

History manager accepts five options:
\n-h: Display help
\n--enable tablename [table_name [...]]: Enable history logging for all args
\n--disable tablename [table_name [...]]: Disable history logging for all args
\n--disableall: Disable history logging for all tables in the
db
\n--dump table_name [table_name [...]]: Dump the history table for all args to
disk

How it works
============

Assuming you have passed it legal arguments, history-manager.py creates (or
replaces, if they already exist) four functions each time you run it, which are
contained in the sql files in this directory. It creates a function to log the
history for any table (log-history.sql), a function to register a trigger for
history logging on a given table (create-trigger.sql), a function to drop the
trigger for history logging on a given table (delete-trigger.sql), and a
function to drop the trigger for history logging on all tables in the database
(delete-all.sql).

The utility is basically just a thin wrapper around several psql command line
calls - it doesn't actually create a connection to your database, just calls
psql using the connection arguments you specify at the top of the file.

It should fail gracefully in most cases; in the worst case you will just get
some errors from postgres and nothing bad will happen (knock on wood).

Some random points of note: Enabling the logging of history does not actually
create the history table until the first action is logged. Once a history table
has been created, it will stay in the database and continue being written to.
Don't try to create a history table for an existing history table, or you will
get column errors (this is pointless anyway).

Very important: if you add a column to a table that is currently being logged
and the history table as already been created, YOU MUST ADD THIS COLUMN TO THE
HISTORY TABLE. You will be reminded of this any time you enable history logging
for a table. Deleting columns is not a big deal - they will simply be null in
all further history table entries. Changing the type of a column is more
complicated, and may require some sort of schema migration.

Special thanks to Thomas Liske (liske@ibh.de) for the original history logging
script, which I tweaked to allow for logging on individual tables.


