# Robottiohjelmoinnin harjoitustyö
## Doge-(aka koira)-bot

Koirabotti seuraa webcamin avulla oranssia it-konferenssista saatua stressipalloa,
tarttuu siihen kourilla,
ja tuo sen lopuksi vihreä värillä merkittyyn lähtöpaikkaansa.
Seinien ja esteiden välttely ei kuulu koirabotin toimenkuvaan vaan silloin http://imgur.com/gallery/Dl6PLBd

![Yleiskuva](/docs/kuvat/yleiskuva.jpg "Yleiskuva")
Video: https://www.youtube.com/watch?v=isHXTbQbh4o

## Hardware

- NXT, jossa leJOS
    - 2 servoa edessä ajamiseen
    - 1 servo päällä kouria ohjaamaan
- eMachines eM350-miniläppäri
    - 25.8 cm x 18.5 cm x 2.5 cm
    - 1.2 kg
- Logitech, Inc. HD Webcam C510
    - turha kääntyvä osa poistettu voimalla

## Rakenne

Ajavien servojen perusrakenne pohjautuu sivun http://www.nxtprograms.com/NXT2/race_car/steps.html vaiheisiin 1-5,
joskin rakennetta on levennetty hieman ja rattaat/välitykset ovat eripäin vääntöä lisäämässä rakennelman yhteispainon (yli 2 kg) takia.
Takaosassa on yksi pieni ei-kääntyvä rengas (kaikki kääntyvät rengassysteemit toimivat huonosti painon takia.
Itse läppäri kiinnittyy pohjaan ilmastointiteipillä.
Muu osuus (brick + kouran servo) on saranoitu läppärin ympärille siten, että läppärin kannen saa vähällä purkamisella auki.
Erityisesti brickiä ei ole kiinnitetty mitenkään läppärin kanteen, vaan leijuu.

![](/docs/kuvat/yla.jpg)
![](/docs/kuvat/sivu.jpg)
![](/docs/kuvat/etu.jpg)
![](/docs/kuvat/ala.jpg)
![](/docs/kuvat/auki.jpg)
![](/docs/kuvat/ilman_konetta.jpg)
![](/docs/kuvat/kameran_kiinnitys.jpg)
![](/docs/kuvat/servot.jpg)
![](/docs/kuvat/lapileikkaus.jpg)
![](/docs/kuvat/takapyora.jpg)
![](/docs/kuvat/pallokuva.jpg)

## Ohjelmisto

### NXT-brickin softa

NXT:llä pyörii leJOS-softa, joka lukee USB-yhteyden yli leJOS:n Socket-luokan avulla viestejä,
ja ohjaa servoja sen perusteella. Kommunikaatio on yksisuuntainen (PC -> NXT).

Käynnistymisen yhteydessä kouran servot pyöritetään tunnettuun asentoon (ja resetoi kierroslukeman) nostamalla kouraa kunnes servon `isStalled()` palauttaa `true`.
Tämän jälkeen kouran voi avata ja sulkea käyttämällä `rotateTo(0)` ja `rotateTo(-115)`.
Ajamiseen käytetään `DifferentialPilot`ia.
USB:n yli voi lähettää seuraavia komentoja (yksi ASCII-tavu / komento):

- `, o a e` (WASD dvorak-näppäimistöllä) - Ohjaus eteen, taakse, vasemmalle, oikealle. Käännökset tapahtuvat paikallaan (zero radius turn). Tarkempi kääntyminen on mahdollista, kts. alla.
- `Space` - Pysähdys.
- `1 2 3` - Ajonopeuden säätö. Lähinnä manuaalista ajoa varten, varsinainen robosofta ajaa aina täysii.
- `+ -` - Koura kiinni / auki.
- `r` - Kouran servon uudelleenkalibrointi.
- `A - Z` - Hienovaraisempi kääntyminen. Kirjain tulkitaan lukuna välillä 0 -- 25,
            jossa luvun alin bitti kertoo kääntymisen suunnan (vasen/oikea) ja loput bitit kääntymisnopeuden (lineaarisesti verrannollinen `DifferentialPilot`-luokan `steer`-metodin `turnRate`-parametriin).
- `b` - Beep. For lulz.
- `q` - `System.exit(0)`, paluu takaisin valikkoon / fläshäystilaan.

### Läppärin softa

Suurin osa logiikasta pyörii vanhalla Arch Linuxilla varustetulla Acerin miniläppärillä.
Itse softa on Pythonin OpenCV-bindingejä käyttävä graafinen X-sovellus,
joten sen ajamiseen etänä täytyy käynnistää VNC-palvelin.
Ohjelma kaappaa luupissa kuvia webcamista, ja joka framella päättää mitä komentoja lähetetään robotille.

Videosta https://www.youtube.com/watch?v=isHXTbQbh4o voi nähdä neljä tilaa, jotka ohjelma käy läpi:
    - Pallon suuntaan ajaminen
    - Pallon kaappaus sulkemalla koura, kun robotti on tarpeeksi lähellä palloa
    - Lähtöpaikan (vihreä kassi) etsintä
    - Lähtöpaikan suuntaan ajaminen

Pallon ja lähtöpaikan paikantaminen perustuu värisävyjen tunnistamiseen.
OpenCV:llä tehdään kaapattuun frameen seuraavat käsittelyt:
    - Kuvan kääntö 180 astetta, koska kamera on asennettu ylösalaisin.
    - Muunnetaan kuva HSV-väriavaruuteen.
    - Etsitään OpenCV:n `inRange()`-funktiolla pikselit joiden väriarvo on tietyllä välillä.
      Oranssille pallolle lukuväli on (6, 90, 40) - (13, 255, 255), vihreällä kotipaikalle (44, 90, 40) - (54, 255, 255).
      Oranssin pallon lukuväliä voi säätää lennosta käyttöliittymän slidereillä, virheän värin arvot on kovakoodattu.
      Tuloksena mustavalkobitmap, jossa valkoiset pikselit ovat värialueen sisällä ja mustat ulkopuolella.
    - Etsitään OpenCV:n `findContours()`-funktiolla edellisen vaiheen kuvasta yhtenäiset valkoiset alueet ja niiden bounding boxit.
    - Järjestetään bounding boxit koon mukaan (kriteeriksi valittu leveys + korkeus)
    - Nyt pallo/kotipaikka löytyy suurimman bounding boxin, joka ylittää minimikoon 50, keskipisteestä.
Jos pallo/kotipaikka löydettiin kuvasta, lähetetään robotille kääntymiskomento (A-Z) sen mukaan kuinka kaukana kohde on kuvan keskipisteestä.
Mikäli kohdetta ei löytynyt kuvasta, käsketään robottia pysähtymään.

Koska kamera on kiinnitetty pallon halkaisijaa korkeammalle,
katoaa pallo kameran kuvasta kun se on tarpeeksi lähellä,
ja siinä kohtaa softa sulkee kouran.

Kun koura on suljettu, alkaa robotti pyörimään paikallaan oikealle ja etsimään kotipaikkaa.

Kun robotti pyöriessään löytää virheän kohteen, jonka bounding boxin koko (leveys + korkeus) on yli 150, alkaa robotti ajaa sitä kohti, samaan tapaan kuin palloa etsittäessä.

## Testaus

### Manuaaliohjaus

Käynnistämällä leJOS-ohjelman ja ajamalla SSH:n yli `scripts/console.sh` saa livekonsolin jolla komentoja voi syöttää käsin.
Tällä voi sanity testata, että servot on kytketty oikein päin (kääntyminen oikealle/vasemmalle kääntää oikeaan suuntaan), kouran avaus/sulkeminen toimii, ym. mekaanisia ongelmia.

Testi onnistui, robotilla voi ajaa onnistuneesti ja koura toimii. Joskin robotilla on taipumus kääntyä helpommin oikealle kuin vasemmalle; johtuen luultavasti läppärin painopisteen olevan jossain muualla kuin keskellä.

### OpenCV-logiikan kalibrointi/testaus

Ajamalla VNC:n yli `python2 opencv.py -t` saa ajettua PC-puolen softan niin, että robotille lähtevät komennot menevät `/dev/null`iin.
Tällä voi varmistua, mm. siitä, että OpenCV kaappaa kuvat ulkoisesta webcamista eikä läppärin sisäisestä webcamista,
ja että tunnistaako robotti pallon nykyisessä valaistuksessa.

Testi onnistui, joskin robotti sekoittaa helposti laitoksen puiset tuolit sekä Topin punaisen paidan palloon.
Värifiltterin tuunaukseen olisi pitänyt käyttää enemmän aikaa, ja varmaan olisi myös ollut fiksua eikä edes liian työlästä tallettaa läjä kuvankaappauksia palloista/tuoleista eri valaisuuksissa,
ja tehdä automaattiset yksikkötestit sille.

### Robotin käyttö
Käynnistämällä leJOS-ohjelman ja ajamalla VNC:n yli `python2 opencv.py` (ilman edellä käytettyä `-t`-parametriä) saa ajettua robon tositoimissa. Pitäisi siis tapahtua:
    - Pallon suuntaan ajaminen
    - Pallon kaappaus sulkemalla koura, kun robotti on tarpeeksi lähellä palloa
    - Lähtöpaikan (vihreä kassi) etsintä
    - Lähtöpaikan suuntaan ajaminen

Tämän testin tulos on kuvattu edellä linkatussa youtube-videossa, eli ihan onnistunut.
Joskin vaatii useamman yrityksen, koska koura ei aina saa pallosta tarpeeksi hyvää otetta.

# Rajoitukset

Viimeistelyä ja hienosäätöä pitäisi olla enemmän:
 - pitäisi laskea optimaalinen kääntymismäärä (`turnRate`) funktiona pallon x-koordinaatin suhteen, nykyinen malli on lähinnä hatusta heitetty
 - värintunnistus kaipaisi automaattisia testejä / testidataa kuvina sopivien parametrien valintaan
 - kouran sivuille tarvittaisiin joku rakennelma estämään pallon liukumisen pois kouran alta robotin pyöriessä paikallaan
 - mekaaninen rakenne vaatisi paremman takapyörän sekä luultavasti renkaiden etäisyyksien mitoittamisen järkevästi kääntymisen parantamiseksi

Myöskin ilmeisesti leJOS 0.9.1:ssä (mutta ei 0.9.0:ssa) servo-ohjauksessa näyttäisi olevan jotain bugeja silloin kun servojen pyöriminen estyy liikaa -
esim. servon pysäytys muuttuu välillä mahdottomaksi

# Käyttöohje
leJOS-softan kääntö & flashaus voidaan tehdä devausläppärillä - IntelliJ IDEA:ssa 'Flash over SSH'-ajokonfiguraatio kääntää Java-koodin nxj-tiedostoksi,
ajaa skriptin `scripts/flash-ssh.sh`, joka kopioi sen ssh:lla robotin miniläppäriin (kovakoodattu osoite `acer.dezgeg.me`) ja ajaa `nxjupload`:in myös ssh:n yli.

Kun NXT-softa on käynnistetty, pitää robotin miniläppärillä käynnistää (esim. SSH:n yli) `nxjsocketproxy` skriptillä `scripts/proxy.sh`, joka putkittaa NXT:n usb-liikenteen
`/tmp/nxt`-nimiseen named pipeen, johon muu koodi kirjoittaa.

Tämän jälkeen voidaan käynnistää joko `scripts/console.sh` SSH:n yli tai `python2 opencv.py` VNC:n yli,
jotka on selitetty testauskappaleessa.

## OpenCV-kälin selitys
![](/docs/kuvat/screenshot.jpg)

- slidereillä säädetään oranssin värin tunnistamisen min/max-rajoja
- punainen laatikko on tunnistetun kappaleen bounding box
- punaisella oleva lukuarvo on bounding boxin koko (leveys + korkeus)
- vihreä piste on tunnistetun kappaleen keskipiste
- siniset + valkoiset pystyviivat ovat kääntymismäärän rajoja 
- sininen lukuarvo on robotille annettava nykyinen kääntymismäärä
