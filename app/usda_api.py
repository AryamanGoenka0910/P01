api_key = 'YVKKDBfyvvkgKvFKDzTOwWjUOlP2QWBlWJb6C4Xh'
import requests

def searchRecipes(query):
  r = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", 
  params={'api_key': api_key, 'query': query})
  foods = r.json()['foods']
  #Makeshift hack to cut the summary sentences off after the sentence with the serving price
  if foods:
    return foods[0]
  
  return None