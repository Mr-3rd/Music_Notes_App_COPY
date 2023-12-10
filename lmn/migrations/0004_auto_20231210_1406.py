# Generated by Django 3.1.2 on 2023-12-10 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lmn', '0003_auto_20231206_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmn.artist', unique=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='show_date',
            field=models.DateTimeField(unique=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lmn.venue', unique=True),
        ),
        migrations.AlterField(
            model_name='venue',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterUniqueTogether(
            name='show',
            unique_together={('show_date', 'artist', 'venue')},
        ),
    ]
