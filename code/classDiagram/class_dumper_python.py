#!/usr/bin/python

from class_dumper    import ClassDumper
from class_reader    import ClassReader
from class_decriptor import Method
import os, re 

class ClassDumperPython(ClassDumper):
    def __init__(self,output_dir):
        ClassDumper.__init__(self)
        self.output_dir = output_dir
        self.nb_tabulation = 0

    def makeBaseFilename(self,class_name):
        name = re.sub(r'([0-9]|[A-Z0-9])','_\g<1>',class_name)
        name = name.lower()
        
        if name[0] == '_':
            name = name[1:]
        return name
        
    def dump(self,class_file):
        cls_reader = ClassReader()
        classes = cls_reader.read(class_file)
        for c in classes:
            basename = self.makeBaseFilename(c.name)
            class_filename = os.path.join(self.output_dir,basename+".py")
            with open(class_filename,'w') as f:
                f.write("""#!/usr/bin/env python
# -*- coding: utf-8 -*-
""")
                imports = []
                if c.inheritance is not None:
                    imports = ["from " + self.makeBaseFilename(i) + " import *" for i in c.inheritance]
                imports = "\n".join(imports)
                f.write("""#################\n""")
                f.write(imports)
                f.write("""\n#################\n""")
        
                        
                f.write("""
\"\"\"
Module containing class {0}
\"\"\"
""".format(c.name))
                self.dumpClass(c,f)

                f.write("""


if __name__ == '__main__':
        test = {0}()

""".format(c.name))
                
        return ""

        
    def dumpClass(self,c,f):

        sstr =  self.formatClassDeclaration(c)
        self.incTabulation()
        sstr += """
{0}\"\"\" 
class {1}: Documentation TODO
{0}\"\"\"
""".format(self.getTabulation(),c.name)

        sstr += self.formatStaticMembers(c)
        sstr += self.formatConstructors(c)
        sstr += self.formatMethods(c)
        sstr += "\n" 
        self.decTabulation()

        f.write("## -------------------------------------------------------------------------- ##\n")

        f.write(sstr)
        f.write("## -------------------------------------------------------------------------- ##\n")

    def formatClassDeclaration(self,c):
        sstr = "class " + c.name

        if c.inheritance is not None:
            sstr += "(" + ", ".join(c.inheritance) + ")"
            
        sstr += ":\n"
        return sstr


        
    def formatConstructors(self,c):
        sstr = ""

        meths = {}
        for encaps in ['public','private', 'protected']:
            meths.update(c.getMethods(encaps))
            
        if c.name in meths:
            for m in meths[c.name]:
                m.name = "__init__"
                sstr += self.formatMethod(c,m,pass_flag=False)
                self.incTabulation()
                sstr += self.formatMembers(c)
                sstr += self.getTabulation() + "pass\n\n"
                self.decTabulation()
        else:
            m = Method('__init__',"","",'public','','','','default constructor')
            sstr += self.formatMethod(c,m,pass_flag=False)
            self.incTabulation()
            sstr += self.formatMembers(c)
            sstr += self.getTabulation() + "pass\n\n"
            self.decTabulation()

        if '~' + c.name in meths:
            for m in meths['~' + c.name]:
                m.name = "__del__"
                sstr += self.formatMethod(c,m)

                        

        if not sstr == "": 
            sstr = """
{0}## ------------------------------------------------------------------ ##
{0}## Constructors/Destructors                                           ##
{0}## ------------------------------------------------------------------ ##

""".format(self.getTabulation()) + sstr 

        return sstr


    def formatMethods(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            meths = c.getMethods(encaps)
            meths_names = set(meths.keys()) - set([c.name,'~'+c.name])
            meths_names = list(meths_names)
            if len(meths_names) is not 0:
                sstr += self.getTabulation() + "# " + encaps + ":\n\n"
                for n in meths_names:
                    for m in meths[n]:
                        sstr += self.formatMethod(c,m)
                        sstr += "\n"

        if not sstr == "":
            sstr = """
{0}## ------------------------------------------------------------------ ##
{0}## Methods                                                            ##
{0}## ------------------------------------------------------------------ ##

""".format(self.getTabulation()) + sstr

        return sstr


    def formatMembers(self,c):
        sstr = ""

#        print c.name,c.members
        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                for n,m in membs.iteritems():
                    if m.static == 'static': continue
                    sstr += self.formatMember(c,m)
                    sstr += "\n"

        if not sstr == "":
            sstr = """
{0}## Members ---------------------- ##

""".format(self.getTabulation()) + sstr

        return sstr

    def formatStaticMembers(self,c):
        sstr = ""

#        print c.name,c.members
        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                for n,m in membs.iteritems():
                    if not m.static == 'static': continue
                    sstr += self.formatStaticMember(c,m)
                    sstr += "\n"

        if not sstr == "":
            sstr = """
{0}## Members ---------------------- ##

""".format(self.getTabulation()) + sstr

        return sstr


    def formatMethod(self,c,m,pass_flag=True):

        sstr = ""

        name = m.name
        first_param = "self"
        if m.encapsulation == 'private': name = "__" + name
        if m.encapsulation == 'protected': name = "_" + name
        if m.static: 
                sstr += self.getTabulation() + "@classmethod\n"
                first_param = "cls"
                
        sstr += self.getTabulation() + "def " + name + "("
        sstr += ", ".join([first_param]+[b for b,a in list(m.args.iteritems())])
        sstr +=  "):\n"

        self.incTabulation()
        
        if m.virtual == 'pure virtual': 
                sstr += self.getTabulation() + "raise Exception('This is a pure virtual method')\n"


        sstr += "{0}\"\"\" Documentation TODO \"\"\"\n".format(self.getTabulation(),name)

        if pass_flag: sstr += self.getTabulation() + "pass\n"

        self.decTabulation()
            
        return sstr

    def formatMember(self,c,m):
        name = m.name
        if m.encapsulation == 'private': name = "__" + name
        if m.encapsulation == 'protected': name = "_" + name

        sstr = self.getTabulation() + "#" + m.type + " " + name + "\n"
        sstr += self.getTabulation() + "self." + name + " = None\n"
        return sstr

    def formatStaticMember(self,c,m):
        name = m.name
        if m.encapsulation == 'private': name = "__" + name
        if m.encapsulation == 'protected': name = "_" + name

        sstr = self.getTabulation() + "#" + m.type + " " + name + "\n"
        sstr += self.getTabulation() + name + " = None\n"
        return sstr

    def getTabulation(self):
        return "    " * self.nb_tabulation

    def incTabulation(self):
        self.nb_tabulation += 1

    def decTabulation(self):
        self.nb_tabulation -= 1

        
import argparse
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='CPP project producer for class representation')
    parser.add_argument('--class_file','-c', help='The class file to process',required=True)
    parser.add_argument('--output_dir','-o' , help='The directory where to put produced files',required=True)

    args = parser.parse_args()
    args = vars(args)
    os.makedirs(args['output_dir'])
    dumper_class = ClassDumperPython(args['output_dir'])

    dumper_class.dump(args['class_file'])
