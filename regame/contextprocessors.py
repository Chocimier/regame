from regame.models import DEFAULT_WIN_CONDITION_NUMBER, WinConditionType

def global_values(request):
	return {
		'WinConditionType': {i.name: i for i in WinConditionType},
		'DEFAULT_WIN_CONDITION_NUMBER': DEFAULT_WIN_CONDITION_NUMBER,
	}
