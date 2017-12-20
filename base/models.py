from django.db import models

# Create your models here.

CLASSES_WITH_TRANSLATION = [
    ("SN", "Scienze Naturali", "Natural Sciences"),
    ("SM", "Scienze Morali", "Moral Sciences"),
    ("SS", "Scienze Sociali", "Social Sciences"),
    ("A", "Altro", "Other")
]

CLASS_CHOICES = [(choice[0], choice[1])
                 for choice in CLASSES_WITH_TRANSLATION]
