import re

text = """
James is 37 and Hadley is 10.
Bill is 32 and Joey is 35
"""

print(text)

age = re.findall(r'\d{1,3}',text)
names = re.findall(r'[A-Z][a-z]*',text)

print(age)
print(names)

agedict = {}

x = 0

for eachname in names:
	agedict[eachname] = age[x]
	x=+1

print(agedict)