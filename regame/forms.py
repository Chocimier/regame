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

    def ontablefields(self):
        return (self['on_table_first'], self['on_table_second'], self['on_table_third'])
