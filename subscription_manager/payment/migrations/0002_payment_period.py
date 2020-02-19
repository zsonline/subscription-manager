# Generated by Django 3.0.3 on 2020-02-19 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0001_initial'),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='period',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='subscription.Period', verbose_name='Periode'),
        ),
    ]
