import sys

#data = sys.stdin.readline()

#print("Output: ",data)
"""
try:
    for line in sys.stdin:
        line = line.strip()
        if line:
            print(f"Read: {line}")
except KeyboardInterrupt:
    print("\nInterrupted by user.")
"""

#print("Enter text (type 'exit' to quit):")

bitZac1 = 0
bitZac2 = 0
niz = ""
niz_list = []


while True:
    try:
        #print(bitZac1, bitZac2)
        line = sys.stdin.readline()

        if not line:
            #print("\nEnd of input detected.")
            break

        line = line.strip()
        list_out = line.split()
        for x in range(0, len(list_out), 2):
            bit0 = list_out[x]
            bit1 = list_out[x + 1]
            #print(list_out)
            if (bitZac1 == 0) and (bitZac2 == 0):
                if (4000 < int(bit0) < 10000) and (4000 < int(bit1) < 5000):
                    bitZac1 = bit0
                    bitZac2 = bit1
                    #continue
                #for x in range(2, len(list_out[2:]), 2):
            elif 310 < int(bit0) < 800:
                if int(bit1) < 1000:
                    #bit_list.append(0)
                    niz += "0"
                elif 1000 < int(bit1) < 2000:
                    #bit_list.append(1)
                    niz += "1"
                elif int(bit1) > 2000:
                    #print("Koncano.")
                    #print("\n")
                    print(len(niz), niz)
                    #print("-" * len(niz))
                    niz_list.append(niz)
                    niz = ""
                    bitZac1 = 0
                    bitZac2 = 0
                    #continue
            else:
                print("Error")
                break

        if line.lower() == "exit":
            print("Existing program.")
            break

        #print(f"You entered: {line}")
        #print(list_out)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Exiting.")
        break
    except Exception as e:
        print(f"Error reading input: {e}")
        break