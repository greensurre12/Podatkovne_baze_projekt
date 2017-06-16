"""Tabele za bazo"""

CREATE TABLE uporabnik (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE, 
    geslo TEXT NOT NULL,
    telefon TEXT,
    email TEXT NOT NULL,
    );

CREATE TABLE kraj (
    ime TEXT PRIMARY KEY 
    );
    
CREATE TABLE prevoz (
    id SERIAL PRIMARY KEY,
    objavil TEXT """FOREIGN KEY TO DA ERROR; ZAKAJ?""" REFERENCES uporabnik(username),
    ON DELETE CASCADE, --ce se uporabnik zbrise, se tudi njegov prevoz zbrise   
    zacetek TIMESTAMP NOT NULL, 
    zacetni_kraj TEXT REFERENCES kraj(ime) NOT NULL,
    konec TIMESTAMP,
    koncni_kraj TEXT REFERENCES kraj(ime) NOT NULL,  
    prosta_mesta INTEGER
    );

    
CREATE TABLE narocanje (
    narocnik TEXT REFERENCES uporabnik(username),
    prevoz INTEGER REFERENCES prevoz(id),
    mesta INTEGER,  
    
    PRIMARY KEY (narocnik, prevoz)
    )
