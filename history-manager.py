import os
import argparse
import re

#How should the psql command line calls connect to the database?
#Example: '-U s2s -d s2sdb'
DB_ARGS=''

#Initialize the functions necessary for this script to work (see below)
def init_functions():
    os.system('psql '+DB_ARGS+' -f log-history.sql')
    os.system('psql '+DB_ARGS+' -f create-trigger.sql')
    os.system('psql '+DB_ARGS+' -f delete-trigger.sql')
    os.system('psql '+DB_ARGS+' -f delete-all.sql')

#Enable history logging for the given table by creating the log_history trigger
#for it 
def enable_logging(table):
    retcode = os.system('psql '+DB_ARGS+' -c \
            \"SELECT history_create_trigger(\'{0}\');\"'.format(table))
    if not retcode:
        print 'History logging enabled for table {t}. Remember that if you add'\
              ' a column to {t} after the {t}_hist table is created, you need'\
              ' to add that column to {t}_hist as well!'.format(t=table)
    else:
        print 'Something went wrong trying to enable history logging for'\
              ' table {t}... it\'s probably already enabled.'.format(t=table)

#Disable history logging for the given table by deleting the log_history
#trigger for it 
def disable_logging(table): 
    retcode = os.system('psql '+DB_ARGS+' -c \
            \"SELECT history_delete_trigger(\'{0}\');\"'.format(table))
    if not retcode:
        print 'History logging disabled for table {t}.'.format(t=table)
    else:
        print 'Something went wrong trying to disable history logging for'\
              ' table {t}... it\'s probably already disabled.'.format(t=table)

#Disable history logging for all tables in the database under the "public"
#schema (ignores tables that do not have history logging enabled)
def disable_all():
    os.system('psql '+DB_ARGS+' -c \
              \"SELECT history_delete_all();\"')

#Dump the history table corresponding to the table given as an argument to
#disk, as table_name_histdump.dump
def make_dump(table):
    #This ridiculous hackery is necessary because pg_dump doesn't take the -d
    #option like psql. Arrg. It might fail if you format the argument string
    #weirdly, if so just do the dump yourself. But it should work if you follow
    #the format of the example I give :)
    try:
        dbstr = re.findall(r'-d .+[ ]*', DB_ARGS)
        dbname = dbstr[0].split('-d')[1].strip(' ')
        rest_of_args = DB_ARGS.replace(dbstr[0], '')
    except:
        print 'Something went wrong trying to derive the database name from'\
              ' your DB_ARGS string. You should feel bad. Do the dump'\
              ' yourself! \n(pg_dump [connection args] -t table_name_hist'\
              ' db_name > output_file.dump)'
        exit(1)
    os.system('pg_dump '+rest_of_args+' -t {0}_hist {1} > {2}_histdump.dump'\
              .format(table,dbname,table))

#Main driver. Note that you could easily tweak this to allow it to be integrated
#into a python project and be called programmatically, with arguments (instead
#of using command line arguments)
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
    parser.add_argument('--disableall', action='store_const', const=1, \
                        help='disable history logging for all tables'\
                             ' in the database under the "public" schema.'\
                             ' Don\'t use this with other options.')
    parser.add_argument('--dump', nargs='+', metavar='table_name',\
                        help='dump the history tables corresponding to all '\
                        'argument tables to disk, as table_name_histdump.dump')
    #Make args a dictionary {'option' : [args]}
    args = vars(parser.parse_args())

    #Ensure that at least one option had arguments. If so, run the sql to create
    #the necessary functions; they are CREATE OR REPLACE statements so it won't
    #matter if the functions already exist. This will ensure that the rest of
    #this script will never fail if the functions were never created
    if not (args['enable'] or args['disable'] or args['dump'] \
            or args['disableall']):
        print 'Use --enable, --disable, --disableall, or --dump!'\
              ' See -h for details.'
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

    if args['disableall'] != None:
        disable_all()

    if args['dump'] != None:
        for a_table in args['dump']:
            make_dump(a_table)

main()
