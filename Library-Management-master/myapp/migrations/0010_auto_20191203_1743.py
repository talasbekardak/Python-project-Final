# Generated by Django 2.2.5 on 2019-12-03 22:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0009_auto_20191203_1742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=datetime.datetime(2019, 12, 3, 22, 43, 27, 873844, tzinfo=utc)),
        ),
    ]
