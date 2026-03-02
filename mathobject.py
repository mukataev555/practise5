import re

txt = "The rain in Spain"
x = re.search("ai", txt)
print(x) #this will print an object

import re

txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.span())

import re

txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.string)

import re

txt = "The rain in Spain"
x = re.search(r"\bS\w+", txt)
print(x.group())

