import os

os.system('psql -U alex -d alex -f log-history.sql')


def main():
