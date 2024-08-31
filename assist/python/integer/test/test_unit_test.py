import unittest
from ddt import ddt, data, unpack


class CustomTestResult(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exceptions = []

    def addError(self, test, err):
        super().addError(test, err)
        self.exceptions.append(err)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.exceptions.append(err)


@ddt
class TestAddition(unittest.TestCase):

    @data((1, 2, 3), (4, 5, 9), (-1, 1, 0))
    @unpack
    def test_add(self, a, b, expected):
        try:
            result = a + b
            self.assertEqual(result, expected)
        except Exception as e:
            raise e


if __name__ == '__main__':
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAddition)
    runner.run(suite)