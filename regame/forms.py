from django import forms
from django.contrib.auth import get_user_model
from .models import CardLocation, slotscount
from collections import defaultdict

class NewMatchForm(forms.Form):
    other_player = forms.CharField(label='Who do you want to play with?', max_length=200)

    def clean_other_player(self):
        username = self.cleaned_data['other_player']
        if not username:
            raise forms.ValidationError('Type in username')
        other_player = get_user_model().objects.filter(username=username).first()
        if not other_player:
            raise forms.ValidationError('I do not know who {} is.'.format(username))
        self.cleaned_data['competitor'] = other_player

MOVE_CARD_ORDER_CHOICES = [
    ('0', '-')
] + [(str(i), str(i)) for i in range(1, slotscount(CardLocation.TABLE)+1)]

MOVE_TARGET_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.TABLE))]
HAND_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.HAND))]


class OntoTableForm(forms.Form):
    put_card = forms.TypedChoiceField(choices=HAND_CARD_CHOICES, coerce=int, empty_value=None, widget=forms.RadioSelect)
    action = forms.CharField(initial='refill', widget=forms.HiddenInput)

    def widgetsfor(self, location, *, competitor):
        if not competitor and location == CardLocation.HAND:
            return [i.tag for i in self['put_card']]
        else:
            return defaultdict(lambda: None)


class AttackForm(forms.Form):
    on_table_first = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    on_table_second = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    on_table_third = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    target_card = forms.TypedChoiceField(choices=MOVE_TARGET_CARD_CHOICES, coerce=int, empty_value=None, widget=forms.RadioSelect)
    action = forms.CharField(initial='attack', widget=forms.HiddenInput)

    _tablefieldnames = ('on_table_first', 'on_table_second', 'on_table_third')

    def clean(self):
        cleaned_data = super().clean()
        cardorders = [cleaned_data.get(i) for i in self._tablefieldnames if cleaned_data.get(i)]
        uniquecardorders = list(set(cardorders))
        if len(cardorders) != len(uniquecardorders):
            raise forms.ValidationError("You can't use two cards at same position")

    def ontablefields(self):
        return [self[i] for i in self._tablefieldnames]

    def order(self):
        order = [None] * slotscount(CardLocation.TABLE)
        for cardindex, name in enumerate(self._tablefieldnames):
            cardorder = self.cleaned_data[name]
            if cardorder:
                order[cardorder-1] = cardindex
        return [i for i in order if i is not None]

    def widgetsfor(self, location, *, competitor):
        if not competitor and location == CardLocation.TABLE:
            return self.ontablefields()
        elif competitor and location == CardLocation.TABLE:
            return [i.tag for i in self['target_card']]
        else:
            return defaultdict(lambda: None)
