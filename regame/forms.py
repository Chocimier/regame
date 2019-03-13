from django import forms
from .models import CardLocation, slotscount

class NewMatchForm(forms.Form):
    other_player = forms.CharField(label='Who do you want to play with?', max_length=200)


MOVE_CARD_ORDER_CHOICES = [
    ('0', '-')
] + [(str(i), str(i)) for i in range(1, slotscount(CardLocation.TABLE)+1)]

MOVE_TARGET_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.TABLE))]


class MoveForm(forms.Form):
    on_table_first = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    on_table_second = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    on_table_third = forms.TypedChoiceField(choices=MOVE_CARD_ORDER_CHOICES, coerce=int, empty_value=0)
    target_card = forms.TypedChoiceField(choices=MOVE_TARGET_CARD_CHOICES, coerce=int, empty_value=None, widget=forms.RadioSelect)

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
