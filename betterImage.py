#!/usr/bin/env python
import os, sys, getopt, string
from myHttp import getHttp
from BeautifulSoup import BeautifulSoup, Tag
import time, datetime
import random
from PIL import Image


def przekodujDodatek(dodatek):
    przekodowanie = {
            "unlimited-edition":"unlimited",
            "limited-edition-alpha":"alpha",
            "limited-edition-beta":"beta",
            "third-edition":"3rd-edition",
            "fourth-edition":"4th-edition",
            "fifth-edition":"5th-edition",
            "classic-sixth-edition":"6th-edition",
            "seventh-edition":"7th-edition",
            "eighth-edition":"8th-edition",
            "tenth-edition":"10th-edition",
            "eleventh-edition":"11th-edition",
            "twelveth-edition":"12th-edition",
            "thirteenth-edition":"13th-edition",
            "fourteenth-edition":"14th-edition",
            "fifteenth-edition":"15th-edition",
            "magic-the-gatheringconspiracy":"conspiracy",
            "commander-2013-edition":"commander-2013",
            "magic-origins":"magic-origins",
            "ravnica-city-of-guilds":"ravnica",
            "magic-the-gathering-commander":"commander",
            
            
        }
    try:
        nowy = przekodowanie[dodatek]
    except:
        if dodatek.replace("magic-", "") != dodatek:
            dodatek = dodatek.replace("magic-", "") + "-core-set"
        
        nowy = dodatek
    return nowy
              
def wklejka(sciezka, sciezkaPrzenies):
    img = Image.open(sciezka)
    imgbase = Image.open("temp/medium/aaa_empty_base2.png")

    old_width, old_height = img.size
    diffX = old_width - 277
    diffY = old_height - 401



    if diffX < 0 or diffY < 0 or diffX > 6 or diffY > 6:
        print "WYMIARY SKOPANE: %d %d zamiast 277x401" % (old_width, old_height)
        img.close()
        print sciezka
        print sciezkaPrzenies
        os.rename(sciezka, sciezkaPrzenies)        
        return

    if diffX > 0 or diffY > 0:
        print "LEKKO SKOPANE - sprawdz to!: %d %d zamiast 277x401" % (old_width, old_height)

    nowy_plik = "temp/imgpng/%s.png" % (sciezka.split("/")[-1].split(".")[0])


    x = 15 - diffX/2
    y = 15 - diffY/2
    imgbase.paste(img, (x, y, x+old_width, y+old_height))    
    
    imgbase.save(nowy_plik,'png')

def doUrl(x):
    x = x.replace(" ","-")
    x = x.replace("'","")
    x = x.replace(".","")
    x = x.replace("/","")
    x = x.replace(",","")
    x = x.replace(":","")
    x = x.replace(";","")
    x = x.lower()
    return x

def przygotujUrl(nazwa, dodatek):
    nazwa = doUrl(nazwa)
    dodatek = przekodujDodatek(doUrl(dodatek))
    url = "https://www.cardkingdom.com/mtg/%s/%s" % (dodatek, nazwa)
    return url
    
def przygotujPlik(nazwa, dodatek = None):
    nazwa = doUrl(nazwa).replace("-","_")
    if dodatek != None:
        dodatek = doUrl(dodatek).replace("-","_")
        nazwa = "%s__%s" % (nazwa, dodatek)
    return nazwa

def testPliku(path):
    try:
        x = open(path, "rb")
        cont = x.read()
        x.close()
        return True
    except:
        return False

def pobierzMedium(path, nazwa, dodatek):
    url = przygotujUrl(nazwa, dodatek)
    html2 = getHttp(url)
    if html2 == None:
        print "BLAD POBIERANIA URL:\n%s" % url
        return
    else:
        print " obrazek z: %s" % url

    
    html = ""
    for x in html2:
        try:
            html += "%s" % x.decode("utf-8")
        except:
            pass
    
    soup = BeautifulSoup()
    soup.feed(html)

    imgURL = ""
    div = soup.first("div", {"class":"cardLink zoomed notoggle "})
    if div != None:
        img = div.first("img")
        imgURL = img['src']
        
    if imgURL != "":
        try:
            imgContent = getHttp(imgURL)
        except:
            return
        fo = open(path, "wb")
        fo.write(imgContent)
        fo.close()

def pobierzNowy(nazwa, dodatek):
    plik = przygotujPlik(nazwa)
    medium = "temp/medium/%s.jpg" % plik
    mediumDodatek = "temp/medium/%s.jpg" % przygotujPlik(nazwa, dodatek)
    final = "temp/imgpng/%s.png" % plik
    if not testPliku(medium) and not testPliku(mediumDodatek):
        pobierzMedium(medium, nazwa, dodatek)

    if not testPliku(final) and testPliku(medium):
        wklejka(medium, mediumDodatek)

    if testPliku(final):
        return plik
    return ""


def main():
    print "TEST"

    fileName = pobierzNowy("Greater Good", "Urza's Saga")

    print fileName


    print "END OF MAIN"





if __name__ == "__main__":
    main()

