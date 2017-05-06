"""Tabele za bazo"""

CREATE TABLE uporabnik (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE, 
    geslo TEXT NOT NULL,
    telefon TEXT 
    );

CREATE TABLE kraj (
    ime TEXT PRIMARY KEY 
    );
    
CREATE TABLE prevoz (
    id SERIAL PRIMARY KEY,
    objavil INTEGER """FOREIGN KEY TO DA ERROR; ZAKAJ?""" REFERENCES uporabnik(id),
    ON DELETE CASCADE, --ce se uporabnik zbrise, se tudi njegov prevoz zbrise   
    zacetek TIMESTAMP NOT NULL, 
    zacetni_kraj TEXT REFERENCES kraj(ime) NOT NULL,
    konec TIMESTAMP,
    koncni_kraj TEXT REFERENCES kraj(ime) NOT NULL,  
    prosta_mesta INTEGER
    );

    
CREATE TABLE narocanje (
    narocnik INTEGER REFERENCES uporabnik(id),
    prevoz INTEGER REFERENCES prevoz(id),
    mesta INTEGER,  
    
    PRIMARY KEY (narocnik, prevoz)
    )
