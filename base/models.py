from django.db import models

# Create your models here.

# If you modify the classes do a migration to recreate the correct permissions
CLASSES_WITH_TRANSLATION = [
    ("SN", "Scienze Naturali", "Natural Sciences"),
    ("SM", "Scienze Morali", "Moral Sciences"),
    ("SS", "Scienze Sociali", "Social Sciences"),
    ("A", "Altro", "Other")
]

CLASS_CHOICES = [(choice[0], choice[1])
                 for choice in CLASSES_WITH_TRANSLATION]
