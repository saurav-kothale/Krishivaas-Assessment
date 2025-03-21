import requests
import numpy as np
import pandas as pd

token = "kbyhpz56f1"
r = requests.get('https://coderbyte.com/api/challenges/json/age-counting')
my_list = (r.json()['data']).split(",")
count = 0
for i in range(len(my_list)):
  if i % 2 != 0:
    striped_ele = my_list[i].strip()
    age = int(striped_ele.split("=")[1])
    if age >= 50:
      count += 1

output = str(count)
final_output = "".join(a+b for a, b in zip(output,token)) + token[len(output):]
print(final_output)