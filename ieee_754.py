def from_binary_to_decimale(s: str) -> int:
    num = 0

    for i, x in enumerate(reversed(s)):
        num += int(x)*2**i

    return num


def from_point_to_binary(n):
    binary = ''

    while(n):
        n *= 2

        if n >= 1:
            binary += '1'
            n -= 1
        else:
            binary += '0'
        
        if len(binary) > 50:
            break
        
    return binary


def from_binary_to_point(s: str) -> float:
    num = 0

    for i, x in enumerate(s):
        num += int(x)*2**-(i + 1)

    return num


def from_binary_to_hexadecimale(s: str) -> str:
    hexadecimale = hex(int(s.replace('|', ''), 2))

    if len(hexadecimale) - 2 < ieee_ex:
        hexadecimale += '0' * (ieee_ex - len(hexadecimale))

    return hexadecimale


def len_corrector(s: str) -> str:
    if len(s) < ieee_len + 2:
        s += '0' * (ieee_len + 2 - len(s))
    if len(s) > ieee_len + 2:
        s = s[:ieee_len + 2]

    return s


def separator(s: str) -> tuple:
    final_number = 0
    final_binary = ''
    
    s = len_corrector(s)
    s_split = s.split('|')

    sign = s_split[0]
    exponent = from_binary_to_decimale(s_split[1]) - (2**(ieee_ex - 1) - 1)
    mantissa = '1.' + s_split[2]

    final_binary = mantissa
    for dot_index in range(exponent + 1):
        final_binary = final_binary.replace('.', '')
        final_binary = final_binary[:dot_index + 1] + '.' + final_binary[dot_index + 1:]

    final_binary_split = final_binary.split('.')
    final_number += from_binary_to_decimale(final_binary_split[0])
    final_number += from_binary_to_point(final_binary_split[1])

    if sign == '1':
        final_number = -(final_number)

    hexadecimal = from_binary_to_hexadecimale(s)
    hexadecimal = hexadecimal[:2] + hexadecimal[2:].upper()

    return s, final_number, hexadecimal


def float_separetor(s: int) -> tuple:
    sign = 0
    if s < 0 :
        sign = 1

    s_float = abs(s)
    s_bin = bin(int(s_float))[2:]
    s_binary = f'{s_bin}.{from_point_to_binary(s_float - int(s_float))}'
    
    neg_point_index = 0
    point_index = 0
    while True:
        dot_index = s_binary.index('.')
        
        if '1' in s_binary[:dot_index]:
            if neg_point_index < 0:
                point_index = neg_point_index
                break

            point_index = -(s_binary.index('1') + 1 - s_binary.index('.'))
            break

        s_binary = s_binary.replace('.', '')
        dot_index += 1
        s_binary = s_binary[1:dot_index] + '.' + s_binary[dot_index:]
        neg_point_index -= 1
    
    exponent = bin(point_index + (2**(ieee_ex - 1) - 1))[2:]
    if len(exponent) < ieee_ex:
        exponent = '0' * (ieee_ex - len(exponent)) + exponent[0:]

    mantissa = s_binary.replace('.', '')[1:]

    ieee = len_corrector(f'{sign}|{exponent}|{mantissa}')
    hexadecimal = from_binary_to_hexadecimale(ieee)
    hexadecimal = hexadecimal[:2] + hexadecimal[2:].upper()
    mantissa = '1.' + mantissa

    return ieee, sign, str(exponent), mantissa[:(ieee_len - ieee_ex + 1)], hexadecimal


def hex_separetor(s: str) -> tuple:
    if '0x' in s[:2] or '0X' in s[:2]:
        s = s[2:]

    hex_binary = bin(int(s, 16))[2:].zfill(len(s)*4)
    new_hex_binary = hex_binary[:1] + '|' + hex_binary[1:(ieee_ex + 1)] + '|' + hex_binary[(ieee_ex + 1):]

    return separator(new_hex_binary)


def ieee_size_settings(ieee_size: int):
    ieee = {
        16: 5, 
        32: 8, 
        64: 11
        }

    global ieee_len, ieee_ex

    ieee_len = ieee_size
    ieee_ex = ieee[ieee_len]


def from_ieee_to_float(ieee_size: str, s: str):
    ieee_size_settings(int(ieee_size))

    return separator(s)


def from_float_to_ieee(ieee_size: str, num: str):
    ieee_size_settings(int(ieee_size))

    return float_separetor(float(num))


def from_hexadecimal_to_ieee(ieee_size: str, s: str):
    ieee_size_settings(int(ieee_size))

    return hex_separetor(s)


if __name__ == '__main__':
    ieee_size = input('IEEE-754 size: ')
    choice = input('1 - Float to IEEE-754\n2 - IEEE-754 to Float\n3 - HEX to IEEE-754\nChoice: ')

    if choice == '1':
        num = float(input('\nNumber: '))
        ieee, sign, exponent, mantissa, hexadecimal = from_float_to_ieee(ieee_size, num)
        
        print(f'IEEE-754: {ieee}')
        print(f'Hexadecimal: {hexadecimal}\n')
        print(f'Sign: {sign}')
        print(f'Exponent: {exponent}')
        print(f'Mantissa: {mantissa}')
        
    elif choice == '2':
        s = input('\nSequence: ')

        ieee, num, hexadecimal = from_ieee_to_float(ieee_size, s)

        print(f'Number: {num}')
        print(f'IEEE-754: {ieee}')
        print(f'Hexadecimal: {hexadecimal}')
    
    elif choice == '3':
        s = input('\nSequence: ')
        
        ieee, num, hexadecimal = from_hexadecimal_to_ieee(ieee_size, s)

        print(f'Number: {num}')
        print(f'IEEE-754: {ieee}')
        print(f'Hexadecimal: {hexadecimal}')

    else:
        print('Invalid choice!')