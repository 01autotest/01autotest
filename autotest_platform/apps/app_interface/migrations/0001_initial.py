# Generated by Django 2.1 on 2018-08-08 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='interfaces_oeasy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('url', models.TextField(null=True)),
                ('head', models.TextField(null=True)),
                ('body_format', models.CharField(max_length=20, null=True)),
                ('body', models.TextField(null=True)),
                ('mode', models.CharField(max_length=30, null=True)),
                ('charger', models.CharField(max_length=20, null=True)),
                ('order', models.IntegerField(null=True)),
                ('module', models.CharField(max_length=30, null=True)),
                ('update_cookie', models.CharField(max_length=10, null=True)),
                ('assert_use_new', models.CharField(max_length=10, null=True)),
                ('assert_keywords_old', models.TextField(null=True)),
                ('assert_url', models.TextField(null=True)),
                ('assert_head', models.TextField(null=True)),
                ('assert_mode', models.CharField(max_length=10, null=True)),
                ('assert_body_format', models.CharField(max_length=20, null=True)),
                ('assert_body', models.TextField(null=True)),
                ('assert_keywords', models.TextField(null=True)),
                ('assert_keywords_is_contain', models.CharField(max_length=10, null=True)),
                ('assert_use_new_AI', models.CharField(max_length=10, null=True)),
                ('assert_url_AI', models.TextField(null=True)),
                ('assert_head_AI', models.TextField(null=True)),
                ('assert_mode_AI', models.CharField(max_length=10, null=True)),
                ('assert_body_format_AI', models.CharField(max_length=20, null=True)),
                ('assert_body_AI', models.TextField(null=True)),
                ('assert_keywords_is_contain_AI', models.CharField(max_length=10, null=True)),
                ('assert_keywords_new_AI', models.TextField(null=True)),
                ('assert_keywords_old_AI', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='public_para',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yypt', models.TextField(null=True)),
                ('wypt', models.TextField(null=True)),
                ('yhsq', models.TextField(null=True)),
                ('wyj', models.TextField(null=True)),
                ('dspt', models.TextField(null=True)),
                ('sjpt', models.TextField(null=True)),
                ('ggpt', models.TextField(null=True)),
                ('xqmc', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='public_para1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('keywords', models.CharField(max_length=100, null=True)),
                ('value', models.TextField(null=True)),
                ('left', models.TextField(null=True)),
                ('right', models.TextField(null=True)),
                ('index', models.CharField(max_length=20, null=True)),
                ('module', models.CharField(max_length=20, null=True)),
                ('module_id', models.CharField(max_length=20, null=True)),
                ('type', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='suit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suit_name', models.CharField(max_length=100, null=True)),
                ('interface_name', models.TextField(null=True)),
                ('interface_name_display', models.TextField(null=True)),
                ('charger', models.CharField(max_length=20, null=True)),
                ('orders', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='suit_interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suit_id', models.IntegerField(null=True)),
                ('suit_name', models.CharField(max_length=100, null=True)),
                ('interface_name', models.CharField(max_length=100, null=True)),
                ('url', models.TextField(null=True)),
                ('head', models.TextField(null=True)),
                ('body_format', models.CharField(max_length=20, null=True)),
                ('body', models.TextField(null=True)),
                ('mode', models.CharField(max_length=10, null=True)),
                ('update_cookie', models.CharField(max_length=10, null=True)),
                ('assert_use_new', models.CharField(max_length=10, null=True)),
                ('assert_keywords_old', models.TextField(null=True)),
                ('assert_url', models.TextField(null=True)),
                ('assert_head', models.TextField(null=True)),
                ('assert_mode', models.CharField(max_length=10, null=True)),
                ('assert_body_format', models.CharField(max_length=20, null=True)),
                ('assert_body', models.TextField(null=True)),
                ('assert_keywords', models.TextField(null=True)),
                ('assert_keywords_is_contain', models.CharField(max_length=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='suit_result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suit_id', models.IntegerField(null=True)),
                ('suit_interface_id', models.IntegerField(null=True)),
                ('response', models.TextField(null=True)),
                ('result', models.CharField(max_length=20, null=True)),
                ('date_time', models.CharField(max_length=20, null=True)),
            ],
        ),
    ]