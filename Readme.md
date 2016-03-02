Booking
=======

[![Build Status](https://travis-ci.org/studentisgss/booking.svg?branch=master)](https://travis-ci.org/studentisgss/booking)

Sistema di prenotazione aule usato dagli studenti della Scuola Galileiana di Studi Superiori.

Demo: <https://demo-sgss.rhcloud.com>


Documentazione
-------------

Istruzioni per l'installazione: [Installazione](https://github.com/studentisgss/booking/wiki/Installazione)

Documentazione: [wiki del progetto](https://github.com/studentisgss/booking/wiki)


Utilizzo
--------

Preparativi:

	make install
	make delete-db  # solo se necessario!
	make delete-migrations  # solo se necessario!
	make migrate-db
	make populate-db

Test:

    make linter
    make test

Avvio del server:

	make server
