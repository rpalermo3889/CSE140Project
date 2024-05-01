# pc = 0
# next_pc = 0

class if_ex_register:
    def __init__(self):
        self.next_pc = 0
        self.pc = 0

if_ex = if_ex_register()

def Fetch():
    global if_ex

    pc = if_ex.pc   # input

    pc = pc + 1
    
    if_ex.pc = pc   # output

    print("if_ex.pc: ", if_ex.pc)


def Execute():
    global if_ex
    pc = if_ex.pc   # input

    next_pc = pc

    if_ex.next_pc = next_pc     # output

    print("if_ex.next_pc: ", if_ex.next_pc) 

def main():
    global if_ex
    print("Hello")
    
    i = 0
    while i < 2:
        i+=1        
        Fetch()
        Execute()

        next_pc = if_ex.next_pc

        print("next_pc: ", next_pc)

if __name__ == "__main__":
    main()

"""


Expected Output:

Hello
next_pc:  1
next_pc:  2

#=========================
pc = 0
next_pc = 0

class if_ex_register:
    def __init__(self):
        self.next_pc = 0
        self.pc = 0

if_ex = if_ex_register()

def Fetch():
    global pc
    pc = pc + 1


def Execute():
    global pc, next_pc
    next_pc = pc

def main():    
    print("Hello")
    
    i = 0
    while i < 2:
        i+=1

        Fetch()
        Execute()

        print("next_pc: ", next_pc)

if __name__ == "__main__":
    main()
#=========================

#================================

Expected Output:

Hello
next_pc:  0
next_pc:  1

pc = 0
next_pc = 0

def Fetch():
    global pc, next_pc
    next_pc = pc

def Execute():
    global pc
    pc += 1

def main():    
    print("Hello")
    
    i = 0
    while i < 2:
        i+=1

        Fetch()
        Execute()

        print("next_pc: ", next_pc)

if __name__ == "__main__":
    main()

"""