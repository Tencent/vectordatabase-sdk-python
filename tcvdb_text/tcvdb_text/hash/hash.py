from typing import Union, Callable

import mmh3


class Hash:

    @staticmethod
    def mmh3_hash(text: Union[str, int]) -> int:
        """Use mmh3 to hash text to 32-bit unsigned integer

        Args:
            text: 文本

        Returns:
            hash值
        """
        if isinstance(text, int):
            return text
        if not isinstance(text, str):
            raise TypeError(f"input text({text}) must be a str or int")
        return mmh3.hash(text, signed=False)


def hash_function_from_name(hash_function_name: str) -> Callable[[Union[str, int]], int]:
    if hash_function_name == "mmh3_hash":
        return Hash.mmh3_hash
    else:
        raise ValueError("no such hash function")
