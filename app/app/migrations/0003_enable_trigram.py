from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_scamrecord_and_more'),
    ]

    operations = [
        TrigramExtension(),
    ]