# Generated by Django 3.2.2 on 2021-05-09 23:11

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('public_id', models.PositiveSmallIntegerField(db_index=True)),
                ('name', models.CharField(max_length=200)),
                ('height', models.PositiveSmallIntegerField()),
                ('weight', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('base_stat', models.PositiveSmallIntegerField()),
                ('effort', models.PositiveSmallIntegerField()),
                ('pokemon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='api.pokemon')),
            ],
        ),
        migrations.CreateModel(
            name='Evolution',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('type', models.CharField(choices=[('pre-evolution', 'Pre-Evolution'), ('evolution', 'Evolution')], max_length=30)),
                ('pokemon_from', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pokemon_from', to='api.pokemon')),
                ('pokemon_to', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pokemon_to', to='api.pokemon')),
            ],
        ),
    ]
