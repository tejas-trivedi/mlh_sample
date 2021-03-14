# Generated by Django 3.0.8 on 2020-08-08 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_delete_membershiptype'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipType',
            fields=[
                ('MEMBERSHIP', models.CharField(default='None', max_length=100, primary_key=True, serialize=False, unique=True)),
                ('Price', models.IntegerField()),
                ('Duration', models.IntegerField()),
            ],
        ),
    ]
