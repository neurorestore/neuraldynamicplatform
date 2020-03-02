
class Typename:
    def __init__(self,name,encapsulation):
        self.name = name
        self.encapsulation = encapsulation


class Method:
    def __init__(self,name,args,ret,encapsulation,virtual,static,const,comments):

        self.name = name
        self.virtual = virtual
        self.static = static
        self.args = dict()
        for k,v in args:
            self.args[v] = k
        self.ret = ret
        self.encapsulation = encapsulation
        if self.encapsulation == '':
            self.encapsulation = 'public'
        self.comments = comments
        self.const = const
        #print "creating method {0}".format(name)
        #print self.__dict__

        
    def __str__(self):
        sstr = self.encapsulation + " "
        if not self.virtual == '': sstr += self.virtual + " "

        sstr += self.ret + " " + self.name + "("
        pairs = list(self.args.iteritems())
        pairs = [b + " " + a for a,b in pairs]
        sstr += ", ".join(pairs)
        sstr += ")"
        return sstr

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

class Member:
    def __init__(self,name,_type,encapsulation,static,comments):
        self.name = name
        self.type = _type
        self.encapsulation = encapsulation
        self.static = static
        self.comments = comments

    def __str__(self):
        return self.encapsulation + " " + self.type + " " + self.name

class ClassDescriptor:


    def __init__(self,name,inheritance=None):
        self.name = name 
        self.inheritance = inheritance 
        self.members = {'private':{},'public':{},'protected':{}}
        self.methods = {'private':{},'public':{},'protected':{}}
        self.types   = {'private':{},'public':{},'protected':{}}

    def addMethod(self,name,args,ret,encapsulation,virtual,static,const,comments):
        new_method = Method(name,args,ret,encapsulation,virtual,static,const,comments)
        if name not in self.methods[encapsulation]: self.methods[encapsulation][name] = set()
        self.methods[encapsulation][name].add(new_method)

    def addMember(self,name,_type,encapsulation,static,comments):
        new_member = Member(name,_type,encapsulation,static,comments)
        self.members[encapsulation][name] = new_member

    def addType(self,name,encapsulation):
        new_type = Typename(name,encapsulation)
        self.types[encapsulation][name] = new_type

    def getMembers(self,encapsulation=None):
        return self.members[encapsulation]

    def getTypes(self,encapsulation=None):
        return self.types[encapsulation]

    def getMethods(self,encapsulation=None):
        return self.methods[encapsulation]

    def __str__(self):
        sstr = "Class " + self.name + "\n"
        if (self.inheritance):
            sstr += "Inherit: "
            sstr += ",".join(self.inheritance) + "\n"
            
        sstr += "Methods:\n"
        for encaps,meths in self.methods.iteritems():
            sstr += encaps + ":\n"
            for name,m_list in meths.iteritems():
                for m in m_list:
                    sstr += str(m) + "\n"
        sstr += "\n"
        sstr += "Members:\n"
        for encaps,membs in self.members.iteritems():
            sstr += encaps + ":\n"
            for name,m in membs.iteritems():
                sstr += str(m) + "\n"       
        return sstr
        
if __name__ == '__main__':
    my_class = ClassDescriptor('dummy')
    my_class.addMethod('compute',[('int','arg1'),('double','arg2')],'bool','public','')
    my_class.addMember('res','double','private')
    print my_class
