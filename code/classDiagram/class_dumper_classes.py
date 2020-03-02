#!/usr/bin/python

from class_dumper    import ClassDumper
from class_reader    import ClassReader
from class_decriptor import Method
import os, re, sys

class ClassDumperClasses(ClassDumper):
    def __init__(self,output_file):
        ClassDumper.__init__(self)
        self.output_file = output_file
        self.nb_tabulation = 0

    def dump(self,class_file=None,classes=None):
        fout = open(self.output_file,'w')

        if class_file is not None:
            cls_reader = ClassReader()
            classes = cls_reader.read(class_file)
        for c in classes:
            self.dumpClass(c,fout)
        
    def dumpClass(self,c,f):

        sstr =  self.formatClassDeclaration(c)
        self.incTabulation()
        sstr += self.formatConstructors(c)
        sstr += self.formatMethods(c)
        sstr += self.formatMembers(c)
        sstr += "\n" 
        self.decTabulation()
        f.write(sstr)

    def formatClassDeclaration(self,c):
        sstr = "class " + c.name

        if c.inheritance is not None:
            sstr += "(" + ", ".join(c.inheritance) + ")"
            
        sstr += "\n"
        return sstr


        
    def formatConstructors(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            meths = c.getMethods(encaps)
            if c.name in meths:
                for m in meths[c.name]:
                    sstr += self.formatMethod(c,m)

        for encaps in ['public','private', 'protected']:   
            meths = c.getMethods(encaps)                 
            if '~' + c.name in meths:
                for m in meths['~' + c.name]:
                    sstr += self.formatMethod(c,m)

                        

        return sstr


    def formatMethods(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            meths = c.getMethods(encaps)
            meths_names = set(meths.keys()) - set([c.name,'~'+c.name])
            meths_names = list(meths_names)
            if len(meths_names) is not 0:
                for n in meths_names:
                    for m in meths[n]:
                        sstr += self.formatMethod(c,m)

        return sstr


    def formatMembers(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                for n,m in membs.iteritems():
                    sstr += self.formatMember(c,m)
                    sstr += "\n"
        return sstr



    def formatMethod(self,c,m):

        sstr = self.getTabulation()
        sstr += m.encapsulation + " "
        if m.static: sstr += m.static + " "
        if m.virtual: sstr += m.virtual + " "
        if m.ret: sstr += m.ret + " "
        
        sstr += m.name + "("
        sstr += ", ".join([a + " " + b for b,a in list(m.args.iteritems())])
        sstr +=  ")"
        if m.const: sstr += " const"
        sstr+= ";\n"

        self.incTabulation()
        
        self.decTabulation()
            
        return sstr

    def formatMember(self,c,m):
        sstr = self.getTabulation()
        sstr += m.encapsulation + " "
        if m.static == 'static': sstr += m.static
        sstr += m.type + " " + m.name + ';'
        return sstr

    def getTabulation(self):
        return "  " * self.nb_tabulation

    def incTabulation(self):
        self.nb_tabulation += 1

    def decTabulation(self):
        self.nb_tabulation -= 1

        
import argparse
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Classes descriptor format producer for class representation')
    parser.add_argument('--class_file','-c', help='The class file to process',required=True)
    parser.add_argument('--output_file','-o' , help='The file where to put the classes description',required=True)

    args = parser.parse_args()
    args = vars(args)
    dumper_class = ClassDumperClasses(args['output_file'])
    dumper_class.dump(class_file=args['class_file'])
