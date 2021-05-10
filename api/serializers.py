from rest_framework import serializers
from .models import Pokemon, Evolution, Stat


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ['name', 'base_stat', 'effort', ]


class EvolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evolution
        fields = ['id', 'name', 'type', ]


class PokemonSerializer(serializers.ModelSerializer):
    evolutions = EvolutionSerializer(many=True, read_only=True, source='pokemon_from')
    stats = StatSerializer(many=True, read_only=True, source='stat_set')

    class Meta:
        model = Pokemon
        fields = ['public_id', 'name', 'height', 'weight', 'evolutions', 'stats', ]
