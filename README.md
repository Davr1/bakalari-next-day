<h1 align="center">bakalari-next-day</h1>
  
<div align="center">
  
  Co si na zítra přidat a co z tašky vyndat podle Bakalářů.
  
  ![GitHub](https://img.shields.io/github/license/Davr1/bakalari-next-day)
  ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Davr1/bakalari-next-day)
  ![GitHub last commit](https://img.shields.io/github/last-commit/Davr1/bakalari-next-day)
  ![Support <3](https://kokolem.github.io/LGBT-friendly-rainbow.svg)
  
</div>

## O programu
*Co si na zítra přidat a co z tašky vyndat podle Bakalářů* je Python program zobrazující co si vzít a co na příští den z tašky vyndat podle rozvrhu z Bakalářů.
Po spuštění se vás zeptá na tři údaje:
- Přihlašovací jméno
- Heslo
- URL adresa Bakalářů školy (například `https://skola.bakalari.cz/bakaweb/login`)

Při prvním použití programu se vám zobrazí nabídka pro uložení přihlašovacích údajů:
1. Uložení refresh tokenu a url - refresh token bude použit při každém přihlášení pro získání tokenu, a pokaždé se přepíše soubor `bakalari-next-day.json` s novým refresh tokenem
2. Uložení jména, hesla a url - použije se normální způsob přihlášení stejně jako ve webové aplikaci, soubor se po prvním uložení už nebude přepisovat
3. Nic neukládat - soubor zůstane prázdný

Potom vám ukáže požadované informace. Mohou vypadat třeba takto:

```
Uzivatel: Petr Novotný, 1.C

Do tasky si pridej:

Dějepis
Francouzský jazyk
Fyzika
Anglický jazyk
Pracovní činnosti

A vyndej: 

Zeměpis
Tělesná výchova
```

## Závislosti
- Python 3.x
- Knihovna [requests](http://docs.python-requests.org/en/master/)
