# Generated by Django 4.0.2 on 2022-03-08 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_desc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='projects',
            field=models.ManyToManyField(blank=True, to='projects.Project'),
        ),
    ]
