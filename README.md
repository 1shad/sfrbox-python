### sfrbox.py -- box sfr interface v3.4

Ce script permet d'afficher certains paramètres de la box, de la redemarrer
ou d'allumer/éteindre les leds

### Synopsis:
    sfrbox.py -led on
    sfrbox.py -i -c -led on
    sfrbox.py -r

voir sfrbox.py -h pour l'ensemble des commandes

### Configuration:
    - Remplacer la valeur dans KEY par la clé wifi de la box.
    - Vérifier que l'ip dans URL soit la bonne

### Modules requis:
    pyquery
    requests
