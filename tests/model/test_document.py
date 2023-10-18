import unittest
from tcvectordb.model.document import Filter


class TestFilter(unittest.TestCase):
    """test **kwargs"""

    def test_In(self):
        filter_in_01 = Filter.In("id", ["1", "2"])
        filter_in_02 = Filter.In("id", [1, 2])
        self.assertEqual(filter_in_01, 'id in ("1","2")')
        self.assertEqual(filter_in_02, 'id in (1,2)')


# 运行测试
if __name__ == '__main__':
    unittest.main()
