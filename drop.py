import MySQLdb as mdb

con = None
try:
    con = mdb.connect('129.21.50.240', 'Tal', 'rossissexy6969', 'cshsports')
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)


cur = con.cursor()
cur.execute("drop table sports_matchup; drop table sports_player; drop table sports_team;")
