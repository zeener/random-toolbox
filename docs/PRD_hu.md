# Termékkövetelmény Dokumentum - Random Toolbox

## Bevezetés
A Random Toolbox egy sokoldalú parancssori eszközkészlet és API fejlesztők számára. Egyszerű eszközöket biztosít helyőrző adatok, biztonságos hitelesítő adatok és erős jelszavak generálására, elérhető CLI-n keresztül vagy RESTful API-n keresztül.

## Funkciók
- **CLI Eszközök**: Parancssori interfész az azonnali adatgeneráláshoz.
- **RESTful API**: API végpontok alkalmazásokba való integráláshoz.
- **Véletlenszerű Szöveg Generátor**: Helyőrző szövegek generálása (bekezdések, mondatok, szavak) UI/UX makettekhez és adatfeltöltéshez.
- **API Kulcs Generátor**: Egyedi, kriptográfiailag biztonságos API kulcsok létrehozása.
- **Jelszó Generátor**: Erős, véletlenszerű jelszavak előállítása konfigurálható követelményekkel.

## Követelmények
- **Telepítés**: Repository klónozása és függőségek telepítése pip-pel.
- **Használat**: CLI parancsok és API végpontok biztosítása példákkal.
- **Biztonság**: A generált kulcsok és jelszavak kriptográfiailag biztonságosak legyenek.

## Felhasználói Történetek
- Fejlesztőként szeretnék véletlenszerű szöveget generálni UI elrendezések teszteléséhez.
- Fejlesztőként szeretnék biztonságos API kulcsokat létrehozni alkalmazásaimhoz.
- Fejlesztőként szeretnék erős jelszavakat generálni, amelyek megfelelnek a biztonsági szabványoknak.

## Elfogadási Kritériumok
- A CLI eszközök könnyen használhatók legyenek világos parancsokkal.
- Az API helyesen válaszoljon GET kérésekre.
- A generált adatok véletlenszerűek és biztonságosak legyenek.