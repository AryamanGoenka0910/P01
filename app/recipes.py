import requests

apiKey = "e9e1becba4c54f5296a7285059e2c485"

def searchRecipes(query):
  r = requests.get("https://api.spoonacular.com/recipes/complexSearch", 
  params={'instructionsRequired': True, 'addRecipeInformation': True, 'query': query, 'apiKey': apiKey})
  print(r.json()['results'])
  return r.json()['results']

def getRecipeInformation(recipe_id):
  r = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information", 
  params={'id': recipe_id, 'apiKey': apiKey})
  
  return r.json()


