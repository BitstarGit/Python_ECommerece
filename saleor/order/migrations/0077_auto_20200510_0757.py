# Generated by Django 2.2.6 on 2020-05-10 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0076_auto_20191018_0554'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fulfillment',
            name='shipping_date',
        ),
        migrations.AddField(
            model_name='order',
            name='new_order_status',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]