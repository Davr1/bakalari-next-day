#!/usr/bin/env python3

import requests
import datetime
import re

class Bakalari: # Trida pro pristup k API bakalaru
    
    
    def __init__(self, login, password, adresa): # Argumenty jsou string s prihlasovacim jmenem, string s heslem a string s url adresou bakalaru skoly. Zadane udaje se vyuziji pri ziskavani tokenu
        
        # Odstrani prebytecny text z adresy a prida zpatky https protokol a /api endpoint
        adresa = re.sub(r"(https?:\/\/)|(\/login)|(\/$)", "", adresa)
        self.adresa = f"https://{adresa}/api"
        
        prihlasovaciUdaje = {
            "client_id": "ANDR",
            "grant_type": "password",
            "username": login,
            "password": password
        }

        # Ziska token ze serveru bakalaru
        self.token = requests.post(
            self.adresa + "/login",
            headers={"Content-type": "application/x-www-form-urlencoded"},
            data=prihlasovaciUdaje
        ).json().get("access_token")
    
    
    def rozvrh(self): # Vraci json s rozvrhem a vytvori promenou schedule se stejnym obsahem
        
        # Ziska zitrejsi datum a zformatuje jej (YYYY-MM-DD) aby bylo pouzitelne v nasledujicim requestu
        datum = (datetime.datetime.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # Ziskani rozvrhu pro dane datum
        self.schedule = requests.get(
            self.adresa + "/3/timetable/actual",
            headers={"Content-type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {self.token}"},
            params={"date": datum}
        ).json()
        return self.schedule

class SkolniTyden(): # Trida pro zpracovavani json z bakalaru


    def __init__(self, schedule): # Argument je json s rozvrhem z Bakalaru
        
        # Ziska nazvy predmetu a vytvori dict key id:nazev pro kazdy predmet
        nazvyPredmetu = {}
        predmety = schedule["Subjects"]
        for predmet in predmety:
            nazvyPredmetu[predmet["Id"]] = predmet["Name"]

        self.rozvrh = [] 
        cisloDnu = 0      
        
        # Pro kazdy den v rozvrhu se do self.rozvrh prida prazdne pole
        dny = list(den["Atoms"] for den in schedule["Days"])
        for denniRozvrh in dny:
            self.rozvrh.append([])
            
            # Pro kazde pole (reprezentuje den ve skolnim rozvrhu) v self.rozvrh se do nej pridaji nazvy hodin, ktere v ten den jsou
            for hodina in denniRozvrh:
                if hodina["SubjectId"] != None:
                    self.rozvrh[cisloDnu].append(nazvyPredmetu[hodina["SubjectId"]])
            
            cisloDnu += 1


    def vzitNa(self, den): # Vraci list se dvema listy, prvni obsahuje predmety co do tazky pridat, druhy co z ni vyndat
        
        # Pokud je pondeli, predchozi den je patek
        if den == 0:
            vcera = self.rozvrh[4]
        else:
            vcera = self.rozvrh[den-1]
        
        dnes = self.rozvrh[den]
        pridat = []
        odebrat = []
        
        # Pokud je hodina dnes a nebyla vcera, prida se do promene pridat, pokud byla vcera a neni dnes, prida se do promene odebrat
        for hodina in dnes:
            if hodina not in vcera:
                pridat.append(hodina)
        
        for hodina in vcera:
            if hodina not in dnes:
                odebrat.append(hodina)
        
        # Filtrovani opakujicich se predmetu
        pridat = set(pridat)
        pridat = list(pridat)
        
        odebrat = set(odebrat)
        odebrat = list(odebrat)
        
        return([pridat, odebrat])

# Ziskani udaju
jmeno = input("Prihlasovaci jmeno: ")
heslo = input("Heslo: ")
adresa = input("URL adresa bakalaru skoly: ")

# Inicializace trid    
uzivatel = Bakalari(jmeno, heslo, adresa)
tyden = SkolniTyden(uzivatel.rozvrh())

# Pokud neni zitra vikend, zobrazi se co si na zitrek vzit a co vyndat
zitra = datetime.datetime.today().weekday()+1
if zitra != 6 and zitra != 7:
    naZitra = tyden.vzitNa(zitra)

    # Odpoved
    print("")
    print ("Do tasky si pridej: \n")
    for predmet in naZitra[0]:
        print(predmet)
        # Za poslednim udelat prazdnou radku
        if naZitra[0][len(naZitra[0])-1] == predmet:
            print("")

    print ("A vyndej: \n")
    for predmet in naZitra[1]:
        print (predmet)
else:
    print ("Zitra je vikend :)")

