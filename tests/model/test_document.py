import unittest
from tcvectordb.model.document import Filter


class TestFilter(unittest.TestCase):
    """test **kwargs"""

    def test_In(self):
        filter_in_01 = Filter.In("id", ["1", "2"])
        filter_in_02 = Filter.In("id", [1, 2])
        self.assertEqual(filter_in_01, 'id in ("1","2")')
        self.assertEqual(filter_in_02, 'id in (1,2)')

    def test_include(self):
        filter_in_01 = Filter.Include("name", ["aa"])
        self.assertEqual(filter_in_01, 'name include ("aa")')
        filter_in_02 = Filter.Include("name", ["aa", "bb"])
        self.assertEqual(filter_in_02, 'name include ("aa","bb")')
        filter_in_03 = Filter('age=20').And(Filter.Include("name", ["aa", "bb"])).And('sex="man"')
        self.assertEqual(filter_in_03.cond, 'age=20 and name include ("aa","bb") and sex="man"')

    def test_exclude(self):
        filter_in_01 = Filter.Exclude("name", ["aa"])
        self.assertEqual(filter_in_01, 'name exclude ("aa")')
        filter_in_02 = Filter.Exclude("name", ["aa", "bb"])
        self.assertEqual(filter_in_02, 'name exclude ("aa","bb")')
        filter_in_03 = Filter('age=20').And(Filter.Exclude("name", ["aa", "bb"])).And('sex="man"')
        self.assertEqual(filter_in_03.cond, 'age=20 and name exclude ("aa","bb") and sex="man"')

    def test_include_all(self):
        filter_in_01 = Filter.IncludeAll("name", ["aa"])
        self.assertEqual(filter_in_01, 'name include all ("aa")')
        filter_in_02 = Filter.IncludeAll("name", ["aa", "bb"])
        self.assertEqual(filter_in_02, 'name include all ("aa","bb")')
        filter_in_03 = Filter('age=20').And(Filter.IncludeAll("name", ["aa", "bb"])).And('sex="man"')
        self.assertEqual(filter_in_03.cond, 'age=20 and name include all ("aa","bb") and sex="man"')


# 运行测试
if __name__ == '__main__':
    unittest.main()
