# Generated by Django 3.0.8 on 2020-08-03 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20200803_2212'),
    ]

    operations = [
        migrations.AddField(
            model_name='guestuser',
            name='guest_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
