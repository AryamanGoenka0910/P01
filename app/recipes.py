import requests

apiKey = "75ac2f64fd464206b3df85eedc3ca67c"

def searchRecipes(query):
  r = requests.get("https://api.spoonacular.com/recipes/complexSearch", 
  params={'instructionsRequired': True, 'addRecipeInformation': True, 'query': query, 'apiKey': apiKey})
  print(r.json()['results'])
  return r.json()['results']

def getRecipeInformation(recipe_id):
  r = requests.get(f"https://api.spoonacular.com/recipes/{recipe_id}/information", 
  params={'id': recipe_id, 'apiKey': apiKey})
  
  return r.json()


