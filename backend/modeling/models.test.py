import unittest
import numpy
import models
import rechartsConverter
import parameters

class TextModelingFunctions(unittest.TestCase):

    def test_LARmodel(self):
        models.createLARModel(parameters.LAR, parameters.DELTA, parameters.XMU)


    def test_L2model(self):
        models.createQuadroModel(parameters.L2)


    def test_calibrate(self):
        inputData = ([0, 1, 2, 3], [-2, -4, -2, 3], [2, 4, 2, 1])
        outputData = models._calibrateData(*inputData)
        self.assertEqual(outputData, ([0, 1, 2, 3], [-2, -4, -2, 2], [2, 4, 2, 2]))


    def test_extrapolate(self):
        
        def compareSimilarList(l1, l2, eps = 1e-5):
            for i, j in zip(l1, l2):
                if abs(i - j) > eps:
                    return False
            return True

        inputData = ([-2, -1, 0, 1, 2], [-2, -1, 0, 1, 2], [4, 1, 0, 1, 4])
        outputArgs, outputNegative, outputPositive = models._extrapolateResults(*inputData, [-3, 4], 1)
        self.assertTrue(compareSimilarList(outputArgs, [-3, -2, -1, 0, 1, 2, 3]))
        self.assertTrue(compareSimilarList(outputNegative, [-3, -2, -1, 0, 1, 2, 3]))
        self.assertTrue(compareSimilarList(outputPositive, [9, 4, 1, 0, 1, 4, 9]))


    def test_nanFilter(self):
        nan = numpy.NaN
        inputData = ([0, 1, 2, 3], [2, 4, 6, nan], [-2, -4, -6, nan])
        outputData = models._nanFilter(*inputData)
        self.assertEqual(outputData, ([0, 1, 2], [2, 4, 6], [-2, -4, -6]))


    def _test_getSolution(self):
        pass


    def _test_getPoints(self):
        pass

    def test_converter(self):
        inputData = [{'value': 1000, 'args': [0, 1, 2], 'pv': [2, 3, 2], 'nv': [1, 0, 1]}, {'value': 2000, 'args': [0, 1], 'pv': [3, 4], 'nv': [2, 1]}]
        outputData = rechartsConverter.convertToRecharts(inputData)
        mustBeData = [{'name': 0, '1000+': 2, '1000-': 1, '2000+': 3, '2000-': 2}, {'name': 1, '1000+': 3, '1000-': 0, '2000+': 4, '2000-': 1}, {'name': 2, '1000+': 2, '1000-': 1}]
        self.assertEqual(outputData, mustBeData)


if __name__ == '__main__':
    unittest.main()
