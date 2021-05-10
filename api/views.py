from rest_framework import viewsets
from api.serializers import PokemonSerializer
from api.models import Pokemon
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class PokemonViewSet(viewsets.ModelViewSet):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    def retrieve(self, request, *args, **kwargs):
        # We'll treat PK as the name to reuse the retrieve method from DRF
        instance = obj = get_object_or_404(self.queryset, name=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)