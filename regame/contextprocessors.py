from regame.models import WinConditionType

def global_values(request):
	return {'WinConditionType': {i.name: i for i in WinConditionType} }
