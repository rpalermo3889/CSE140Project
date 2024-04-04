# Global variables
pc = 0

def Fetch():
    pc += 4


# Main function
def main():
    # Ask the user for the filename
    filename = input("Enter the program file name to run:\n")

    # Open and read the input program text file
    with open(filename, "r") as file:
        instructions = file.readlines()
    
        for instr in instructions:
            # Fetch
            

if __name__ == "__main__":
    main()