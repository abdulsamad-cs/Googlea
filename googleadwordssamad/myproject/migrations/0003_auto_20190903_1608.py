# Generated by Django 2.2.3 on 2019-09-03 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0002_rule_engine_conditions_date_range'),
    ]

    operations = [
        migrations.RenameField(
            model_name='adgroupperformancereportmodel',
            old_name='AdGroupId',
            new_name='adgroupid',
        ),
    ]
