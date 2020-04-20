import re

txt = "That will be 59 dollars"

#Find all digit characters:

x = re.findall("\d", txt)
print(x)

txt1 = "hello world"

#Search for a sequence that starts with "he", followed by two (any) characters, and an "o":

x1 = re.findall("he......r", txt1)
print(x1)

x2 = re.findall("^h.*d$", txt1)
print(x2)

x3 = re.findall(".*world$", txt1)
print(x3)

#Check if the string contains "ai" followed by 0 or more "x" characters:
txt2 = "The rain in Spain falls + mainly in the plain!"
x4 = re.findall("aix*", txt2)
print(x4)

x5 = re.findall("aix+", txt2)
print(x5)

#Check if the string contains "a" followed by exactly two "l" characters:

x6 = re.findall("al{2}", txt2)
print(x6)

#Check if the string contains either "falls" or "stays":
x7 = re.findall("falls|in", txt2)
print(x7)

#Check if the string has any + characters:
x8 = re.findall("[+]", txt2)
print(x8)

x9 = re.split("\s", txt2)
print(x9)

x10 = re.search(r"\bS\w+", txt2)
print(x10)
print(x10.span())