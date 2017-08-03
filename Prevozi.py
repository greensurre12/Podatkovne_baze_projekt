#!/usr/bin/env python3

import bottle
from bottle import *
import hashlib
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from funkcije import * 
import sqlite3
from datetime import datetime
from bottle import get, static_file

######################################################################

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) #
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)                          #GLOBALNO
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)                                      #

secret = "to je signature key za cookije, zato naj bo nek nakjlučni niz aosfh1309uhn0f1j1f9hj"
#####################################################################################

static_dir = "./static"
# Static Routes
"Da lahko bere css in javascript datoteke iz mape static"
@route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return bottle.static_file(filename, root=static_dir)

######################################################################
"""PRVA STRAN"""

@route("/")
def prva_stran():

	return bottle.template("index.html", napaka=False) 

######################################################################
"""SIGNUP"""

@route('/signup', method= "POST")
def signup():
    """Registrira novega uporabnika. Preveri ce uporabnisko ime ze obstaja, ce se gesli ujemata, ce sta geslo, uporabnisko ime dovolj dolgi. Ce je vse ok, hashano geslo 
    in podatke o uporabniku shrani v tabelo uporabnik v bazi. Nastavi piskotek in prikaze glavno stran."""
         
    uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
    geslo = bottle.request.forms.geslo
    potrdi_geslo = bottle.request.forms.potrdi_geslo
    email= bottle.request.forms.email


    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [uporabnisko_ime])

    if cur.rowcount != 0: 
        return bottle.template("index.html", napaka="To uporabnisko ime že obstaja!")
            
    elif geslo != potrdi_geslo:
        return bottle.template("index.html", napaka="Gesli se ne ujemata!")
    elif len(geslo)<4: 
        return bottle.template("index.html", napaka="Geslo naj ima vsaj 4 znake!")
    elif len(uporabnisko_ime)<4:
        return bottle.template("index.html", napaka="Uporabnisko ime naj ima vsaj 4 znake!")

        
    else:
        geslo = funkcije.password_md5(geslo) 
        cur.execute("INSERT INTO uporabnik (id, username, geslo, email) VALUES (DEFAULT, %s, %s, %s)", (uporabnisko_ime, geslo, email))
        bottle.response.set_cookie("account", value=uporabnisko_ime, secret=secret, path='/') 
        
        return redirect('/{0}'.format(uporabnisko_ime)) 

########################################################################################        
"""LOGIN"""

@route('/login', method="POST")
def login():
	"""Logira ze obstojecega uporabnika. Preveri ce se hasha gesel ujemata, ce je prijava uspesna prikaze glavno stran, drugace se vrne na prvo stran z sporocilom o neuspesni prijavi."""

    
	uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
	geslo = funkcije.password_md5(bottle.request.forms.geslo)
	cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND geslo=%s",[uporabnisko_ime, geslo])

	if cur.rowcount == 0: 
		return bottle.template("index.html", napaka="Napacno uporabnisko ime ali geslo!")

	else:
		bottle.response.set_cookie('account', value=uporabnisko_ime, secret=secret, path='/')
		return redirect('/{0}'.format(uporabnisko_ime))

########################################################################################     
"""LOGOUT"""

@bottle.get('/logout')
def logout():

	bottle.response.delete_cookie('accout', secret=secret)
	return redirect('/')


######################################################################
"""GLAVNA STRAN"""

@route("/<uporabnik>", method = "GET")
def glavna_stran(uporabnik):
	"""Glavna stran aplikacije. Preveri piskotek, ce ga ni, se vrne na prvo stran. 
	Od tu so gumbi na iskalnik in odjavo. Gumb 'Moji prevozi' prikaze prevoze, na katere je uporabnik ze prijavljen. Gumb 'Objavi' prikaze moznost, da uporabnik 
	objavi svoj prevoz.
	POST metoda obdela objavo novega prevoza."""
	cookie = request.get_cookie('account', secret=secret)

	if str(cookie) == uporabnik:
		cur.execute("SELECT * FROM ((SELECT zacetni_kraj, koncni_kraj, zacetek, narocnik FROM prevoz INNER JOIN narocanje ON narocanje.prevoz = prevoz.id) AS neki JOIN uporabnik ON neki.narocnik = uporabnik.id) AS neki2 WHERE username = %s",[uporabnik])
		moji_prevozi = cur.fetchall()

		cur.execute("SELECT * FROM (prevoz INNER JOIN uporabnik ON prevoz.objavil = uporabnik.id) WHERE username = %s", [uporabnik])
		objavljeni_prevozi = cur.fetchall()
		return bottle.template("uporabnik.html", sporocilo="", uporabnik=uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'), moji_prevozi = moji_prevozi, objavljeni_prevozi=objavljeni_prevozi)
	else:
		return redirect("/")

@route("/<uporabnik>", method = "POST")
def glavna_stran(uporabnik):
	zacetni_kraj = bottle.request.forms.zacetni_kraj
	koncni_kraj = bottle.request.forms.koncni_kraj
	zacetek = bottle.request.forms.zacetek
	konec = bottle.request.forms.konec
	prosta_mesta = bottle.request.forms.prosta_mesta
	uporabnik =  str(request.get_cookie('account', secret=secret))


	cur.execute("SELECT 1 FROM kraj WHERE ime = %s", [zacetni_kraj])
	if cur.rowcount == 0:
		return bottle.template("uporabnik.html", sporocilo="Zacetni kraj ne obstaja!", uporabnik=uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

	cur.execute("SELECT 1 FROM kraj WHERE ime = %s", [koncni_kraj])
	if cur.rowcount == 0:
		return bottle.template("uporabnik.html", sporocilo="Koncni kraj ne obstaja!", uporabnik=uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

	#if zacetek < datetime.now():
	#	return bottle.template("uporabnik.html", sporocilo="Objava prevozov za nazaj ni mogoca!", uporabnik=uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))
	
	else:
		objavil1 = cur.execute("SELECT id FROM uporabnik WHERE username=%s", [uporabnik])
		zacetni_kraj1 = cur.execute("SELECT id FROM kraj WHERE ime=%s",[zacetni_kraj])
		koncni_kraj1 = cur.execute("SELECT id FROM kraj WHERE ime=%s",[koncni_kraj])

		cur.execute("INSERT INTO prevoz (id, objavil, zacetek, zacetni_kraj, konec, koncni_kraj, prosta_mesta) VALUES (DEFAULT,%s,%s,%s,%s,%s,%s)",(objavil1,zacetek,zacetni_kraj1,konec,koncni_kraj1,prosta_mesta)) 
		
		#cur.execute("SELECT zacetek, ime, konec, ime2, prosta_mesta FROM ((prevoz JOIN uporabnik ON prevoz.objavil = uporabnik.id JOIN kraj ON prevoz.zacetni_kraj = kraj.id) AS neki JOIN (SELECT id, ime AS ime2 FROM kraj) AS neki2 ON neki.koncni_kraj = neki2.id) AS neki3")
		
		cur.execute("SELECT zacetni_kraj1, koncni_kraj1, zacetek FROM (((SELECT zacetni_kraj, koncni_kraj, zacetek, narocnik FROM prevoz INNER JOIN narocanje ON narocanje.prevoz = prevoz.id) AS neki JOIN uporabnik ON neki.narocnik = uporabnik.id) AS neki2 JOIN (SELECT id, ime AS zacetni_kraj1 FROM kraj) AS neki3 ON neki2.zacetni_kraj = neki3.id) AS neki4 JOIN (SELECT id, ime AS koncni_kraj1 FROM kraj) AS neki5 ON neki4.koncni_kraj = neki5.id WHERE username =  %s",[uporabnik])
		moji_prevozi = cur.fetchall()

		cur.execute("SELECT zacetni_kraj1, koncni_kraj1, zacetek, prosta_mesta FROM (((prevoz JOIN uporabnik ON prevoz.objavil = uporabnik.id) AS neki JOIN (SELECT id, ime AS zacetni_kraj1 FROM kraj) AS neki2 ON neki.zacetni_kraj = neki2.id)AS neki4 JOIN (SELECT id, ime AS koncni_kraj1 FROM kraj) AS neki5 ON neki4.koncni_kraj = neki5.id) AS neki6 WHERE username =  %s", [uporabnik])
		objavljeni_prevozi = cur.fetchall()
		return bottle.template ("uporabnik.html", sporocilo="Uspesno si objavil prevoz!", uporabnik=uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'), moji_prevozi = moji_prevozi, objavljeni_prevozi=objavljeni_prevozi)                            



########################################################################################    
"""SEARCH"""
@route("/search", method = "GET")
def isci():
	"""Iskalnik, zahteva zacetni in koncni kraj in stevilo potnikov. Metoda POST podatke obdela in prikaze stran z rezultati iskanja. Tam se pokazejo vsi prevozi, ki vstrezajo parametrom iskanja in
	vsaj se dovolj prostora za zeljeno stevilo potnikov."""
	uporabnik = str(request.get_cookie('account', secret=secret))
	cur.execute("SELECT 1 FROM uporabnik WHERE username = %s", [uporabnik])

	if cur.rowcount == 0:
		return redirect("/") 

	else:
		return bottle.template("iskanje.html", zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'), uporabnik=uporabnik)

@route('/search', method = "POST")
def isci():
	uporabnik = str(request.get_cookie('account', secret=secret))


	odhod = bottle.request.forms.odhod
	prihod = bottle.request.forms.prihod
	st_potnikov = bottle.request.forms.st_potnikov


	if odhod == None:
		odhod = ""
	if prihod == None:
		prihod = ""

	cur.execute("SELECT zacetni_kraj1, koncni_kraj1, zacetek, prosta_mesta, username, id1 FROM (((SELECT id AS id1, zacetek, konec, prosta_mesta, objavil, zacetni_kraj, koncni_kraj FROM prevoz) AS prevoz JOIN (SELECT id, ime AS zacetni_kraj1 FROM kraj) AS neki ON prevoz.zacetni_kraj = neki.id) AS neki2 JOIN (SELECT id, ime AS koncni_kraj1 FROM kraj) AS neki3 ON neki2.koncni_kraj = neki3.id) AS neki4 JOIN uporabnik ON neki4.objavil = uporabnik.id WHERE  prosta_mesta >= %s AND zacetni_kraj1 ILIKE %s AND koncni_kraj1 ILIKE %s ", [st_potnikov, odhod, prihod])
    
	rezultat_iskanja = cur.fetchall() #type() = tuple

	return bottle.template("rezultati.html",zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'), rezultat_iskanja=rezultat_iskanja, uporabnik=uporabnik, st_potnikov=st_potnikov)
 
########################################################################################    
"""PRIJAVA"""

@route('/prijava/<id_prevoza>&<st_potnikov>', method = "POST")
def prijava(id_prevoza, st_potnikov):
	"""Obdela prijavo na prevoz, hkrati odsteje prijavljena mesta od prostih mest v prevozu. Vrne se na glavno stran."""
	uporabnik = str(request.get_cookie('account', secret=secret))
	id_uporabnika = cur.execute("SELECT id FROM uporabnik WHERE username = %s",(uporabnik))
	
	cur.execute("INSERT INTO narocanje(id, narocnik, prevoz, mesta) VALUES (DEFAULT, %s, %s, %s)",(id_uporabnika, id_prevoza, st_potnikov))
	cur.execute("UPDATE prevoz SET prosta_mesta = prosta_mesta-%s WHERE id = %s", (st_potnikov, id_prevoza))

	return redirect("/{0}".format(uporabnik))
  



run()
