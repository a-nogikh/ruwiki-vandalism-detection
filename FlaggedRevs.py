from bitarray import bitarray
import glob
import pickle

class FlaggedRevs:
    def __init__(self, mask):
        self.bits = bitarray(100000000)  # 100 mln
        self.bits.setall(False)
        for file in glob.glob(mask):
            print(file)
            f = open(file)
            buffer = ""
            while True:
                new_buffer = f.read(1024)
                if not new_buffer:
                    break
                buffer += new_buffer
                parts = buffer.split(' ')
                buffer = parts[-1]

                del parts[-1]
                for x in parts:
                    self.bits[int(x)] = True

    def exists(self, x):
        return self.bits.length() > x and self.bits[x]


class FlaggedTools:
    @staticmethod
    def save(instance: FlaggedRevs, name: str):
        output = open(name, 'wb')
        pickle.dump(instance, output)

    @staticmethod
    def load(name: str) -> FlaggedRevs:
        pkl_file = open(name, 'rb')
        return pickle.load(pkl_file)
