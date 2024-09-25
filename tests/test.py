
import sys
sys.path.append('../src')

import unittest
import fondi

class TestMethods(unittest.TestCase):

    def __createMathText__(self, mathtext, filename, fontsize=50, color=(255,255,255,255)):
        txt = fondi.MathText(mathtext, fontsize, color)
        txt.image.save(filename)

    def testPolynomen(self):
        self.__createMathText__('2*x_{5}^{2}+7^{2}_{1}', 'images/polynomen.png')

    def testCases(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'images/cases.png')
    
    def testNestedFraction(self):
        self.__createMathText__('10+\\frac{\\frac{1}{2}}{x}', 'images/nested_fraction.png')

    def testBigFont(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'images/bigfont.png', 200)
    
    def testSmallFont(self):
        self.__createMathText__('f(x^2)=\\cases{2*x}{10>x}{[2^{x}]}{10<x}{\\frac{1}{2}}{else}', 'images/smallfont.png', 16)

    def testSuperSuber(self):
        self.__createMathText__('0,4x^{3}+2*x^{2}+5*x+c_{0}+5^{2}_{x}', 'images/supersub.png')
    
    def testrsquared(self):
        self.__createMathText__('R^2=0,9281', 'images/rsquared.png')

    def testrsquared(self):
        self.__createMathText__('R^2=0,9281', 'images/rsquared.png')
    
    def testSquareRoot(self):
        self.__createMathText__('\\sqrt{10^{2+1}}', 'images/sqrt.png')
    
    def testSomethingCrazy(self):
        self.__createMathText__('\\sin(\\frac{x^2 + (10+2)_{hej}}{\\frac{2}{x}_{i,j}})', 'images/para.png')

    def testIntegral(self):
        return
        self.__createMathText__('\\int{2x}{dx}', 'images/integral.png')


    def testSpaces(self):
        self.__createMathText__('100\\quad000', 'images/10000a.png')
        self.__createMathText__('100\\,000', 'images/10000b.png')
        self.__createMathText__('100\\:000', 'images/10000c.png')
        self.__createMathText__('100\\;000', 'images/10000d.png')
        self.__createMathText__('100\\smallSpace000', 'images/10000e.png')
        self.__createMathText__('100\\qquad000', 'images/10000f.png')

    def test18x(self):
        self.__createMathText__('18x+\\ln{2*x}', 'images/18x.png')


if __name__ == '__main__':
    unittest.main()
    #TestMethods().testIntegral()
    #TestMethods().test18x()
