#!/usr/bin/env python3

import bottle
from bottle import *
import hashlib # računanje MD5 kriptografski hash za gesla
import auth_public as auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
import funkcije 
import sqlite3
from datetime import datetime
######################################################################

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password) #GLOBALNO
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)                          #
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)                                      #

secret = "to je signature key za cookije, zato naj bo nek nakjlučni niz aosfh1309uhn0f1j1f9hj"

######################################################################
"""PRVA STRAN"""

@route("/")
def prva_stran():
    return template("prva_stran.html", napaka=False)


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
            
        bottle.response.set_cookie("account", uporabnisko_ime, secret=secret) #cookie 
        return template("glavna_stran.html", uporabnik = uporabnisko_ime, napaka=False) #na glavno stran

########################################################################################        
"""LOGIN"""

@route('/login', method ="GET")
def login():
    """Prikaze template za vpis"""
    return template ("login.html", napaka = False)

@route('/login', method="POST")
def login():
    print("login1")
    
    uporabnisko_ime = bottle.request.forms.uporabnisko_ime 
    geslo = funkcije.password_md5(bottle.request.forms.geslo)
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s AND geslo=%s",[uporabnisko_ime, geslo])

    if cur.rowcount == 0: #ce SELECT ne najde nicesar -> ta kombinacija (username, password) ne obstaja
        print("login2")
        return bottle.template("login.html", napaka="Napacno uporabnisko ime ali geslo!")

    else:
        print("login3")
        bottle.response.set_cookie('account', uporabnisko_ime, secret=secret)
        return template("glavna_stran.html", uporabnik = uporabnisko_ime, napaka=False)
        #return redirect("/<username>")
########################################################################################     
"""LOGOUT"""

@bottle.get('/logout')
def logout():
    """Pobriši cookie in preusmeri na login."""
    bottle.response.delete_cookie('account')
    return template("prva_stran.html",napaka=False)

########################################################################################
"""OBJAVA PREVOZA"""

@route('/objavi/<name>')
def objavi(name):
    cur.execute("SELECT 1 FROM uporabnik WHERE username=%s", [name])

    if cur.rowcount == 0: #ce uporabnika ni v bazi, npr če naroke napišeš /objavi/neobstoječ_uporabnik , to ne sme!!
        return template("prva_stran.html", napaka = "Žal ta uporabnik ne obstaja!")
    else:
        return template("objavi.html",uporabnik = name,napaka=False, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M')) #tisti koledar nebo dovolil vnosa manjsega od zdaj
    
@route('/objavi/<name>', method = "POST")
def objavi_post(name):
    ''' /objavi/<name> : forma v html na glavni strani sprejme /objavi/upobraniško_ime, zato da ga lahko upiševa v bazo.
    nekako morava zaščititi to, da lahko dostopiš do wwww.spletna.com/objavi/, le če si loginan, drugače te mora zavrniti'''
    zacetek = bottle.request.forms.zacetek
    zacetni_kraj=bottle.request.forms.zacetni_kraj
    konec = bottle.request.forms.konec
    koncni_kraj = bottle.request.forms.koncni_kraj
    prosta_mesta = bottle.request.forms.prosta_mesta
    uporabnisko_ime = name
    print("objavi2")

    ##
    cur.execute("SELECT 1 FROM kraj WHERE ime=%s",[zacetni_kraj])
    if cur.rowcount == 0:
        return template("objavi.html", napaka = "Zacetni kraj ne obstaja!", uporabnik = name, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

    cur.execute("SELECT 1 FROM kraj WHERE ime=%s",[koncni_kraj])
    if cur.rowcount == 0:
        return template("objavi.html", napaka = "Koncni kraj ne obstaja!", uporabnik = name, zdaj = datetime.now().strftime('%Y-%m-%dT%H:%M'))

    else:
        id = cur.execute("SELECT id FROM uporabnik WHERE username=%s", [name]) #poisce id uporabnika
        cur.execute("INSERT INTO prevoz (id,objavil,  zacetek,zacetni_kraj,konec,koncni_kraj,prosta_mesta) VALUES (DEFAULT,%s,%s,%s,%s,%s,%s)",
                                        (name,zacetek,zacetni_kraj,konec,koncni_kraj,prosta_mesta)) 
        return template("glavna_stran.html",uporabnik=name, napaka= "Uspesno si objavil prevoz!")
        
    ##

    
    #TO NEKI NE DELA, KAJ CE BI NAREDILA KOT JE ZE PRI OMEJITVAH ZA USERNAME/GESLO
    #error = funkcije.validate_form(request.forms, [ "zacetni_kraj", "koncni_kraj", "zacetek","konec"]) #preveri ali je kaj prazno validate_form je v funkcije.py 
    #if error is []:
    #    napaka = False
    #    print('ni napake')
    #else:
    #    print('je napaka')
    #    napaka = "Prazno : " + str(error)
    #    return template("objavi.html", napaka = napaka, uporabnik = name)
    # 
    #
    #    
    #cur.execute("SELECT 1 FROM kraj WHERE ime = %s", [zacetni_kraj]) #zaenkrat tukaj preveriva ali je kraj OK, kasneje z Javascript že na sami strani!"
    #if cur.rowcount == 0: 
    #    return template("objavi.html", uporabnik = name,napaka="Kraj '%s' ne obstaja! Preveri ali si ga pravilno zapisal \n primer: Bohinjska Bela, Bled"% (zacetni_kraj))
    # 
    #cur.execute("SELECT 1 FROM kraj WHERE ime = %s", [koncni_kraj]) #zaenkrat tukaj preveriva ali je kraj OK!"
    #if cur.rowcount == 0: 
    #    return template("objavi.html", uporabnik = name, napaka="Kraj '%s' ne obstaja! Preveri ali si ga pravilno zapisal \n primer: Bohinjska Bela, Bled" %(koncni_kraj))
    #        
    #
    #
    #
    #
    #id = cur.execute("SELECT id FROM uporabnik WHERE username=%s", [name]) #poisce id uporabnika
    #cur.execute("INSERT INTO prevoz (id,objavil,zacetek,zacetni_kraj,konec,koncni_kraj,prosta_mesta) VALUES (DEFAULT, %s, %s, %s,%s,%s,%s)", 
    #            (id, zacetek, zacetni_kraj, konec, koncni_kraj,prosta_mesta))
    # 
    #return template("glavna_stran.html",uporabnik=name, napaka= "Uspesno si objavil prevoz!")
    
    
    
    

run()
