import base64

def bitfield(n):
    '''
    Obtains the binary array from the number
    '''
    return [1 if digit=='1' else 0 for digit in bin(n)[2:]]

def shifting(bitlist):
    '''
    Obtain the number from the binary array
    '''
    out = 0
    for bit in bitlist:
        out = (out << 1) | bit
    return out

def true_in_list(l):
    return [i for i,v in enumerate(l) if v]

def pad_left_list(l, size, pad_value):
    for n in range(len(l), size):
        l = [pad_value] + l
    return l

def pad_right_list(l, size, pad_value):
    for n in range(len(l), size):
        l = l + [pad_value]
    return l

# toggleBit() returns an integer with the bit at 'offset' inverted, 0 -> 1 and 1 -> 0.
def toggleBit(int_type, offset):
    mask = 1 << offset
    return(int_type ^ mask)

# setBit() returns an integer with the bit at 'offset' set to 1.

def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

# clearBit() returns an integer with the bit at 'offset' cleared.

def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)


