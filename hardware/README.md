# Hardware

- Vasca da 10 L con *Chlorella vulgaris*.
- Sonda di torbidità SEN0189, letta dall'ADS1115 sul bus I2C del Pi 5.
- Pompa sulla linea di raccolta, scheda relè su GPIO 17.
- Filtro da 5 µm: la pompa parte sopra 280 NTU e si ferma sotto 90 NTU.
- Schermo sul Pi, pannello in `display/`.

Lo schermo mostra la fase del ciclo (latenza, crescita, picco, raccolta, recupero), la torbidità, il filtraggio e l'ossigeno prodotto.

Cablaggio e pin: `electronics/README.md`.
