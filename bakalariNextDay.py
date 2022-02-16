#!/usr/bin/env python3

import requests
import datetime
import re
import json
import os.path

class Bakalari: # Trida pro pristup k API bakalaru
    
    
    def __init__(self, login, adresa): # Login argument je dict s uzivatelskym jmenem a heslem nebo tokenem, a adresa je url bakalaru skoly. Zadane udaje se vyuziji pri ziskavani tokenu
        
        # Odstrani prebytecny text z adresy a prida zpatky https protokol a /api endpoint
        adresa = re.sub(r"(https?:\/\/)|(\/login)|(\/$)", "", adresa)
        self.adresa = f"https://{adresa}/api"
        
        if "token" in login:
            self.token = login["token"]
        else:
            prihlasovaciUdaje = {
                "client_id": "ANDR",
                "grant_type": "password",
                "username": login["username"],
                "password": login["password"]
            }
            
            # Ziska token ze serveru bakalaru
            self.token = requests.post(
                self.adresa + "/login",
                headers={"Content-type": "application/x-www-form-urlencoded"},
                data=prihlasovaciUdaje
            ).json().get("access_token")
        
        # Ziska informace o prihlasenem uzivateli
        userdata = requests.get(
            self.adresa + "/3/user",
            headers={"Content-type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {self.token}"}
        )

        # Pokud jsou prihlasovaci udaje nebo token neplatny tak se program ukonci
        if userdata.status_code == 401:
            print("Neplatne prihlasovaci udaje")
            quit()
        self.userdata = userdata.json()
    
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

def main():

    # Zkontroluje existenci souboru bakalari-next-day.json a precte ho, pokud soubor neexistuje tak ho vytvori
    if os.path.isfile("bakalari-next-day.json"):
        file = open("bakalari-next-day.json", "r+")
    else:
        file = open("bakalari-next-day.json", "w+")
    fileContents = file.read()
    
    if fileContents == "":
        jmeno = input("Prihlasovaci jmeno: ")
        heslo = input("Heslo: ")
        adresa = input("URL adresa bakalaru skoly: ")
        
        uzivatel = Bakalari({"username": jmeno, "password": heslo}, adresa)

        print("")
        options = input("Moznosti ulozeni prihlaseni: \n1) Ulozit token a adresu\n2) Ulozit jmeno, heslo a adresu\n3) Nic neukladat\n")
        
        # Ulozi zadana data do souboru
        if options == "1":
            json.dump({"token": uzivatel.token, "url": adresa}, file)
        elif options == "2":
            json.dump({"username": jmeno, "password": heslo, "url": adresa}, file)
    else:
        # Obsah souboru pouzije pro prihlaseni
        fileContentsJson = json.loads(fileContents)
        uzivatel = Bakalari(fileContentsJson, fileContentsJson["url"])
    
    tyden = SkolniTyden(uzivatel.rozvrh())
    
    # Pokud neni zitra vikend, zobrazi se co si na zitrek vzit a co vyndat
    zitra = datetime.datetime.today().weekday()+1
    if zitra != 6 and zitra != 7:
        naZitra = tyden.vzitNa(zitra)
        
        # Odpoved
        print("")
        print(f"Uzivatel: {uzivatel.userdata['FullName']}")
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
    
    file.close()

main()

