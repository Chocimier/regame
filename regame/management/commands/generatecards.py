from django.core.management.base import BaseCommand, CommandError
from regame.models import Card
import json
import random
import string


class Command(BaseCommand):
    help = 'Generates fixture of cards'
    specialchars = '-_!@#$%^,:'
    patterns = []
    weights = []

    def __init__(self):
        super().__init__()
        pattern_weights = {}
        # single
        pattern_weights['[a-z]'] = len(string.ascii_lowercase)
        pattern_weights['[A-Z]'] = len(string.ascii_uppercase)
        pattern_weights['\\d'] = len(string.digits)
        pattern_weights['\\W'] = len(self.specialchars)-1
        # alternative
        pattern_weights['(\\d|\\W)'] = len(string.digits)/2
        pattern_weights['(\\W|[a-z])'] = len(string.digits)/2
        pattern_weights['[A-Z0-9_]'] = len(string.digits)/2
        pattern_weights['\\w'] = 2
        # consecutive
        pattern_weights['([a-z]\\d)'] = len(string.digits)/2
        pattern_weights['(\\W[A-Z])'] = len(string.digits)/2
        pattern_weights['([a-z][A-Z])'] = len(string.digits)/2
        # others
        pattern_weights['[AEIOUaeiou]'] = len(string.digits)/2
        # repetition
        for i in range(2,4):
            pattern_weights['{' + str(i) + '}'] = 3
        pattern_weights['{5,}'] = 4
        self.patterns = list(pattern_weights.keys())
        self.weights = list(map(pattern_weights.get, self.patterns))

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int)
        parser.add_argument('--first-pk', type=int)

    def handle(self, *args, **options):
        count = options['count'] if options['count'] is not None else 1000
        first_pk = options['first_pk'] if options['first_pk'] is not None else 1
        cards = []
        for i in range(count):
            card = self.randomcard(first_pk + i)
            cards.append(self.cardasdictionary(card))
        print(json.dumps(cards, indent=2))

    def randompatternbit(self):
        return random.choices(self.patterns, weights=self.weights)[0]

    def randomchar(self):
        chars = string.ascii_letters + string.digits + self.specialchars
        return random.choice(chars)

    def randomtext(self):
        text = ''
        for i in range(random.randint(3,12)):
            text += self.randomchar()
        return text

    def randomcard(self, pk):
        text = self.randomtext()
        patternbit = self.randompatternbit()
        card = Card(id=pk, text=text, patternbit=patternbit)
        return card

    def cardasdictionary(self, card):
        dictionary = {
            'model': 'regame.Card',
            'pk': card.id,
            'fields':{
                'text': card.text,
                'patternbit': card.patternbit,
            },
        }
        return dictionary
