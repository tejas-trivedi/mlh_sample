# Generated by Django 3.0.8 on 2020-08-06 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20200806_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiptype',
            name='amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]