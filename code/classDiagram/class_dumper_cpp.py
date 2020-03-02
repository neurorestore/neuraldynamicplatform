#!/usr/bin/python

from class_dumper import ClassDumper
from class_reader import ClassReader
import os, re 

class ClassDumperCPP(ClassDumper):
    def __init__(self,output_dir):
        ClassDumper.__init__(self)
        self.output_dir = output_dir
        
    def dump(self,class_file,make_system="cmake"):
        cls_reader = ClassReader()
        classes = cls_reader.read(class_file)
        for c in classes:
            self.dumpHeader(c)
            self.dumpCCFile(c)

        self.dumpMain()
        self.dumpMakefile(classes)
        self.dumpCMake(classes)

        return ""

    def dumpMakefile(self,classes):
        make_filename = os.path.join(self.output_dir,'Makefile')
        CC_files     = [self.makeBaseFilename(c.name)+ ".cc" for c in classes]
        obj_files    = [self.makeBaseFilename(c.name)+ ".o" for c in classes]
        header_files = [self.makeBaseFilename(c.name)+ ".hh" for c in classes]
        sstr = """
CXXFLAGS=-g -Wall
CC_FILES     = {0}
OBJ_FILES    = {1}
HEADER_FILES = {2}

EXEC=main

$(EXEC): $(OBJ_FILES) main.o
\tg++ -g $(OBJ_FILES) main.o -o $@

.o: $(HEADER_FILES)
\tg++ -c $(CXXFLAGS) $^ -o $@

clean:
\trm -f *.o *~ $(EXEC)

""".format(" ".join(CC_files)," ".join(obj_files)," ".join(header_files))

        with open(make_filename,'w') as f:
            f.write(sstr)

    def dumpCMake(self,classes):
        make_filename = os.path.join(self.output_dir,'CMakeLists.txt')
        CC_files     = [self.makeBaseFilename(c.name)+ ".cc" for c in classes]
        obj_files    = [self.makeBaseFilename(c.name)+ ".o" for c in classes]
        header_files = [self.makeBaseFilename(c.name)+ ".hh" for c in classes]

        sstr = """
cmake_minimum_required (VERSION 2.6)
project (GeneratedFromCodeGenerator)

add_executable(main 
main.cc 
{0})
""".format("\n".join(CC_files))

        with open(make_filename,'w') as f:
            f.write(sstr)


    def dumpMain(self):
        main_filename   = os.path.join(self.output_dir,"main.cc")
        with open(main_filename,'w') as f:
            f.write("""
#include <cstdio>
#include <cstdlib>
#include <iostream>
            
int main(int argc, char ** argv){

/// ... your code here ...

  return EXIT_FAILURE;
}""")

    def makeBaseFilename(self,class_name):
        name = re.sub(r'([0-9]|[A-Z0-9])','_\g<1>',class_name)
        name = name.lower()
        
        if name[0] == '_':
            name = name[1:]
        return name
        
    def dumpHeader(self,c):

        basename = self.makeBaseFilename(c.name)
        header_filename = os.path.join(self.output_dir,basename+".hh")
        
        self.stage = 'header'
        sstr =  self.formatClassDeclaration(c)
        sstr += self.formatConstructors(c)
        sstr += self.formatMethods(c)
        sstr += self.formatMembers(c)
        sstr += "};\n" 

        with open(header_filename,'w') as f:
#            print header_filename
            f.write("#ifndef __" + basename.upper() + "__HH__\n")
            f.write("#define __" + basename.upper() + "__HH__\n\n")
            f.write("/* -------------------------------------------------------------------------- */\n")

            if c.inheritance is not None:
                for herit in c.inheritance:
                    f.write("#include \"" + self.makeBaseFilename(herit) + ".hh\"\n")                

#            if c.members is not None:
#                for encaps,membs in c.members.iteritems():
#                    for name,m in membs.iteritems():
#                        if m.type in self.base_types: continue
#                        f.write("#include \"" + self.makeBaseFilename(self.baseType(m.type)) + ".hh\"\n")                
#
            f.write(sstr)
            f.write("\n/* -------------------------------------------------------------------------- */\n")
            f.write("#endif //__" + basename.upper() + "__HH__\n")


            

    def dumpCCFile(self,c):

        basename = self.makeBaseFilename(c.name)
        CC_filename = os.path.join(self.output_dir,basename+".cc")
        header_filename = os.path.join(self.output_dir,basename+".hh")

        self.stage = 'CC'
        sstr = self.formatConstructors(c)
        sstr += self.formatMethods(c)

        with open(CC_filename,'w') as f:
#            print CC_filename
            f.write("#include \"" + os.path.basename(header_filename) + "\"\n")
            f.write("/* -------------------------------------------------------------------------- */\n\n")
            f.write(sstr)

    def formatClassDeclaration(self,c):
        sstr = """
/**
  * Documentation TODO
  */
  
"""
  
        sstr += "class " + c.name

        if c.inheritance is not None:
            sstr += ": public " + ", public ".join(c.inheritance)
            
        sstr += "{\n"
        return sstr


        
    def formatConstructors(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            meths = c.getMethods(encaps)
            if c.name in meths:
                if self.stage == 'header': sstr += encaps + ':\n\n'
                for m in meths[c.name]:
                    sstr += self.formatMethod(c,m)
            if '~' + c.name in meths:
                if self.stage == 'header' and sstr == "": sstr += encaps + ':\n\n'
                for m in meths['~' + c.name]:
                    sstr += self.formatMethod(c,m)
        

        if not sstr == "" and self.stage == 'header': 
            sstr = """
  /* ------------------------------------------------------------------------ */
  /* Constructors/Destructors                                                 */
  /* ------------------------------------------------------------------------ */

""" + sstr 

        return sstr


    def formatMethods(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            meths = c.getMethods(encaps)
            meths_names = set(meths.keys()) - set([c.name,'~'+c.name])
            meths_names = list(meths_names)
            if len(meths_names) is not 0:
                if self.stage == 'header': sstr += encaps + ':\n\n'

                for n in meths_names:
                    for m in meths[n]:
                        sstr += self.formatMethod(c,m)
                sstr += "\n"

        if not sstr == "" and self.stage == 'header':
            sstr = """
  /* ------------------------------------------------------------------------ */
  /* Methods                                                                  */
  /* ------------------------------------------------------------------------ */

""" + sstr

        return sstr


    def formatMembers(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                if self.stage == 'header': sstr += encaps + ':\n\n'

                for n,m in membs.iteritems():
                    sstr += self.formatMember(c,m)
                sstr += "\n"

        if not sstr == "" and self.stage == 'header':
            sstr = """
  /* ------------------------------------------------------------------------ */
  /* Members                                                                  */
  /* ------------------------------------------------------------------------ */

""" + sstr

        return sstr



    def formatMethod(self,c,m):

        if self.stage == 'header':
            sstr =  "  //! Documentation TODO\n"
            sstr += "  "

            if m.static: sstr += m.static + " "
            if m.virtual in ['virtual','pure virtual']:
                sstr += "virtual "
            if (not m.ret == ""): sstr += m.ret + " "
            sstr += m.name + "("
            sstr += ", ".join([a + " " + b for b,a in list(m.args.iteritems())])
            sstr +=  ")"
            if m.virtual == 'pure virtual': sstr += "=0"
            sstr += ";\n"

        if self.stage == 'CC':
            sstr = ""
            if m.virtual == 'pure virtual': return ""

            sstr += m.ret + " " + c.name + "::" + m.name + "("
            sstr += ", ".join([a + " " + b for b,a in list(m.args.iteritems())])
            sstr +=  "){\n\n}\n\n"
            sstr += "\n"
            sstr += """
/* --------------------------------------------------------------------------- */

"""

            
        return sstr

    def formatMember(self,c,m):
        sstr = "  //!Documentation TODO\n"
        sstr += "  "
        if m.static == 'static': sstr += 'static '
        sstr += m.type + " " + m.name + ";\n"
        return sstr

import argparse
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='CPP project producer for class representation')
    parser.add_argument('--class_file','-c', help='The class file to process',required=True)
    parser.add_argument('--output_dir','-o' , help='The directory where to put produced files',required=True)

    args = parser.parse_args()
    args = vars(args)
    os.makedirs(args['output_dir'])
    dumper_class = ClassDumperCPP(args['output_dir'])

    dumper_class.dump(args['class_file'])
