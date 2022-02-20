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
        
        if "refreshtoken" in login:
            prihlasovaciUdaje = {
                "client_id": "ANDR",
                "grant_type": "refresh_token",
                "refresh_token": login["refreshtoken"]
            }
        else:
            prihlasovaciUdaje = {
                "client_id": "ANDR",
                "grant_type": "password",
                "username": login["username"],
                "password": login["password"]
            }
        
        auth = requests.post(
            self.adresa + "/login",
            headers={"Content-type": "application/x-www-form-urlencoded"},
            data=prihlasovaciUdaje
        ).json()
        
        self.refreshtoken = auth["refresh_token"]
        self.token = auth["access_token"]
        
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


    def rozvrh(self, den): # Vraci json s rozvrhem pro dany den a vytvori promenou schedule se stejnym obsahem
        
        # Zformatuje datum (YYYY-MM-DD) aby bylo pouzitelne v nasledujicim requestu
        datum = den.strftime('%Y-%m-%d')
        
        # Ziskani rozvrhu
        schedule = requests.get(
            self.adresa + "/3/timetable/actual",
            headers={"Content-type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {self.token}"},
            params={"date": datum}
        ).json()
        
        # Ziska nazvy predmetu a vytvori dict key id:nazev pro kazdy predmet
        nazvyPredmetu = {}
        predmety = schedule["Subjects"]
        for predmet in predmety:
            nazvyPredmetu[predmet["Id"]] = predmet["Name"]
        
        self.schedule = []
        cisloDnu = den.weekday() # Rozsah 0..6
        
        # Pokud je den vyssi nez 4 (je sobota nebo nedele) tak se snizi zpatky na 4
        if cisloDnu > 4:
            cisloDnu = 4
        
        # Vytvori list s rozvrhem pro kazdy den
        dny = list(den["Atoms"] for den in schedule["Days"])
        
        # Prida nazvy hodin do self.schedule
        for hodina in dny[cisloDnu]:
            if hodina["SubjectId"] != None:
                self.schedule.append(nazvyPredmetu[hodina["SubjectId"]])
        
        return self.schedule


def vzitNa(dnesniRozvrh, zitrejsiRozvrh): # Vraci list se dvema listy, prvni obsahuje predmety co do tazky pridat, druhy co z ni vyndat
    
    pridat = []
    odebrat = []
    
    # Pokud je hodina dnes a nebyla vcera, prida se do promene pridat, pokud byla vcera a neni dnes, prida se do promene odebrat
    for hodina in zitrejsiRozvrh:
        if hodina not in dnesniRozvrh:
            pridat.append(hodina)
    
    for hodina in dnesniRozvrh:
        if hodina not in zitrejsiRozvrh:
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
        options = input("Moznosti ulozeni prihlaseni: \n1) Ulozit refresh token a adresu\n2) Ulozit jmeno, heslo a adresu\n3) Nic neukladat\n")
        
        # Ulozi zadana data do souboru
        if options == "1":
            json.dump({"refreshtoken": uzivatel.refreshtoken, "url": adresa}, file)
        elif options == "2":
            json.dump({"username": jmeno, "password": heslo, "url": adresa}, file)
    else:
        # Obsah souboru pouzije pro prihlaseni
        fileContentsJson = json.loads(fileContents)
        uzivatel = Bakalari(fileContentsJson, fileContentsJson["url"])
        
        # Ulozi nove vygenerovany refresh token
        if "refreshtoken" in fileContentsJson:
            file.seek(0)
            fileContentsJson["refreshtoken"] = uzivatel.refreshtoken
            json.dump(fileContentsJson, file)
    
    dnes = datetime.datetime.today()
    zitra = datetime.datetime.today() + datetime.timedelta(days=1)
    
    # Pokud neni zitra vikend, zobrazi se co si na zitrek vzit a co vyndat
    if zitra.isoweekday() != 6 and zitra.isoweekday() != 7:
        dnesniRozvrh = uzivatel.rozvrh(dnes)
        zitrejsiRozvrh = uzivatel.rozvrh(zitra)
        
        naZitra = vzitNa(dnesniRozvrh, zitrejsiRozvrh)
        
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

