---
title: "RSS má 27 rokov a stále drží spravodajstvo pohromade"
perex: "Formát z roku 1999 prežil portál, pre ktorý vznikol, aj najpopulárnejšiu čítačku. Dnes z neho žijú podcasty a čoraz častejšie aj AI agenti."
sekcia: softver
tagy: ["RSS", "Atom", "otvorené štandardy"]
publikovane: 2026-11-12T08:00:00+01:00
obrazok:
  src: /obrazky/vzor-rss.svg
  alt: "Oranžový bod, z ktorého vychádzajú dva sústredné oblúky, symbol RSS kanála"
  popisok: "Symbol kanála: bod a dve vlny."
  kredit: "Bitoviny"
  licencia: "vlastná ilustrácia"
zdroje:
  - nazov: "RSS 2.0 Specification, RSS Advisory Board"
    url: "https://www.rssboard.org/rss-specification"
  - nazov: "RFC 4287: The Atom Syndication Format"
    url: "https://www.rfc-editor.org/rfc/rfc4287"
  - nazov: "A second spring of cleaning, Google Official Blog"
    url: "https://googleblog.blogspot.com/2013/03/a-second-spring-of-cleaning.html"
vzorovy: true
---

Keď v marci 1999 Netscape zverejnil RSS 0.90, mal to byť spôsob, ako dostať titulky cudzích webov na portál My Netscape. Portál dávno neexistuje. Formát áno.

## Čo to vlastne je

RSS je obyčajný súbor XML, ktorý web zverejňuje na pevnej adrese. Obsahuje zoznam najnovších položiek: titulok, odkaz, dátum, krátky opis, niekedy celý text. Program, ktorý ten súbor pravidelne číta, vie, čo je nové, bez toho, aby musel rozumieť vzhľadu stránky.

Dnes sa používajú dve príbuzné podoby.

- **RSS 2.0** z roku 2002, ktorého špecifikáciu spravuje RSS Advisory Board.
- **Atom**, ktorý v decembri 2005 vyšiel ako internetový štandard RFC 4287 a niektoré nejasnosti RSS upratal.

Pre čitateľa je rozdiel neviditeľný, čítačky zvládajú oba.

## Pohreb, ktorý sa nekonal

Najväčšiu ranu dostal formát v roku 2013. Google v marci oznámil a 1. júla vykonal koniec čítačky Google Reader. Mnohí vtedy RSS odpísali spolu s ňou.

Stalo sa niečo iné. Kanály zo spravodajských webov nezmizli a miesto jednej čítačky zaujalo niekoľko menších. A hlavne: na RSS stojí celý svet podcastov. Každá relácia je kanál, v ktorom má epizóda priložený zvukový súbor.

## Prečo sa hodí strojom

Pre automatizované systémy je RSS pohodlnejší než samotná stránka. Je štruktúrovaný, malý a vydavateľ ho zverejňuje práve preto, aby ho čítali programy.

Aj redakcia Bitovín začína deň pri RSS. Zberač prejde kanály vybraných portálov a až potom, ak v kanáli chýba celý text alebo obrázok, siahne po samotnej stránke.

## Čo si z toho odniesť

Technológie, ktoré vydržia desaťročia, bývajú jednoduché a nikomu nepatria. RSS spĺňa oboje.
