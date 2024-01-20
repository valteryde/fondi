
import sys
sys.path.append('../src')

import unittest
import fondi

class TestMethods(unittest.TestCase):

    def __createMathText__(self, mathtext, filename, fontsize=50, color=(255,255,255,255)):
        txt = fondi.MathText(mathtext, fontsize, color)
        txt.image.save(filename)

    def testPolynomen(self):
        self.__createMathText__('2*x_{5}^{2}+7^{2}_{1}', 'polynomen.png')

    def testCases(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'cases.png')
    
    def testNestedFraction(self):
        self.__createMathText__('10+\\frac{\\frac{1}{2}}{x}', 'nested_fraction.png')

    def testBigFont(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'bigfont.png', 200)
    
    def testSmallFont(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'smallfont.png', 16)

    def testSuperSuber(self):
        self.__createMathText__('0,4x^{3}+2*x^{2}+5*x+c_{0}+5^{2}_{x}', 'supersub.png')
    
    def testrsquared(self):
        self.__createMathText__('R^2=0,9281', 'rsquared.png')

    def testrsquared(self):
        self.__createMathText__('R^2=0,9281', 'rsquared.png')

if __name__ == '__main__':
    unittest.main()
