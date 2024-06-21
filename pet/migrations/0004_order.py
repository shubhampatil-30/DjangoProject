# Generated by Django 3.0.5 on 2024-06-12 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0003_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordernumber', models.CharField(max_length=100)),
                ('orderdate', models.DateField()),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50)),
                ('phoneno', models.BigIntegerField()),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('pincode', models.BigIntegerField()),
                ('orderstatus', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'order',
            },
        ),
    ]
