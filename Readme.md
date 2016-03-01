Booking
=======

[![Build Status](https://travis-ci.org/studentisgss/booking.svg?branch=master)](https://travis-ci.org/studentisgss/booking)

Sistema di prenotazione aule usato dagli studenti della Scuola Galileiana di Studi Superiori.

* Istruzioni per l'installazione: [Installazione](https://github.com/studentisgss/booking/wiki/Installazione)


Utilizzo
--------

Preparativi:

	make install
	make prepare-db

Test:

    make linter
    make test

Avvio del server:

	make server


Deploy su OpenShift
-------------------

	git add remote openshift ssh://...
	rhc env set OPENSHIFT_PYTHON_WSGI_APPLICATION="booking/wsgi_openshift.py" -a demo
	git push openshift -f
