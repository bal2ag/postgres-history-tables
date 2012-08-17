import os
import argparse

#How should the psql command line calls connect to the database?
#Example: '-U s2s -d s2sdb'
DB_ARGS=''

#Initialize the functions necessary for this script to work (see below)
def init_functions():
    os.system('psql '+DB_ARGS+' -f log-history.sql')
    os.system('psql '+DB_ARGS+' -f create-trigger.sql')
    os.system('psql '+DB_ARGS+' -f delete-trigger.sql')

#Enable history logging for the given table by creating the log_history trigger
#for it 
def enable_logging(table):
    os.system('psql '+DB_ARGS+' -c \
            \"SELECT history_create_trigger(\'{0}\');\"'.format(table))

#Disable history logging for the given table by deleting the log_history
#trigger for it 
def disable_logging(table): 
    os.system('psql '+DB_ARGS+' -c \
            \"SELECT history_delete_trigger(\'{0}\');\"'.format(table))

#Dump the history table corresponding to the table given as an argument to
#disk, as table_name_histdump.dump
def make_dump(table):
    os.system('pg_dump '+DB_ARGS+' -t {0}_hist > {1}_histdump.dump'\
              .format(table,table))

#Main driver
def main():
    #Set up argument parsing
    parser = argparse.ArgumentParser(description=\
    'Command line tool to manage postgres history tables.')
    parser.add_argument('--enable', nargs='+', metavar='table_name',\
                        help='enable history logging (creates history logging'\
                        ' trigger) for all argument tables')
    parser.add_argument('--disable', nargs='+', metavar='table_name',\
                        help='disable history logging (deletes history logging'\
                        ' trigger) for all argument tables')
    parser.add_argument('--dump', nargs='+', metavar='table_name',\
                        help='dump the history tables corresponding to all '\
                        'argument tables to disk, as table_name_histdump.dump')

    #Make args a dictionary {'option' : [args]}
    args = vars(parser.parse_args())

    #Ensure that at least one option had arguments. If so, run the sql to create
    #the necessary functions; they are CREATE OR REPLACE statements so it won't
    #matter if the functions already exist. This will ensure that the rest of
    #this script will never fail if the functions were never created
    if not (args['enable'] or args['disable'] or args['dump']):
        print 'Use --enable, --disable, or --dump! See -h for details.'
        exit(1)
    else:
        init_functions()

    #Process arguments, call appropriate functions
    if args['enable'] != None:
        for a_table in args['enable']:
            enable_logging(a_table)

    if args['disable'] != None:
        for a_table in args['disable']:
            disable_logging(a_table)

    if args['dump'] != None:
        for a_table in args['dump']:
            make_dump(a_table)

main()
