#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-
import os, sys, getopt, string, urllib, urllib2
import threading, math
import httplib
import  random, time, socket
from httplib import HTTPConnection, HTTPException
import cookielib
import json
import codecs

G_LICZNIK_POBRAN = 0
G_STRONA = ""
g_lista_plikow = []
## ZMIENNE USTAWIANE
g_slownik = {}

## inicjalnie
g_slownik['DEBUG'] = {}
g_slownik['DEBUG']['LEVEL'] = '0'

def mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

jar = cookielib.CookieJar()

# All functions related to retrieving data from other servers
# those headers are supposed to mimic FireFox
user_agent_hdr = "User-Agent"
user_agent_val = "Mozilla/5.1 (Windows; U; Windows NT 5.1; pl; rv:1.7.5) Gecko/20041107 Firefox/2.0"

accept_hdr = "Accept"
accept_val = "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5"

accept_lang_hdr = "Accept-Language"
accept_lang_val = "pl,en-us,en;q=0.5"

# don't give that, not sure if python handles it
# Accept-Encoding: gzip,deflate

accept_encoding_hdr = "Accept-encoding"
accept_encoding_val = "gzip"

content_encoding_hdr = "Content-Encoding"

accept_charset_hdr = "Accept-Charset"
accept_charset_val = "ISO-8859-2,utf-8;q=0.7,*;q=0.7"

keep_alive_hdr = "Keep-Alive"
keep_alive_val = "500"

connection_hdr = "Connection"
connection_val = "keep-alive"

referer_hdr = "Referer"

location_hdr = "Location"

# a class to trick urllib2 to not handle redirects
class HTTPRedirectHandlerNoRedirect(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        pass

def _getHttpHelper(url, postData, handleRedirect, dbgLevel, referer, cookieJar):
    global G_LICZNIK_POBRAN, g_slownik
    import cookielib
    G_LICZNIK_POBRAN += 1
    
    url = url.replace(" ", "%20")
    req = urllib2.Request(url)
    req.add_header(user_agent_hdr, user_agent_val)
    req.add_header(accept_hdr, accept_val)
    req.add_header(accept_lang_hdr, accept_lang_val)
    req.add_header(accept_charset_hdr, accept_charset_val)
    req.add_header(keep_alive_hdr, keep_alive_val)
    req.add_header(connection_hdr, connection_val)
    if None != referer:
        req.add_header(referer_hdr, referer)
    if None != postData:
        if len(postData) == 1:
            data = 'json='+postData['json']
            req.add_data(data)
        else:    
#        req.add_data(urllib.urlencode(postData))
            req.add_data(postData)

    httpHandler = urllib2.HTTPHandler(debuglevel=dbgLevel)
    httpsHandler = urllib2.HTTPSHandler(debuglevel=dbgLevel)
    if cookieJar is None:
        cookieJar = cookielib.CookieJar()
        
    cookieHandler = urllib2.HTTPCookieProcessor(cookieJar)

    czyProxy = 'OFF'
    try:
        czyProxy = g_slownik['PROXY']['STATUS']
    except:
        czyProxy = 'OFF'
    proxy_support = None
    authinfo = None
    if 'ON' == czyProxy:
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, g_slownik['PROXY']['ADRES'], g_slownik['PROXY']['LOGIN'], g_slownik['PROXY']['HASLO']) 
        authinfo = urllib2.ProxyBasicAuthHandler(passmgr)
        proxy_support = urllib2.ProxyHandler({"http" : g_slownik['PROXY']['ADRES']})

    if 'ON' == czyProxy:
        opener = urllib2.build_opener(proxy_support, authinfo, cookieHandler, httpHandler, httpsHandler)
    else:
        opener = urllib2.build_opener(cookieHandler, httpHandler, httpsHandler)

    if 4 <= int(g_slownik['DEBUG']['LEVEL']):
        print "Otwieram strone %s" % url
    if 5 <= int(g_slownik['DEBUG']['LEVEL']):
        print "POST DATA: %s " % str(postData)
    url_handle = opener.open(req)
    if not url_handle:
        print 'NONE kurcze'
        return None

    headers = url_handle.info()

    # TODO: is it always present? What happens if it's not?
    encoding = url_handle.headers.get(content_encoding_hdr)

    if "gzip" == encoding:
        htmlCompressed = url_handle.read()
        compressedStream = StringIO.StringIO(htmlCompressed)
        gzipper = gzip.GzipFile(fileobj=compressedStream)
        htmlTxt = gzipper.read()
    else:
        htmlTxt = url_handle.read()

    url_handle.close()

    if url[-4:].lower()  not in ('.jpg') and 3 <= int(g_slownik['DEBUG']['LEVEL']):
        fo = open("test.htm", "wb")
        fo.write(htmlTxt)
        fo.close()    
    if 5 <= int(g_slownik['DEBUG']['LEVEL']):
        print "Dlugosc odpowiedzi: %d" % len(htmlTxt)
    return htmlTxt

def _getHttpHandleException(url, postData, handleRedirect, dbgLevel, referer, cookieJar):
    htmlTxt = None
    try:
        htmlTxt = _getHttpHelper(url, postData, handleRedirect, dbgLevel, referer, cookieJar)
    except Exception, ex:
        print  str(ex)
    return htmlTxt

# do an http request to retrieve html data for url. By default we use GET request
# if postData (a dictionary) is given we do POST request
# set handleRedirect to False to disable automatic handling of HTTP redirect (302 etc.)
# set dbgLevel to 1 to have HTTP request and response headers dumped to stdio
# to set HTTP header referer, use referer
g_ile_requestow = 0
def getHttp(url, postData = None, handleRedirect=True, dbgLevel=0, referer=None, handleException=True, cookieJar = None):
    global g_ile_requestow
    htmlTxt = None
    if handleException:
        htmlTxt = _getHttpHandleException(url, postData, handleRedirect, dbgLevel, referer, cookieJar)
    else:
        htmlTxt = _getHttpHelper(url, postData, handleRedirect, dbgLevel, referer, cookieJar)
    g_ile_requestow += 1
    if g_ile_requestow >= 100:
        g_ile_requestow = 0
    return htmlTxt

def main():
    print getHttp("http://www.wp.pl")

if __name__ == "__main__":
    main()

