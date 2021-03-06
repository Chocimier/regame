from django import forms
from django.contrib.auth import get_user_model
from .models import CardLocation, slotscount, UserProfile, Match, MatchParticipant, MoveKind, MatchStatus
from django_registration.forms import RegistrationForm
from collections import defaultdict

class UsernameInput(forms.widgets.Input):
    input_type = 'text'
    template_name = 'regame/forms/widgets/username.html'

class NewMatchForm(forms.ModelForm):
    player2 = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        to_field_name='username',
        widget=UsernameInput(),
        label='Who do you want to challenge?',
        error_messages = {'invalid_choice': 'I do not know him'}
    )
    class Meta:
        model = Match
        fields = ['player2', 'winconditiontype', 'winconditionnumber']
        labels = {
            'winconditiontype': 'Winner is one who',
            'winconditionnumber': 'How many?'
        }


    def __init__(self, sender, *args, **kwargs):
        super(NewMatchForm, self).__init__(*args, **kwargs)
        self._sender = sender


    def clean_player2(self):
        if self.cleaned_data['player2'] == self._sender:
            raise forms.ValidationError("You can't play a match with yourself", code='yourself')
        return self.cleaned_data['player2']


MOVE_CARD_ORDER_CHOICES = [
    ('0', '-')
] + [(str(i), str(i)) for i in range(1, slotscount(CardLocation.TABLE)+1)]

MOVE_TARGET_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.TABLE))]
HAND_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.HAND))]
TARGET_CARD_CHOICES = [(str(i), str(i+1)) for i in range(slotscount(CardLocation.TABLE))]


class OntoTableForm(forms.Form):
    put_card = forms.TypedChoiceField(choices=HAND_CARD_CHOICES, coerce=int, empty_value=None, widget=forms.RadioSelect)
    action = forms.CharField(initial='refill', widget=forms.HiddenInput)

    def widgetsfor(self, location, *, competitor):
        if not competitor and location == CardLocation.HAND:
            return [i.tag for i in self['put_card']]
        else:
            return defaultdict(lambda: None)

    def header(self):
        return "Select card in hand and put it onto table."

    def submittext(self):
        return 'Resupply'


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
        if not cardorders:
            raise forms.ValidationError("Select at least one card for pattern")

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

    def header(self):
        return ("Select what regexp bits placed on card go first, second and third." + "\n" +
               "Then choose which text on opponent's card match with.")

    def submittext(self):
        return "Attack"


class ThrowOutForm(forms.Form):
    indices = forms.MultipleChoiceField(choices=TARGET_CARD_CHOICES, widget=forms.CheckboxSelectMultiple)
    action = forms.CharField(initial='throwout', widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super().clean()
        if 'indices' not in cleaned_data or not cleaned_data['indices']:
            raise forms.ValidationError('Select at least one card to throw out')

    def widgetsfor(self, location, *, competitor):
        if not competitor and location == CardLocation.TABLE:
            return [i.tag for i in self['indices']]
        else:
            return defaultdict(lambda: None)

    def header(self):
        return ("Select cards you want to replace with random ones.")

    def submittext(self):
        return "Throw out"


class MoveKindForm(forms.ModelForm):
    action = forms.CharField(initial='changemovekind', widget=forms.HiddenInput)
    class Meta:
        model = MatchParticipant
        fields = ['movekind']
        widgets = {
            'movekind': forms.HiddenInput(),
        }

    def submittext(self):
        if self['movekind'].value() == MoveKind.ATTACK.value:
            return 'Attack this time'
        elif self['movekind'].value() == MoveKind.THROWOUT.value:
            return 'Throw out cards this time'
        return '?'


class ResignForm(forms.ModelForm):
    action = forms.CharField(initial='resign', widget=forms.HiddenInput)
    class Meta:
        model = Match
        fields = ['status']
        widgets = {
            'status': forms.HiddenInput(),
        }

    def clean(self):
        return {'status': MatchStatus.REJECTED}

    def submittext(self):
        return 'Resign'


class HideForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['hidden']
        widgets = {
            'hidden': forms.HiddenInput(),
        }

    def submittext(self):
        if self['hidden'].value():
            return "Don't show me to others"
        return 'Show me to others'


class NoEmailUserForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        super(NoEmailUserForm, self).__init__(*args, **kwargs)
        email_field = get_user_model().get_email_field_name()
        self.fields[email_field].required = False
