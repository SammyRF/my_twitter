# Generated by Django 3.1.3 on 2021-08-15 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tweet',
            old_name='create_at',
            new_name='created_at',
        ),
    ]