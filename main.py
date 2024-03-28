from clause import *
from function import *
from hassediagram import *

# Testing functions in arXiv paper Fig 5 ##############
n=4
fS1 = Function(n, {Clause('1110'), Clause('1011'), Clause('0111')})
fS2 = Function(n, {Clause('1110'), Clause('0011')})
fS3 = Function(n, {Clause('1101'), Clause('1010'), Clause('0110'), Clause('0011')})
fS4 = Function(n, {Clause('1010'), Clause('0110'), Clause('0011')})

hd = HasseDiagram(n)
print('Parents[',fS1,']:',hd.get_f_parents(fS1))
print('Childrens[',fS3,']:',hd.get_f_children(fS3))
