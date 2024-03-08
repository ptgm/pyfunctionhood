from clause import *
from function import *
from powerset import *
from hassediagram import *

fS1 = Function(4, {Clause('1110'), Clause('1011'), Clause('0111')})
fS2 = Function(4, {Clause('1110'), Clause('0011')})
fS3 = Function(4, {Clause('1101'), Clause('1010'), Clause('0110'), Clause('0011')})
fS4 = Function(4, {Clause('1010'), Clause('0110'), Clause('0011')})
f=fS2
print("f:",f , '| consistent:', f.is_consistent())

p = PowerSet(4)
# print("powerset:",p)
#print("f.independent_clauses", p.get_independent(f.clauses))
#print("f.max_independent_clauses", p.get_maximal(p.get_independent(f.clauses)))

hd = HasseDiagram(4)
print(hd.get_f_parents(f))
#print(hd.get_f_children(f))

# print("c?", f.is_consistent())
# f.add_clause(c2)
# print("f:",f)
# print("c?", f.is_consistent())

# print("c1.subsets:", c1.get_subsets())   

# print("c2.supersets:", c2.get_supersets())

# hd = HasseDiagram(3)
# fi = hd.get_infimum()
# print("fi:",fi)