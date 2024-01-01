import os

NUMBER_OF_DUMMIES = os.getenv('NUMBER_OF_DUMMIES')

# Returns the locations of N dummies for a user.
# Then moves all dummies one step forward.
def get_dummies_for_user(user_id):
  print(user_id)
  return [
    {"x":48.73460047395676,"y":9.112501862753065},
	  {"x":48.73535788549441,"y":9.113227410029173},
	  {"x":48.73556159973353,"y":9.11221444335842},
  ]
