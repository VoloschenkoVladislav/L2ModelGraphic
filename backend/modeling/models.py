from operator import pos
from sympy import symbols, core, exp, lambdify, solve
from scipy.interpolate import interp1d
from math import log
import numpy

def _calibrateData(args, negativeData, positiveData):
    '''
        Приведение экстраполированных данных к виду линий уровня
        ---
        ---
        Параметры:
        * args: List[float] - аргументы функции,
        * negativeData: List[float] - нижняя дуга значений функции,
        * positiveData: List[float] - верхняя дуга значений функции;
        ---
        Выход функции:
        * List[float] - аргументы функции,
        * List[float] - нижняя дуга значений функции,
        * List[float] - верхняя дуга значений функции;
    '''

    startCut = 0
    endCut = len(args)
    crossDone = False if negativeData[0] > positiveData[0] else True
    for ind, item in enumerate(zip(negativeData, positiveData)):
        if crossDone:
            if item[0] > item[1]:
                negativeData[ind - 1] = positiveData[ind - 1] = (item[0] + item[1]) / 2
                endCut = ind
                break
        else:
            if item[0] <= item[1]:
                negativeData[ind] = positiveData[ind] = (item[0] + item[1]) / 2
                startCut = ind
                crossDone = True
    if not crossDone:
        return [], [], []

    return args[startCut:endCut], negativeData[startCut:endCut], positiveData[startCut:endCut]

def _extrapolateResults(args, negativeData, positiveData, segment, arange):
    '''
        Экстраполяция недостающих данных
        ---
        ---
        Параметры:
        * args: List[float] - аргументы функции,
        * negativeData: List[float] - нижняя дуга значений функции,
        * positiveData: List[float] - верхняя дуга значений функции,
        * segment: [float, float] - область определения,
        * arange: int - кол-во отрезков разибения;
        ---
        Выход функции:
        * List[float] - аргументы функции,
        * List[float] - нижняя дуга значений функции,
        * List[float] - верхняя дуга значений функции;
    '''

    x0, x1 = segment[0], segment[1]
    try:
        fPositive = interp1d(args, positiveData, kind='cubic', fill_value='extrapolate')
        fNegative = interp1d(args, negativeData, kind='cubic', fill_value='extrapolate')
    except:
        raise ValueError('aborted')
    args = [i / arange for i in range(x0, x1)]
    positiveData = fPositive(args)
    negativeData = fNegative(args)

    return args, list(negativeData), list(positiveData)

def _nanFilter(args, negativeData, positiveData):
    '''
        Фильтрация полученных точек решения на NaN
        ---
        ---
        Параметры:
        * args: List[float] - аргументы функции,
        * negativeData: List[float] - нижняя дуга значений функции,
        * positiveData: List[float] - верхняя дуга значений функции;
        ---
        Выход функции:
        * List[float] - аргументы функции,
        * List[float] - нижняя дуга значений функции,
        * List[float] - верхняя дуга значений функции;
    '''

    negativeData_out = negativeData.copy()
    positiveData_out = positiveData.copy()
    args_out = args.copy()
    alreadyPoped = 0
    
    if len(negativeData) != len(positiveData) and len(positiveData) != len(args):
        raise AttributeError('lists must be similar length')
    for i, elem in enumerate(zip(args, negativeData, positiveData)):
        if numpy.isnan(elem[1]) or numpy.isnan(elem[2]):
            negativeData_out.pop(i - alreadyPoped)
            positiveData_out.pop(i - alreadyPoped)
            args_out.pop(i - alreadyPoped)
            alreadyPoped += 1
    return args_out, negativeData_out, positiveData_out

def createLARModel(tetta, delta, xmu):
    '''
        Создание уравнения LAR-модели
        ---
        ---
        Параметры:
        * tetta: List[float] - параметры модели,
        * delta: float - параметр масштаба,
        * xmu: float - точка пересечения;
        ---
        Выход функции:
        * sympy.core.add.Add - уравнение модели.
    '''

    def mu(x, delta, xmu):
        return 1 - 1 / (1 + exp(-1 * delta*(x - xmu)))

    x1, x2 = symbols('x1 x2')
    mu1, mu2 = mu(x1, delta, xmu), mu(x2, delta, xmu)
    out = core.add.Add()
    mult = [1, x1, x2, x1**2, x1*x2, x2**2, mu1, x1*mu1, x2*mu1, mu1*x1**2, mu1*x1*x2, mu1*x2**2, mu2, x1*mu2, x2*mu2, mu2*x1**2, mu2*x1*x2, mu2*x2**2]
    try:
        for i, j in zip(tetta, mult):
            out += i*j
        return out
    except:
        raise

def createQuadroModel(qp):
    '''
        Создание уравнения L2-модели
        ---
        ---
        Параметры:
        * qp: List[float] - параметры модели;
        ---
        Выход функции:
        * sympy.core.add.Add - уравнение модели.
    '''

    x1, x2 = symbols('x1 x2')
    out = core.add.Add()
    mult = [1, x1, x2, x1*x1, x1*x2, x2*x2]
    try:
        for i, j in zip(qp, mult):
            out += i*j
        return out
    except:
        raise
        
def getSolutionOfModel(model, value):
    '''
        Получение решения модели
        ---
        ---
        Параметры:
        * model: sympy.core.add.Add - уравнение модели,
        * value: float - выходная оценка модели;
        ---
        Выход функции:
        * List[Callable[[float, float], float]] - решение модели относительно второй переменной.
    '''

    x1, x2 = symbols('x1 x2')
    return [lambdify(x1, i) for i in solve(model - log(value), x2)]

def getPoints(modelEquationSolution, segment, arange):
    '''
        Получение точек значения функции
        ---
        ---
        Параметры:
        * modelEquationSolution: List[Callable[[float, float], float]] - решение модели относительно второй переменной,
        * segment: [float, float] - область определения, определяемая соотношением [segment0/arange, segment1/arange],
        * arange: int - кол-во отрезков разибения;
        ---
        Выход функции:
        * List[float] - аргументы функции,
        * List[float] - нижняя дуга значений функции,
        * List[float] - верхняя дуга значений функции;
    '''

    x0, x1 = segment[0], segment[1]
    args = [i / arange for i in range(x0, x1)]
    negativeData = [modelEquationSolution[0](i / arange) for i in range(x0, x1)]
    positiveData = [modelEquationSolution[1](i / arange) for i in range(x0, x1)]

    args, negativeData, positiveData = _nanFilter(args, negativeData, positiveData)
    args, negativeData, positiveData = _extrapolateResults(args, negativeData, positiveData, segment, arange)
    args, negativeData, positiveData = _calibrateData(args, negativeData, positiveData)

    return args, negativeData, positiveData
    