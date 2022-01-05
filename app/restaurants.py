import requests
import random
import json

def restaurant():
    random_cats = ['pizza', 'indpak', 'japanese', 'chinese', 'vegan', 'restuarants']
    x = random.randrange(0,5)

    my_headers = {'Authorization' : 'Bearer gJIaQ2GgBZJRE1iV61MUNNMIw8v_Q4x1aAKYFnq6TZrNQHsCwi1b8bpuDZ_MmWUk9paI5MDAYFtfkcrE_HCZZMQhf4L1yc0heQ4coxKhhELU7Cqdy2XUsAaik0C7YXYx'}
    r = requests.get(f'https://api.yelp.com/v3/businesses/search?location=NYC&categories={random_cats[x]}', headers=my_headers)
    print(json.dumps(r.json()))

def get_restaurantJSON_by_id(restaurant_id):
  my_headers = {'Authorization' : 'Bearer gJIaQ2GgBZJRE1iV61MUNNMIw8v_Q4x1aAKYFnq6TZrNQHsCwi1b8bpuDZ_MmWUk9paI5MDAYFtfkcrE_HCZZMQhf4L1yc0heQ4coxKhhELU7Cqdy2XUsAaik0C7YXYx'}
  r = requests.get(f'https://api.yelp.com/v3/businesses/{restaurant_id}', headers=my_headers)
  return r.json()

print(get_restaurantJSON_by_id("WavvLdfdP6g8aZTtbBQHTw"))