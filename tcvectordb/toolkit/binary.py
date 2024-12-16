from typing import List, Union


def binary_to_uint8(binary_array: List[Union[int, float]]) -> List[int]:
    """Convert the binary array into an uint8 array, grouping every eight bits."""
    size = len(binary_array)
    if size % 8 != 0:
        raise ValueError("The length of the array must be a multiple of 8.")
    uint8_array = []
    for i in range(int(size / 8)):
        arr = binary_array[i*8: (i+1)*8]
        binary_string = ''.join(str(bit) for bit in arr)
        decimal_value = int(binary_string, 2)
        uint8_value = decimal_value & 0xFF
        uint8_array.append(uint8_value)
    return uint8_array
