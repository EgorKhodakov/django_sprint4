# Generated by Django 3.2.16 on 2023-07-14 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='crecreated_at',
            new_name='created_at',
        ),
    ]
