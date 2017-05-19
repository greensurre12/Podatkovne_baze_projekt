#!/usr/bin/env python3

import bottle
from bottle import *
import hashlib # računanje MD5 kriptografski hash za gesla
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
from funkcije import * 
import sqlite3
from datetime import datetime
######################################################################

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) #
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)                          #GLOBALNO
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)                                      #

secret = "to je signature key za cookije, zato naj bo nek nakjlučni niz aosfh1309uhn0f1j1f9hj"
######################################################################
"""PREBERI TO
-cookies: cookie ima ime account, v njem je shranjeno uporabnisko ime, hashano ker ga lahko kdorkoli bere
-redirect: ce hoces na istem naslovu pokazat nekaj drugega, uporabis return(template), ce pa hoces uporabnika
 poslat na drugo stran, uporabis redirect. Argumente v redirect shranis v url, ki ga posljes ali pa v cookie.
-ZDI SE MI da je treba ob vsaki novi preusmeritvi cookie preveriti
"""


######################################################################
"""PRVA STRAN"""

@route("/")
def prva_stran():
    cookie = str(request.get_cookie('account', secret=secret))
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [cookie])    

    if cur.rowcount == 0:        
        return template("prva_stran.html", napaka=False) #ce ze ma cookie ga avtomatsko logira
    else:
        return redirect('/{0}'.format(cookie))

######################################################################
"""GLAVNA STRAN"""

@route("/<uporabnik>")
def glavna_stran(uporabnik):
    cookie = request.get_cookie('account', secret=secret)
    if str(cookie) == uporabnik:
        return template("glavna_stran.html", napaka=False, uporabnik=uporabnik)
    else:
        return redirect("/")

######################################################################
"""SIGNUP"""

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
        geslo = funkcije.password_md5(geslo) #zakodira geslo za shranjevanje
        cur.execute("INSERT INTO uporabnik (id, username, geslo, telefon) VALUES (DEFAULT, %s, %s, %s)", (uporabnisko_ime, geslo, telefon))
        bottle.response.set_cookie("account", value=uporabnisko_ime, secret=secret, path='/') #cookie 
        return redirect('/glavna/{0}'.format(uporabnisko_ime)) #na glavno stran

########################################################################################        
"""LOGIN"""

@route('/login', method ="GET")
def login():
    """Prikaze template za vpis"""
    return template ("login.html", napaka = False)

@route('/login', method="POST")
def login():
    
    uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
    geslo = funkcije.password_md5(bottle.request.forms.geslo)
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND geslo=%s",[uporabnisko_ime, geslo])

    if cur.rowcount == 0: #ce SELECT ne najde nicesar -> ta kombinacija (username, password) ne obstaja
        return bottle.template("login.html", napaka="Napacno uporabnisko ime ali geslo!")

    else: #uspesen login
        bottle.response.set_cookie('account', value=uporabnisko_ime, secret=secret, path='/')
        return redirect('/{0}'.format(uporabnisko_ime))


########################################################################################     
"""LOGOUT"""

@bottle.get('/logout')
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('account',secret=secret)
    return redirect('/')

########################################################################################
"""OBJAVA PREVOZA"""

@route('/<uporabnik>/objavi')
def objavi(uporabnik):
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [uporabnik])

    if cur.rowcount == 0: #ce uporabnika ni v bazi, npr če naroke napišeš /objavi/neobstoječ_uporabnik , to ne sme!!
        return template("prva_stran.html", napaka = "Žal ta uporabnik ne obstaja!")
    else:
        return template("objavi.html",uporabnik = uporabnik,napaka=False, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M')) #tisti koledar nebo dovolil vnosa manjsega od zdaj
    
@route('/<uporabnik>/objavi', method = "POST")
def objavi_post(uporabnik):
    ''' /objavi/<name> : forma v html na glavni strani sprejme /objavi/upobraniško_ime, zato da ga lahko upiševa v bazo.
    nekako morava zaščititi to, da lahko dostopiš do wwww.spletna.com/objavi/, le če si loginan, drugače te mora zavrniti'''
    zacetek = bottle.request.forms.zacetek
    zacetni_kraj=bottle.request.forms.zacetni_kraj
    konec = bottle.request.forms.konec
    koncni_kraj = bottle.request.forms.koncni_kraj
    prosta_mesta = bottle.request.forms.prosta_mesta
    uporabnisko_ime = uporabnik
    print("objavi2")

    ##
    cur.execute("SELECT 1 FROM kraj WHERE ime=%s",[zacetni_kraj])
    if cur.rowcount == 0:
        return template("objavi.html", napaka = "Zacetni kraj ne obstaja!", uporabnik = uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

    cur.execute("SELECT 1 FROM kraj WHERE ime=%s",[koncni_kraj])
    if cur.rowcount == 0:
        return template("objavi.html", napaka = "Koncni kraj ne obstaja!", uporabnik = uporabnik, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

    else:
        id = cur.execute("SELECT id FROM uporabnik WHERE username=%s", [uporabnik]) #poisce id uporabnika
        cur.execute("INSERT INTO prevoz (id,objavil,  zacetek,zacetni_kraj,konec,koncni_kraj,prosta_mesta) VALUES (DEFAULT,%s,%s,%s,%s,%s,%s)",
                                        (uporabnik,zacetek,zacetni_kraj,konec,koncni_kraj,prosta_mesta)) 
        return template("glavna_stran.html",uporabnik=uporabnik, napaka= "Uspesno si objavil prevoz!")

########################################################################################    
"""SEARCH"""
@route('/<uporabnik>/isci')
def isci(uporabnik):
    uporabnik = request.get_cookie('account', secret=secret)
    if uporabnik == None
        return redirect("/")
    
    else:
        return template("iskanje.html")
    

run()
