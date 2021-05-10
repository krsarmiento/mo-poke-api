from django.core.management.base import BaseCommand, CommandError
from api.models import Pokemon, Evolution, Stat
import requests
from django.core.exceptions import ObjectDoesNotExist


POKE_API_URL = 'https://pokeapi.co/api/v2'
EVOLUTION_CHAIN_PATH = 'evolution-chain'
POKEMON_PATH = 'pokemon'
SUCCESS_STATUS_CODE = 200


class Command(BaseCommand):
    help = 'Fetch and save info from the PokeAPI'

    def add_arguments(self, parser):
        parser.add_argument('evolution_chain_id', nargs='+', type=int)

    def handle(self, *args, **options):
        url = '{}/{}/{}/'.format(POKE_API_URL, EVOLUTION_CHAIN_PATH, options['evolution_chain_id'][0])
        self.stdout.write('Retrieving information from {}'.format(url))
        r = requests.get(url)
        if r.status_code != SUCCESS_STATUS_CODE:
            self.stderr.write('There was an error while fetching the evolution chain')
            self.stderr.write('{}: {}'.format(r.status_code, r.text))
            return

        self.stdout.write(self.style.SUCCESS('Information retrieved successfully!'))

        evolution_chain = r.json()

        # evolution_chain = {"baby_trigger_item":None,"chain":{"evolution_details":[],"evolves_to":[{"evolution_details":[{"gender":None,"held_item":None,"item":None,"known_move":None,"known_move_type":None,"location":None,"min_affection":None,"min_beauty":None,"min_happiness":None,"min_level":7,"needs_overworld_rain":False,"party_species":None,"party_type":None,"relative_physical_stats":None,"time_of_day":"","trade_species":None,"trigger":{"name":"level-up","url":"https://pokeapi.co/api/v2/evolution-trigger/1/"},"turn_upside_down":False}],"evolves_to":[{"evolution_details":[{"gender":None,"held_item":None,"item":None,"known_move":None,"known_move_type":None,"location":None,"min_affection":None,"min_beauty":None,"min_happiness":None,"min_level":10,"needs_overworld_rain":False,"party_species":None,"party_type":None,"relative_physical_stats":None,"time_of_day":"","trade_species":None,"trigger":{"name":"level-up","url":"https://pokeapi.co/api/v2/evolution-trigger/1/"},"turn_upside_down":False}],"evolves_to":[],"is_baby":False,"species":{"name":"beautifly","url":"https://pokeapi.co/api/v2/pokemon-species/267/"}}],"is_baby":False,"species":{"name":"silcoon","url":"https://pokeapi.co/api/v2/pokemon-species/266/"}},{"evolution_details":[{"gender":None,"held_item":None,"item":None,"known_move":None,"known_move_type":None,"location":None,"min_affection":None,"min_beauty":None,"min_happiness":None,"min_level":7,"needs_overworld_rain":False,"party_species":None,"party_type":None,"relative_physical_stats":None,"time_of_day":"","trade_species":None,"trigger":{"name":"level-up","url":"https://pokeapi.co/api/v2/evolution-trigger/1/"},"turn_upside_down":False}],"evolves_to":[{"evolution_details":[{"gender":None,"held_item":None,"item":None,"known_move":None,"known_move_type":None,"location":None,"min_affection":None,"min_beauty":None,"min_happiness":None,"min_level":10,"needs_overworld_rain":False,"party_species":None,"party_type":None,"relative_physical_stats":None,"time_of_day":"","trade_species":None,"trigger":{"name":"level-up","url":"https://pokeapi.co/api/v2/evolution-trigger/1/"},"turn_upside_down":False}],"evolves_to":[],"is_baby":False,"species":{"name":"dustox","url":"https://pokeapi.co/api/v2/pokemon-species/269/"}}],"is_baby":False,"species":{"name":"cascoon","url":"https://pokeapi.co/api/v2/pokemon-species/268/"}}],"is_baby":False,"species":{"name":"wurmple","url":"https://pokeapi.co/api/v2/pokemon-species/265/"}},"id":135}

        response = self.get_pokemons_from_chain(evolution_chain['chain'])
        if not response:
            self.stderr.write('There was an error while parsing the pokemon info')
            return

        self.stdout.write(self.style.SUCCESS('-----------'))
        self.stdout.write(self.style.SUCCESS(response))

    def get_pokemons_from_chain(self, chain, pre=None, post_id=None):
        evolutions = []

        pokemon_id = self.get_pokemon_id(chain)
        if not pokemon_id:
            return False

        if pre is None:
            pre_evolutions = [pokemon_id]
        else:
            pre_evolutions = pre + [pokemon_id]

        post_id = []
        for ch in chain['evolves_to']:
            result = self.get_pokemons_from_chain(ch, pre_evolutions)
            if not result:
                return False
            evolutions.append(result)
            post_id = post_id + [result['id']] + result['post_id']

        evolution_format = {
            'pre': pre,
            'id': pokemon_id,
            'post': evolutions,
            'post_id': post_id,
        }

        self.save_evolutions(evolution_format)

        return evolution_format

    def get_pokemon_data(self, pokemon_id):
        try:
            pokemon = Pokemon.objects.get(public_id=pokemon_id)
            return pokemon
        except ObjectDoesNotExist:
            pass

        url = '{}/{}/{}/'.format(POKE_API_URL, POKEMON_PATH, pokemon_id)
        self.stdout.write('Retrieving information from {}'.format(url))
        r = requests.get(url)
        if r.status_code != SUCCESS_STATUS_CODE:
            self.stderr.write('There was an error while fetching the pokemon')
            self.stderr.write('{}: {}'.format(r.status_code, r.text))
            return False

        pokemon_data = r.json()
        pokemon, created = Pokemon.objects.get_or_create(
            public_id=int(pokemon_id),
            name=pokemon_data['species']['name'],
            height=pokemon_data['height'],
            weight=pokemon_data['weight'],
        )

        if created:
            stats = []
            for stat in pokemon_data['stats']:
                stats.append(Stat(
                    pokemon=pokemon,
                    name=stat['stat']['name'],
                    base_stat=stat['base_stat'],
                    effort=stat['effort'],
                ))

            Stat.objects.bulk_create(stats)

        return pokemon

    def get_pokemon_id(self, chain):
        split_url = chain['species']['url'].split('/')
        if not split_url:
            return False

        return int(split_url[-2])

    def save_evolutions(self, evolution_format):
        main_pokemon = self.get_pokemon_data(evolution_format['id'])

        print(main_pokemon.name)

        pre_evolutions = []
        if evolution_format['pre']:
            for pokemon_id in evolution_format['pre']:
                pokemon = self.get_pokemon_data(pokemon_id)
                if pokemon:
                    pre_evolutions.append(Evolution(
                        pokemon_from=main_pokemon,
                        pokemon_to=pokemon,
                        name=pokemon.name,
                        type='pre-evolution',
                    ))

        Evolution.objects.bulk_create(pre_evolutions)

        evolutions = []
        if evolution_format['post_id']:
            for pokemon_id in evolution_format['post_id']:
                pokemon = self.get_pokemon_data(pokemon_id)
                if pokemon:
                    evolutions.append(Evolution(
                        pokemon_from=main_pokemon,
                        pokemon_to=pokemon,
                        name=pokemon.name,
                        type='evolution',
                    ))

        Evolution.objects.bulk_create(evolutions)



