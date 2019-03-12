from django.core.management.base import BaseCommand, CommandError
from regame.models import Card
import json
import random
import string


class Command(BaseCommand):
    help = 'Generates fixture of cards'
    specialchars = '-_!@#$%^'

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
        pattern_weights = {}
        pattern_weights['[a-z]'] = len(string.ascii_lowercase)
        pattern_weights['[A-Z]'] = len(string.ascii_uppercase)
        pattern_weights['[0-9]'] = len(string.digits)
        pattern_weights['[' + self.specialchars + ']'] = len(self.specialchars)
        pattern_weights['?'] = 3
        for i in range(2,4):
            pattern_weights['{' + str(i) + '}'] = 2
        pattern_weights['{5,}'] = 3
        patterns = list(pattern_weights.keys())
        weights = list(map(pattern_weights.get, patterns))
        return random.choices(patterns, weights=weights)[0]

    def randomchar(self):
        chars = string.ascii_letters + string.digits + self.specialchars
        return random.choice(chars)

    def randomtext(self):
        text = ''
        for i in range(4):
            text += self.randomchar()
        for i in range(6):
            if random.random() < 0.5:
                text += self.randomchar()
            else:
                break
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
