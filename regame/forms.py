from django import forms

class NewMatchForm(forms.Form):
    other_player = forms.CharField(label='Who do you want to play with?', max_length=200)
