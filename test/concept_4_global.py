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
Expected Output:

Hello
next_pc:  0
next_pc:  1

"""