#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-
import os, sys, getopt, string
from myHttp import getHttp
from BeautifulSoup import BeautifulSoup, Tag
import time, datetime
import random
import betterImage

CARD_NOT_EXISTS = "NO CARD!"

POBIERZ_LEPSZY_IMG = True

PRINT_HEIGHT = " height=332 "
PRINT_X = 4
PRINT_Y = 2

#PRINT_HEIGHT = "  "
#PRINT_X = 3
#PRINT_Y = 3


def getAllTextFromTag(tag):
    if not isinstance(tag, Tag):
        return str(tag).replace("\n"," ").replace("\x0d","").replace("\x0a","")
    returned = []
    isCont = False
    for cont in tag.contents:
        isCont = True
        if not isinstance(cont, Tag):
            returned.append(str(cont).replace("\n"," ").replace("\x0d","").replace("\x0a",""))
        else:
            returned.append(getAllTextFromTag(cont))
    if not isCont:
        if tag.name == 'img':
            return "[%s]" % tag['src'].split("name=")[1].split("&")[0]
    return string.join(returned," ").replace("   "," ").replace("  "," ")

def pobierzKarte(nazwa):
    rarity = "common"
    typ = "unknown"
    mana = ""
    tekst = ""
    pt = ""
    cmc = 0
    ocmc = 0
    setsTab = []
    img = ""

    nazwaPliku = "temp/%s" % nazwa.replace(" ","_").replace("/","_").replace("'","")
    html = ""
    try:
        fo = open(nazwaPliku, "rt")
        html = fo.read()
        fo.close()
    except:
        html2 = getHttp("http://gatherer.wizards.com/Pages/Card/Details.aspx?name=%s" % nazwa)

        html = ""
        for x in html2:
            try:
                html += "%s" % x.decode("utf-8")
            except:
                pass

        if -1 != html.find("Your search returned zero results"):
            print "CARD NOT EXISTS! %s" % nazwa
            return CARD_NOT_EXISTS, typ, mana, tekst, pt, cmc, ocmc, img, setsTab
            
        else:
            fo = open(nazwaPliku, "wt")
            fo.write(html)
            fo.close()
    ## analyze
    soup = BeautifulSoup()
    soup.feed(html)

    div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_typeRow"})
    if div == None:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_typeRow"})
    typ = div.first("div", {"class":"value"}).string.strip()

    div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_rarityRow"})
    if div == None:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_rarityRow"})
    rarity = div.first("span").string.strip()

    div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_currentSetSymbol"})
    if div == None:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_currentSetSymbol"})
    sets = div.fetch("img", {})
    setsTab = []
    for sett in sets:
        setsTab += [sett["title"].split("(")[0].strip()]

    div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_otherSetsRow"})
    if div == None:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_otherSetsRow"})
    if div != None:
        sets = div.fetch("img", {})
        setsTab = []
        for sett in sets:
            setsTab += [sett["title"].split("(")[0].strip()]

    div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_manaRow"})
    if div == None:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_manaRow"})
    try:
        value = div.first("div", {"class":"value"})
        for img in value.fetch("img"):
            symbol = img['src'].split("name=")[1].split("&")[0]
            mana += "[%s]" % symbol
            try:
                wart = int(symbol)
            except:
                wart = 1
                ocmc += 1
            cmc += wart
    except:
        pass

    div = soup.first("div", {"class":"cardImage"})
    if div == None:
        div = soup.first("td", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl02_Td1"})
    img = div.first("img")['src'].replace("../../","http://gatherer.wizards.com/")

    try:
        div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ptRow"})
        if div == None:
            div = soup.first("div", {"id":"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent_ctl03_ptRow"})
        pt = div.first("div", {"class":"value"}).string.strip()
    except:
        pass

    texts = soup.fetch("div", {"class":"cardtextbox"})
    for t in texts:
        if len(tekst) > 0:
            tekst += " | "
        tekst += getAllTextFromTag(t)


    return rarity, typ, mana, tekst, pt, cmc, ocmc, img, setsTab

def pobierzImg(url, nazwa):
    nazwaPliku = "temp/img/%s.jpg" % nazwa.replace(" ","_").replace("/","_").replace("'","")
    try:
        fo = open(nazwaPliku, "rb")
        img = fo.read()
        fo.close()
        return nazwaPliku
    except:        
        pass
    
    htmlImg = getHttp(url)
    fo = open(nazwaPliku, "wb")
    fo.write(htmlImg)
    fo.close()
    return nazwaPliku
    

def pobierzCene(nazwa, page):
    return "0"

    cena = ""
    nazwaPliku = "temp/price__%d_%s" % (page, nazwa.replace(" ","_").replace("/","_").replace("'",""))
    html = ""
    zapiszPlik = False
    try:
        fo = open(nazwaPliku, "rt")
        html = fo.read()
        fo.close()
    except:
        html2 = getHttp("https://www.magiccardmarket.eu/?mainPage=advancedSearch&resultsPage=%d&cardName=%s" % (page, nazwa.replace(" ", "+")))
        html = ""
        for x in html2:
            try:
                html += "%s" % x.decode("utf-8")
            except:
                pass
        zapiszPlik = True
    ## analyze
    soup = BeautifulSoup()
    soup.feed(html)

    price = None
    for tr in soup.fetch("tr", {"class":lambda x: x and x.replace("row_","")!=x}):
        classes = ""
        try:
            classes = tr['class']
        except:
            pass
        if classes.replace("row_", "") != classes:
            td1 = tr.first("td", {"class":lambda x: x and x.replace("col_4","")!=x})
            td2 = tr.first("td", {"class":lambda x: x and x.replace("col_6","")!=x})
            if td1 != None and td2 != None:
                name = getAllTextFromTag(td1)
                list_price = getAllTextFromTag(td2)
                if name.split(" (Version ")[0].lower() == nazwa.lower():
                    list_price = list_price.replace(" &#x20AC;","")
                    try:
                        list_price = float(list_price.replace(",","."))
                    except:
                        list_price = None
                    print list_price
                    if list_price != None:
                        if price is None or list_price < price:
                            price = list_price
    if html.find("Next page") > 0:
        price2 = pobierzCene(nazwa, page+1)
        if price == None:
            price = price2
        elif price2 == None:
            price = price
        else:
            if price2 < price:
                price = price2

    if price != None:
        cena = str(price)

    if zapiszPlik and price != None:
        fo = open(nazwaPliku, "wt")
        fo.write(html)
        fo.close()

    return cena


def kolejneRandomem(zIlu, ile):
    rr = range(zIlu)
    random.shuffle(rr)
    random.shuffle(rr)
    random.shuffle(rr)
    random.shuffle(rr)
    random.shuffle(rr)
    return rr

g_idd = 0


def drukujListe(lista):
    global g_idd
    ret = ""
    for x in lista:
        g_idd += 1
        idd = "idAnal_%d" % g_idd
        ret += """<a href="http://gatherer.wizards.com/Pages/Card/Details.aspx?name=%s"
                    onmouseover='document.getElementById("%s").style.visibility="visible";'
                    onmouseout='document.getElementById("%s").style.visibility="hidden";'
                  >%s</a>
                  <div id='%s' style='position:absolute; visibility:hidden;'><img src='%s' width='200'/></div>
                  """ % (x[0], idd, idd, x[0], idd, x[3])
        ret += "<br>"
    return ret

def sortujPoKoszcie(a, b):
    #   karta = [nazwa, cmc, typ, nazwaImg]
    x = a[1] - b[1]
    if x != 0:
        return x
    return cmp(a[0], b[0])

def opiszKarty(lista, tura):
    ret = ""
    lista.sort(sortujPoKoszcie)
    i = 0

    typL = 0
    typC = 0
    typInne = 0
    for x in lista:
        if x[2].startswith('Land') or x[2].startswith('Basic Land'):
            typL += 1
        elif x[2].startswith('Creature'):
            typC += 1
        else:
            typInne += 1

    ret += "<br><br>Landy:%d" % typL
    ret += "<br>Potwory:%d" % typC
    ret += "<br>Inne:%d" % typInne

    landy = 0
    while i < tura:
        if lista[i][2].startswith('Land') or lista[i][2].startswith('Basic Land'):
            landy+=1
        i += 1
    color = 'black'
    if landy >= tura:
        color = 'green'
    elif landy*2 < tura:
        color = 'red'
    ret += "<br><br><font color='%s'>Landy na stole:%d</font>" % (color, landy)
    i = 0
    stac = []
    niestac = []
    while i < len(lista):
        if lista[i][2].startswith('Land') or lista[i][2].startswith('Basic Land'):
            pass
        else:
            if lista[i][1] <= landy:
                stac += [lista[i]]
            else:
                niestac += [lista[i]]
        i += 1
    lastx = ""
    ret += "<br><font color=green>Stac na:"
    for x in stac:
        if x != lastx:
            ret += "<br>%s" % x[0]
        lastx = x
    ret += "</font>"
        
    lastx = ""
    ret += "<br><font color=red>Nie stac na:"
    for x in niestac:
        if x != lastx:
            ret += "<br>%s" % x[0]
        lastx = x
    ret += "</font>"
    
    return ret

def przykladowyDraw(analizaDraw, ileTur, ktory=0):

    if len(analizaDraw) < 60:
        return ""

    ids = kolejneRandomem(len(analizaDraw), 18)

    reka = []
    for x in range(7):
        reka += [analizaDraw[ids[x]]]
    reka.sort(sortujPoKoszcie)

    if ktory > 2:
        return ""


    lands= 0
    for x in reka:
        if x[2].startswith('Land') or x[2].startswith('Basic Land'):
            lands += 1
    if lands < 2:
        return przykladowyDraw(analizaDraw, ileTur, ktory+1)
    
    ret = "<tr>"
    ret += "<td valign=top>"
    if (ktory > 0):
        ret += "Muligany: %d<br>" % ktory
    ret += drukujListe(reka)
    ret += opiszKarty(reka, 1)
    # analiza
    ret += "</td>"
    
    for i in range(ileTur):
        ret += "<td valign=top>"
        ret += drukujListe([analizaDraw[ids[i+7]]])
        # analiza
        reka += [analizaDraw[ids[i+7]]]
        ret += opiszKarty(reka, 2+i)
        ret += "</td>"
        
    ret += "<td valign=top>"
    analizaDalsze = []
    for i in range(7+ileTur, 7+ileTur+5):
        analizaDalsze += [analizaDraw[ids[i]]]
    ret += drukujListe(analizaDalsze)
    ret += "</td>"
    ret += "</tr>"
    return ret

    


def produkujPlik(plik, tworzImg):
    fo = open(plik, "rt")
    lista = fo.read().split("\n")
    fo.close()

    sumaCMC = 0
    liczbaCMC = 0
    
    suma = 0
    cenaAll = 0.0
    potworkow = 0
    power = {}
    tough = {}

    analizaDraw = []
    

    imgList = []
    iii = 0
    output = "";
    for x in lista:
        if len(x) > 3 and not x.startswith("#"):
            ilosc = int(x.split("x")[0].strip())
            nazwa = x[x.find("x")+1:].strip()
            print "  %d x %s" % (ilosc, nazwa)

            rarity, typ, mana, tekst, pt, cmc, ocmc, img, setsTab = pobierzKarte(nazwa)
            cena = ""
            if rarity != CARD_NOT_EXISTS:
                cena = pobierzCene(nazwa, 0)

            nazwaImg = ""
            if img != "" and tworzImg:
                nazwaImg = pobierzImg(img, nazwa)
                jestLepszy = False
                if POBIERZ_LEPSZY_IMG:
                    nowyImg = ""
                    for sett in setsTab:
                        nowyImg = betterImage.pobierzNowy(nazwa, sett)
                        if nowyImg != "":
                            nazwaImg = "temp/imgpng/%s.png" % nowyImg
                            jestLepszy = True
                            break
                
                for i in range(ilosc):
                    if jestLepszy:
                        imgList += [nazwaImg]
                    else:
                        imgList = [nazwaImg] + imgList
            iii += 1
            divid = "id_%d" % iii                    
            output += "\n"
            output += "<tr nowrap><td>%d</td>" % ilosc
            output += "<td>%s</td>" % rarity
            output += """<td><a href="http://gatherer.wizards.com/Pages/Card/Details.aspx?name=%s"
                         onmouseover='document.getElementById("%s").style.visibility="visible";'
                         onmouseout='document.getElementById("%s").style.visibility="hidden";'
                        >%s</a>
                        <div id='%s' style='position:absolute; visibility:hidden;'><img src='%s'  width='200'></div>
                        </td>""" % (nazwa, divid, divid, nazwa, divid, nazwaImg)
            output += "<td>%s</td>" % typ
            output += "<td nowrap>%s</td>" % mana
            output += "<td nowrap>%s</td>" % cmc
            output += "<td>%s</td>" % tekst
            output += "<td nowrap>%s</td>" % pt
            if pt != "" and pt.find("/") > 0:
                potworkow += ilosc
                p = pt.split("/")[0].strip()
                t = pt.split("/")[1].strip()
                try:
                    power[p] += ilosc
                except:
                    power[p] = ilosc
                try:
                    tough[t] += ilosc
                except:
                    tough[t] = ilosc
            cenaIlosc = ""
            znakCeny = ""
            if cena != "":
                cenaIlosc = ilosc * float(cena)
                cenaIlosc = "%.2f" % cenaIlosc
                if float(cena) >= 1.0:
                    znakCeny = "DROGIE!<br>"
            else:
                znakCeny = "BRAK!"
            output += "<td nowrap>%s%s</td>" % (znakCeny, cena)
            output += "<td nowrap>%s</td>" % cenaIlosc
            output += "</tr>"
            suma += ilosc
            if cena != "":
                cenaAll += ilosc * float(cena)
            if cmc > 0:
                sumaCMC += ilosc * cmc
                liczbaCMC += ilosc

            # analiza draw
            karta = [nazwa, cmc, typ, nazwaImg]
            for iteri in range(ilosc):
                analizaDraw += [karta]

    output += "<tr><td align=right colspan=8>Cena w sumie</td><td nowrap>%.2f</td></tr>" % cenaAll
    
    if (liczbaCMC > 0):
        output += "<tr><td align=right colspan=5>Sredni CMC dla CMC>0</td><td nowrap>%.2f</td></tr>" % (1.0*sumaCMC/liczbaCMC)


    output += "<tr><td align=right colspan=6>Zestawienie potworkow</td><td nowrap>"
    output += "W SUMIE POTWOROW: %d<br>" % potworkow
    output += "Power list: [ile razy] x [power]"
    for x in power:
        output += "<br>%d x %s" % (power[x], x)
    output += "<br>Toughness list: [ile razy] x [toughness]"
    for x in tough:
        output += "<br>%d x %s" % (tough[x], x)
        

    output += "</td></tr>"


    print "W SUMIE KART: %d" % suma
    print "ZA KWOTE W EURO: %.2f" % cenaAll

    analizaDrawTxt = "<table border='1'>"
    analizaDrawTxt += "<tr>"
    analizaDrawTxt += "<th>Ręka na start</th>"
    ileTur = 6
    ileDrawow = 4
    for i in range(ileTur):
        analizaDrawTxt += "<th>%d tura</th>" % (i+2)
    analizaDrawTxt += "<th>kolejne karty</th>"
    analizaDrawTxt += "</tr>"
    if tworzImg:
        for i in range(ileDrawow):
            analizaDrawTxt += przykladowyDraw(analizaDraw, ileTur)
    analizaDrawTxt += "</table>"


    
    fo = open(plik.replace(".txt", ".html"), "wt")
    fo.write("""<html>
        <body><table border="1"><tr>
        <th>Liczba sztuk</th>
        <th>Rarity</th>
        <th>Nazwa</th>
        <th>Typ</th>
        <th>Mana</th>
        <th>CMC</th>
        <th>Tekst</th>
        <th>P/T</th>
        <th nowrap>Cena Euro</th>
        <th nowrap>Cena*Ilosc</th>
        </tr>\n
        """)
    fo.write(output)
    fo.write("""\n</table><br>%s</body></html>""" % analizaDrawTxt)
    fo.close()


    # zapis images
    fo = open(plik.replace(".txt", "_img.html"), "wt")
    x = PRINT_X
    y = PRINT_Y
    i = 0
    fo.write("""
        <html>
        <body>
        <style>
            table { border:none; border-image-width:0 0 0 0;
                    margin: 0;  border-spacing:0; 
                    border-collapse: collapse;
                    padding: 0;
                    border: 0;}
	    td {spacing:0; padding: 0; border:none;
                border-image-width:0 0 0 0;
                margin: 0; }
        </style>
	<table>
        <tr>\n
        """)
    for img in imgList:
        i += 1
        fo.write("\n<td><img src='%s' %s/></td>" % (img, PRINT_HEIGHT))
        if i%x == 0:
              fo.write("\n</tr>")
        if i%(x*y) == 0:
              fo.write("\n</table>\n<p style='page-break-after:always;'></p>\n<table>\n")
        if i%x == 0:
              fo.write("\n<tr>")

    fo.write("\n</tr>\n</table>\n</body>\n</html>")        
    fo.close()
              
def main():
    print "Otwieram plik %s" % sys.argv[1]

    img = False
    if (len(sys.argv) > 2):
        if sys.argv[2] == 'img':
            img = True
        
       
    
    produkujPlik(sys.argv[1], img)


    print "END OF MAIN"





if __name__ == "__main__":
    main()

