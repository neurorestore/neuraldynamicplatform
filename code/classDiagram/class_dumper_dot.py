#!/usr/bin/python


from class_dumper import ClassDumper

def protectStr(string):
    return string.replace('<','\<').replace('>','\>')


class ClassDumperDOT(ClassDumper):
    def __init__(self,inheritance_flag=True, colaboration_flag=True):
        ClassDumper.__init__(self)
        self.encaps_symbol = {'public':'+','private':'-','protected':'#'} 
        self.inheritance_flag  = inheritance_flag
        self.colaboration_flag = colaboration_flag
        
    def dump(self,class_file,output_filename,**kwargs):
        sstr = 'digraph "test"\n{'
        sstr += """
edge [fontname="Helvetica",fontsize="10",labelfontname="Helvetica",labelfontsize="10"]; 
node [fontname="Helvetica",fontsize="10",shape=record];
"""

        sstr += ClassDumper.dump(self,class_file,**kwargs)
        sstr += "}"

        with open(output_filename,'w') as f:
            f.write(sstr)
            f.close()
        
        
    def dumpFile(self,c):
        sstr =  self.formatClassDeclaration(c)
        sstr += self.formatConstructors(c)
        sstr += self.formatMethods(c)
        sstr += self.formatMembers(c)
        sstr += '}"];\n'
        if (self.inheritance_flag): sstr += self.formatInheritance(c)
        if (self.colaboration_flag): sstr += self.formatCompositions(c)
                
        sstr += self.formatTypes(c)
        return sstr

    def formatClassDeclaration(self,c):
        sstr = '"{0}" '.format(c.name)
        sstr += '[label="{' + format(c.name) + "\\n"
        return sstr

    def formatInheritance(self,c):
        if c.inheritance is not None:
            sstr = ""
            for mother in c.inheritance:
                sstr += '"{0}" '.format(mother) + " -> " + '"{0}" '.format(c.name)
                sstr += '[style="solid",color="midnightblue",fontname="Helvetica",arrowtail="onormal",fontsize="10",dir="back"];\n'
            return sstr
        return ""


        
    def formatConstructors(self,c):
        sstr = ""
        for encaps in ['public','private', 'protected']:
            
            meths = c.getMethods(encaps)
            if c.name in meths:
                if sstr == "":  sstr = "|"
                sstr += self.encaps_symbol[encaps] + " "
                for cons in meths[c.name]:
                    sstr += self.formatMethod(c,cons)
                    sstr += "\\l"
            if '~' + c.name in meths:
                if sstr == "":  sstr = "|"
                sstr += self.encaps_symbol[encaps] + " "
                for cons in meths['~' + c.name]:
                    sstr += self.formatMethod(c,cons)
                    sstr += "\\l"

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
                        if sstr == "":  sstr = "|"
                        sstr += self.encaps_symbol[encaps] + " "
                        sstr += self.formatMethod(c,m)
                        sstr += "\\l"

        return sstr


    def formatMembers(self,c):
        sstr = ""

        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                
                for n,m in membs.iteritems():
                    if sstr == "":  sstr = "|"
                    sstr += self.encaps_symbol[encaps] + " "
                    sstr += self.formatMember(c,m)
                    sstr += "\\l"

        return sstr

    def formatCompositions(self,c):
        composition_set = set()
        for encaps in ['public','private', 'protected']:
            
            membs = c.getMembers(encaps)
            if len(membs) is not 0:
                for n,m in membs.iteritems():
                    if m.type in self.base_types: continue
                    composition_set.add(self.baseType(m.type))

        sstr = ""
        for t in composition_set:
            sstr += '"{0}" '.format(t) + " -> " + '"{0}" '.format(c.name)
            sstr += '[style="dashed",color="midnightblue",fontname="Helvetica",arrowtail="odiamond",fontsize="10",dir="back"];\n'

                
        return sstr


    def formatTypes(self,c):

        sstr = ""
        for encaps in ['public','private', 'protected']:
            if c.types[encaps] is not None:

                for t in c.types[encaps]:
                    if t in self.base_types: continue
                    sstr += '"{0}" '.format(c.name) + " -> " + '"{0}" '.format(t)
                    sstr += '[style="solid",color="black",fontname="Helvetica",arrowtail="odiamond",fontsize="10",dir="back"];\n'
        return sstr
        return ""


    def formatMethod(self,c,m):
        arg_types = list(m.args.iteritems())
        arg_types = [protectStr(a) for b,a in arg_types]
        sstr = ""
        if m.static: sstr += m.static + " "
        if m.ret:    sstr += protectStr(m.ret) + " "
        sstr += m.name + "(" + ",".join(arg_types) + ")"
        if m.virtual == 'pure virtual': sstr += "=0"
        return sstr

    def formatMember(self,c,m):
        sstr = ""
        if m.static == 'static': sstr += 'static '
        return sstr + protectStr(m.type) + " " + m.name












################################################################

    
import argparse
import subprocess
import os
    
if __name__ == '__main__':

    
    parser = argparse.ArgumentParser(description='DOT graph producer for class representation')
    parser.add_argument('--class_file','-c', help='The class file to process',required=True)
    parser.add_argument('--format','-f' , default="pdf", help='The format of the produced graph file')
    parser.add_argument('--output','-o' , help='The file to be produced')
    parser.add_argument('--colaboration_no' , action='store_false', help='Disable the collaboration output')
    parser.add_argument('--inheritance_no' , action='store_false', help='Disable the inheritance output')
    parser.add_argument('--classes' , type=str, help='The classes to output')
    
    args = parser.parse_args()
    args = vars(args)
    if args["output"] is None:
        args['output'] = os.path.splitext(args['class_file'])[0] + "." + args['format']

    if args["classes"] is not None:
        args["classes"] = args["classes"].split(',')

    inheritance_flag = True
    colaboration_flag = True
    if not args['inheritance_no'] : inheritance_flag = False
    if not args['colaboration_no'] : colaboration_flag = False        

    dumper_class = ClassDumperDOT(inheritance_flag, colaboration_flag)

    class_file = args['class_file']
    del args['class_file']
    dot_file = os.path.splitext(class_file)[0] + ".dot"
    dumper_class.dump(class_file,dot_file,**args)
    exe           = ['dot']
    option_format = ['-T'+args['format'] ]
    option_output = ['-o', args['output'] ]
    option_input  = [dot_file]
    subprocess.call(exe+option_format+option_output+option_input)

