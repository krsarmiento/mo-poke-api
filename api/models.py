import uuid
from django.db import models


EVOLUTION_TYPES = (
    ('pre-evolution', 'Pre-Evolution'),
    ('evolution', 'Evolution'),
)


class Pokemon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_id = models.PositiveSmallIntegerField(db_index=True, null=False)
    name = models.CharField(max_length=200, null=False)
    height = models.PositiveSmallIntegerField(null=False)
    weight = models.PositiveSmallIntegerField(null=False)

    def __str__(self):
        return '[{}] {}'.format(self.public_id, self.name)


class Evolution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pokemon_from = models.ForeignKey(Pokemon, on_delete=models.DO_NOTHING, related_name='pokemon_from')
    pokemon_to = models.ForeignKey(Pokemon, on_delete=models.DO_NOTHING, related_name='pokemon_to')
    name = models.CharField(max_length=200, null=False)
    type = models.CharField(choices=EVOLUTION_TYPES, max_length=30)

    def __str__(self):
        return '[{}] {} -> {}'.format(self.type, self.pokemon_from.name, self.pokemon_to.name)


class Stat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pokemon = models.ForeignKey(Pokemon, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50, null=False)
    base_stat = models.PositiveSmallIntegerField(null=False)
    effort = models.PositiveSmallIntegerField(null=False)
