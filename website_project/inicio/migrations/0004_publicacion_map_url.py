# Generated by Django 5.1.1 on 2024-09-15 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0003_grupo_publicaciongrupo_comentariogrupo'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicacion',
            name='map_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
