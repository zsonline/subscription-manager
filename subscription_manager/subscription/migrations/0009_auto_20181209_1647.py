# Generated by Django 2.1.4 on 2018-12-09 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0008_auto_20181209_1613'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='duration',
        ),
        migrations.AddField(
            model_name='plan',
            name='duration_in_months',
            field=models.PositiveIntegerField(default=12, help_text='Die Laufzeit muss in Monaten angegeben sein.', verbose_name='Laufzeit in Monaten'),
        ),
    ]