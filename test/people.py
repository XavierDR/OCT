# -*- coding: utf-8 -*-
"""
Created on Tue Aug 04 10:05:58 2015

@author: oct
"""


class People(object):
    
    age = 0
    name = ""
    height = 0
    
    def __init__(self, age, name, height):
        self.age = age
        self.name = name
        self.height = height
        
person1 = People(12, "George", 170)
print(person1.age)
print(person1.height)

class Father(People):
    
    height = 0
    numOfChildren = 0
    def __init__(self, age, name, height, numOfChildren):
        People.__init__(self, age, name, height)
        self.numOfChildren = numOfChildren
        
person2 = Father(30, "max", 190, 2)
print person2.name, person2.numOfChildren
        