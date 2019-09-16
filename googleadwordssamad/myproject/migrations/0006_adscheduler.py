# Generated by Django 2.2.3 on 2019-09-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0005_auto_20190904_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdScheduler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.CharField(blank=True, max_length=255, null=True)),
                ('day', models.CharField(blank=True, max_length=255, null=True)),
                ('starttime', models.CharField(blank=True, max_length=255, null=True)),
                ('endtime', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'adscheduler',
            },
        ),
    ]
