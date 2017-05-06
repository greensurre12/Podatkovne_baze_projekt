#!/usr/bin/python
# -*- encoding: utf-8 -*
"""S tem sem vstavil kraje v tabelo kraji v bazi. Zakomentirana vrstica daje nek error."""

from bottle import *
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) 
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#ZA TABELO KRAJI:
#with open ("Seznam_krajev.txt", "r") as datoteka:
#    seznam_krajev = [i.strip()[5:] for i in datoteka]
#
#    
##cur.executemany("""INSERT INTO kraj (ime) VALUES (%s)""", seznam_krajev) #TO NE DELA ZARAD NEKIH CUDNIH RAZLOGOV
#
#for i in seznam_krajev:
#    cur.execute("""INSERT INTO kraj (ime) VALUES ('{}')""".format(str(i)))
#
run()

