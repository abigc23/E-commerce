# Generated by Django 5.1 on 2024-09-01 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personajes',
            fields=[
                ('Codigo', models.AutoField(primary_key=True, serialize=False)),
                ('Nombre', models.TextField(verbose_name=30)),
                ('Casa', models.TextField(max_length=15)),
                ('Hechizo', models.TextField(max_length=20)),
            ],
        ),
    ]
