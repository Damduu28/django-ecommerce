# Generated by Django 4.1.7 on 2023-06-03 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_alter_customer_email_alter_customer_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='discount_percent',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
