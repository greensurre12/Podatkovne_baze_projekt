#!/usr/bin/env python3


import bottle
from bottle import *
import hashlib # računanje MD5 kriptografski hash za gesla
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

import sqlite3
######################################################################

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) #A GRE TO V VSAKO FUNKCIJO POSEBEJ AL JE LAHKO TUKI ZA VSE?
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)                          #
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)                                      #

secret = "to je signature key za cookije, zato naj bo nek nakjlučni niz aosfh1309uhn0f1j1f9hj"

######################################################################

def password_md5(s):
    """Funkcija za hasanje gesel."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

######################################################################

@route("/")
def prva_stran():
    return template("prva_stran.html")
    

@route('/signup', method = "GET")       #prvi @route prikaze template, drugi pobere podatke ki jih uporabnik vpise
def signup():
    """Prikaze template na strani"""
    return template("signup.html", napaka=False)

@route('/signup', method= "POST")
def signup():
    """Registrira novega uporabnika."""
    
        
    uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
    geslo = bottle.request.forms.geslo
    potrdi_geslo = bottle.request.forms.potrdi_geslo
    telefon = bottle.request.forms.telefon
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [uporabnisko_ime])

    if cur.rowcount != 0: #ce SELECT najde nekaj -> ta username ze obstaja
        return bottle.template("signup.html", napaka="To uporabnisko ime že obstaja!")
            
    elif geslo != potrdi_geslo:
        return bottle.template("signup.html", napaka="Gesli se ne ujemata!")

    elif len(geslo)<4: #Neke omejitve glede na geslo, ime, telefon. Lahko poljubno spreminjas.
        return bottle.template("signup.html", napaka="Geslo naj ima vsaj 4 znake!")
    elif len(uporabnisko_ime)<4:
        return bottle.template("signup.html", napaka="Uporabnisko ime naj ima vsaj 4 znake!")
    elif len(telefon)==0:
        return bottle.template("signup.html", napaka="Telefon je obvezen!")
        
    else:
        geslo = password_md5(geslo) #zakodira geslo za shranjevanje
        cur.execute("INSERT INTO uporabnik (id, username, geslo, telefon) VALUES (DEFAULT, '{0}', '{1}', '{2}')".format(uporabnisko_ime, geslo, telefon))
            
        bottle.response.set_cookie("account", uporabnisko_ime, secret=secret) #cookie 
        return template("glavna_stran.html", uporabnik = uporabnisko_ime) #na glavno stran

########################################################################################        

@route('/login')
def login():
    """Prikaze template za vpis"""
    return template ("login.html", napaka = False)

@route('/login', method="POST")
def login():
    
    uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
    geslo = password_md5(bottle.request.forms.geslo)
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND geslo=%s",[uporabnisko_ime, geslo])

    if cur.rowcount == 0: #ce SELECT ne najde nicesar -> ta kombinacija (username, password) ne obstaja
        return bottle.template("login.html", napaka="Napacno uporabnisko ime ali geslo!")

    else:
        bottle.response.set_cookie('account', uporabnisko_ime, secret=secret)
        return template("glavna_stran.html", uporabnik = uporabnisko_ime)
    
########################################################################################     

@bottle.get('/logout')
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('account')
    return template("prva_stran.html")



run()
