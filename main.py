from clause import *
from function import *
from hassediagram import *

c1 = Clause('10111')
print("c1:",c1)
c2 = Clause('10011')
print("c2:",c2)

f = Function(5, {c1})
print("f:",f)
print("i?", f.independent_clauses())
print("c?", f.is_consistent())
f.add_clause(c2)
print("f:",f)
print("c?", f.is_consistent())

print("c1.subsets:", c1.get_subsets())   

print("c2.supersets:", c2.get_supersets())

hd = HasseDiagram(3)
fi = hd.get_infimum()
print("fi:",fi)