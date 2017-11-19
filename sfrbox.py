#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
sfrbox.py -- box sfr interface v3.4

Ce script permet d'afficher certains paramètres de la box, de la redemarrer
ou d'allumer/éteindre les leds

Synopsis:
    sfrbox.py -led on
    sfrbox.py -i -c -led on
    sfrbox.py -r

voir sfrbox.py -h pour l'ensemble des commandes

Configuration:
    - Remplacer la valeur dans KEY par la clé wifi de la box.
    - Vérifier que l'ip dans URL soit la bonne

Modules requis:
    pyquery
    requests

From:
    https://github.com/1shad/sfrbox-python

"""
import sys
import hmac
import argparse
from hashlib import sha256
from pyquery import PyQuery as pq
from requests import Session


KEY = '0x0x0x0x0x0x0x0x0x0x' # <-- Clé wifi
URL = 'http://192.168.1.1/'  # <-- IP

session = Session()

#_______/ LED \______________________________________________________
def led( state ):
    """ Active ou désactive les leds """
    if 'sid' not in session.cookies:
        login()

    data = { 'leds_state': state }
    response = session.post( URL + 'state', data=data )
    
    if response.status_code != 200:
        print('Impossible de modifier le statut des leds')
    else:
        print('Leds:',state)

#_______/ REBOOT \___________________________________________________
def reboot():
    """ Redémarre la box """
    if 'sid' not in session.cookies:
        login()
    
    response = session.post( URL + 'reboot' )
    
    if response.status_code != 200:
        print("Impossible de relancer la box")
    else:
        print('Redémarrage en cours')

#_______/ CONNECTED \________________________________________________
def connected():
    """ Affiche les appareils connectés à la box """
    if 'sid' not in session.cookies:
        login()
    
    response = session.get( URL + 'network' )
    if response.status_code != 200:
        sys.exit( "Impossible de charger la page")

    d = pq( response.content )

    nodes = d('#network_clients > tbody > tr')
    nodes = [ x.find('td') for x in nodes.items() ]
    nodes = [ [ x.text.replace('\n', '').strip() for x in y ] for y in nodes ]
    for e in nodes:
        print(e[0] + ':', e[3], e[2], e[1], e[4])
    
#_______/ INFOS \____________________________________________________
def infos():
    """ Affiche quelques infos, comme l'uptime, l'etat la connexion ou l'ip """
    response = session.get( URL )

    if response.status_code != 200:
        sys.exit("Impossible d'ouvrir:", URL)

    d = pq( response.content )

    for info in d('#infos tr').items():
        th = info.find('th').text().strip()
        td = info.find('td').text().replace('\n','')
        print( th, td )

    for node in d('#wan_status,#modem_uptime').items():
        text = node.prev('th').text() + ' : '
        text += node.text().replace('\n', '').strip()
        print( text )

#_______/ LOGIN \____________________________________________________
def login():
    """ Permet l'identification sur la box """ 
    headers = { 'X-Requested-With': 'XMLHttpRequest' }
    data    = { 'callback': 'getChallenge', 'action': 'challenge'}

    response = session.post(URL + 'login', headers=headers, data=data)
    if response.status_code != 200:
        sys.exit("login(): Impossible de récuperer le challenge")

    d = pq( response.content )
    challenge = d.find('challenge').text().encode('utf-8')

    hash1 = sha256('admin'.encode('utf-8')).hexdigest().encode('utf-8')
    hash1 = hmac.new(challenge, hash1, sha256).hexdigest()

    hash2 = sha256(KEY.encode('utf-8')).hexdigest().encode('utf-8')
    hash2 = hmac.new(challenge, hash2, sha256).hexdigest()
    
    data = {
        'method'  : 'passwd',
        'page_ref': '',
        'zsid'    : challenge,
        'hash'    : hash1 + hash2
    }

    response = session.post( URL + 'login', data=data )
    if response.status_code != 200:
        sys.exit("login(): Impossible de se connecter")

#_______/ MAIN \_____________________________________________________

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--infos', action="store_true" )
parser.add_argument('-c', '--connected', action="store_true" )
parser.add_argument('-l', '--led', choices=['on', 'off'] )
parser.add_argument('-r', '--reboot', action="store_true" )

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(0)

args = parser.parse_args()

if args.infos: infos()
if args.connected: connected()
if args.led != None: led( args.led )
if args.reboot: reboot()


