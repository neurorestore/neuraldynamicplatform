import re
from class_decriptor import ClassDescriptor

class ClassReader:

    def __init__(self):
        self.classes = []
        self.current_class = None

    def read(self,filename):
        self.filename = filename
        f = open(self.filename,'r')
        self.line_cpt = 0
        for line in f:
            self.readline(line)
            self.line_cpt += 1

        if self.current_class is not None:
            self.classes.append(self.current_class)
        
        return self.classes


    def readline(self,line):
        line = line.split('#')[0]
        line = line.strip()
        if line == "": return
        try:
                if self.isNewClassTag(line): return
                if self.isNewMethodTag(line): return
                if self.isNewTypedef(line): return
                if self.isNewMemberTag(line): return
                else: raise Exception('Unknown tag')
        except Exception as e:
                raise Exception(self.filename + ":{0}".format(self.line_cpt+1) + ":'" + line + "' : " + str(e))
        
        
    def isNewClassTag(self,line):
        ret = False
        m = re.match(r'class\s+(\S*)',line)
        if m:
            name        = m.group(1)
            inheritance = None           
            ret = True

        m = re.match(r'class\s+(\S*)\((.*)\)',line)
        if m: 
            name        = m.group(1).strip()
            inheritance = m.group(2).strip()
            inheritance = inheritance.strip().split(',')
            inheritance = [e.strip() for e in inheritance] 
            ret = True
            
        if ret == False: return False
        
        if self.current_class is not None:
                self.classes.append(self.current_class)
                
        self.current_class = ClassDescriptor(name,inheritance)
        
        return True

    def isNewMemberTag(self,line):
        if not line.find("(") == -1: return False
        if not line.find(")") == -1: return False
        m = re.match(r'((?:public|protected|private)*)\s*((?:static)?)\s*((?:\S|(?:\s+\*)|(?:\s+\&))+)\s+(\S*)[\s|;]*(?://)*(.*)',line)
        if m: 
            encapsulation = m.group(1).strip()
            static        = m.group(2).strip()
            _type         = m.group(3).strip()
            name          = m.group(4).strip()
            comments      = m.group(5).strip()
            name = name.replace(';','')
            self.current_class.addMember(name,_type,encapsulation,static,comments)
            return True
        return False

    def isNewTypedef(self,line):

        if not line.find("(") == -1: return False
        if not line.find(")") == -1: return False
        m = re.match(r'((?:public|protected|private)*)\s*typedef\s*(\S+)',line)
        if m: 
            encapsulation = m.group(1).strip()
            name          = m.group(2).strip()
            name = name.replace(';','')
            self.current_class.addType(name,encapsulation)
            return True
        return False

    def isNewMethodTag(self,line):
        m = re.match(r'((?:public|protected|private)*)\s*((?:static)?)\s*((?:virtual|pure virtual)?)\s*(.*)\s+([\S|~]*)\((.*)\)\s*((?:const)?)[\s|;]*(?://)*(.*)',line)
        if m: 
            encapsulation = m.group(1).strip()
            static        = m.group(2).strip()
            virtual       = m.group(3).strip()
            ret           = m.group(4).strip()
            name          = m.group(5).strip()
            args          = m.group(6).strip().split(',')
            const         = m.group(7).strip()
            comments      = m.group(8).strip()
            args = [list(e.strip().split(' ')) for e in args]
            temp_args = []
            for l in args:
                if len(l) >= 2: 
                    temp_args.append(tuple([" ".join(l[:-1]),l[-1]]))
            args = temp_args
            args = [e for e in args if not e[0] == '']
            self.current_class.addMethod(name,args,ret,encapsulation,virtual,static,const,comments)
            return True
        return False

            

if __name__ == '__main__':
    cls_reader = ClassReader()
    classes = cls_reader.read('test.classes')
    for c in classes:
        print c
