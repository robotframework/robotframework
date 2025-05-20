import os


class BinaryDataLibrary:

    def print_bytes(self):
        """Prints all bytes in range 0-255. Many of them are control chars."""
        for i in range(256):
            print(f"*INFO* Byte {i}: '{chr(i)}'")
        print("*INFO* All bytes printed successfully")

    def raise_byte_error(self):
        raise AssertionError(
            f"Bytes 0, 10, 127, 255: "
            f"'{chr(0)}', '{chr(10)}', '{chr(127)}', '{chr(255)}'"
        )

    def print_binary_data(self):
        print(os.urandom(100))
        print("*INFO* Binary data printed successfully")
