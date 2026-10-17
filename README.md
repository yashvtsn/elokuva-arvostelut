# Elokuva-arvostelut

## Sovelluksen toiminnot
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään ja ulos
- Käyttäjät voivat julkaista omia arvostelujaan. Arvostelulla on otsikko ja teksti.
- Käyttäjä voi muokata ja poistaa omia arvostelujaan
- Käyttäjät voivat selata ja lukea muiden käyttäjien kirjoittamia arvosteluja ja kommentoida niitä.
- Käyttäjä voi valita arvostelulle luokkiteluja: elokuvan genre ja sisältääkö arvostelu spoileria
- Käyttäjä voi lisätä kuvia arvosteluun (JPEG-tiedosto, enintään 100kt) ja poistaa niitä
- Jokaisen käyttäjän sivulla näkyvät hänen kirjoittamansa arvostelut sekä niiden määrä.
- Arvosteluja voi hakea hakusanalla.
- Lomakkeiden syötteet tarkistetaan ja virheistä näytetään ilmoitus. Lomakkeet on suojattu CSRF-hyökkäyksillä.
  
## Sovelluksen asennus
1. Asenna `flask`-kirjasto:

```
$ pip install flask
```

2. Luo tietokanta 'database.db':

```
$ sqlite3 database.db < schema.sql
<<<<<<< Updated upstream
=======
$ sqlite3 database.db < init.sql
>>>>>>> Stashed changes
```
3. Voit käynnistää sovelluksen näin:

```
$ flask run

```

