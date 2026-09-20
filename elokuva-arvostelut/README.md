# Elokuva-arvostelut

## Sovelluksen toiminnot

- Sovelluksessa käyttäjät voivat kirjoittaa laajoja elokuva-arvosteluja. Jokainen arvostelu koostuu otsikosta, käyttäjän kirjoittamasta tekstistä sekä kuvista (esimerkiksi kohtauksista elokuvasta), joita käyttäjä voi halutessaan lisätä.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjät voivat julkaista omia arvostelujaan, ja heillä on mahdollisus muokata tai poistaa niitä myöhemmin.
- Käyttäjät voivat selata ja lukea muiden käyttäjien kirjoittamia arvosteluja sekä arvioida ja kommentoida niitä.
- Käyttäjä voi etsiä arvosteluja avainsanojen, elokuvan nimen, arvostelun sanamäärän sekä sen perusteella, sisältääkö arvostelu spoilereita vai ei.
- Jokaisen käyttäjän sivulla näkyvät hänen kirjoittamansa arvostelut sekä niiden määrä.
- Käyttäjä voi arvostella ja kirjoittaa kommentteja muiden käyttäjien arvosteluihin.
- Jos elokuvaa, josta käyttäjä haluaa kirjoittaa arvostelun, ei ole vielä olemassa sivustolla, hän voi luoda sen itse lisäämällä elokuvan nimen ja liittämällä kuvan.

## Sovelluksen asennus
Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```