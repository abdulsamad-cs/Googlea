# Generated by Django 2.2.3 on 2019-09-04 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myproject', '0004_auto_20190903_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='adgroupperformancereportmodel',
            name='LabelIds',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='campaignperformancereportmodel',
            name='LabelIds',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='keywordperformancereportmodel',
            name='LabelIds',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
