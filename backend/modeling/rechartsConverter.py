def convertToRecharts(inputData):
    '''
        Конвертация выходных данных в Recharts-формат
        ---
        ---
        Параметры:
        * inputData: List[dictionary] - выходные данные;
        ---
        Выход функции:
        * List[dictionary] - сконвертированные выходные данные.
        * List[str] - список именований линий графика
    '''

    args = max(inputData, key = lambda item: len(item['args']))['args']
    outData = []
    values = []
    for arg in args:
        obj = {}
        obj['name'] = arg
        for data in inputData:
            try:
                ind = data['args'].index(arg)
                valuePlus, valueMinus = str(data['value']) + '+', str(data['value']) + '-'
                obj[valuePlus] = data['pv'][ind]
                obj[valueMinus] = data['nv'][ind]
                values.extend([valuePlus, valueMinus])
            except IndexError:
                continue
            except ValueError:
                continue
        outData.append(obj)
    return { 'data': outData, 'values': values }
