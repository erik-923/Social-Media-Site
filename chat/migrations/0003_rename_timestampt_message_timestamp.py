# Generated by Django 4.2.1 on 2023-06-01 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_message_chat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='timestampt',
            new_name='timestamp',
        ),
    ]
