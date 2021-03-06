# Generated by Django 2.1 on 2018-08-08 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='sn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='user_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100, null=True)),
                ('password', models.CharField(max_length=100, null=True)),
                ('pay_password', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('sex', models.CharField(max_length=10, null=True)),
                ('birth', models.CharField(max_length=100, null=True)),
                ('phone', models.CharField(max_length=20, null=True)),
                ('email', models.CharField(max_length=100, null=True)),
                ('id_card', models.CharField(max_length=50, null=True)),
                ('qq', models.CharField(max_length=20, null=True)),
                ('weixin', models.CharField(max_length=20, null=True)),
                ('pre_name', models.CharField(max_length=100, null=True)),
                ('pre_id_card', models.CharField(max_length=50, null=True)),
            ],
        ),
    ]
