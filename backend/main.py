from flask import Flask, request, jsonify
from werkzeug.wrappers import response 
import modeling.models as modeling
from modeling.rechartsConverter import convertToRecharts
import modeling.parameters as parameters

app = Flask(__name__)

#not finished
@app.route('/')
def index():
    return 'Hello, world'

@app.route('/testdata', methods = ['POST'])
def testData():
    res = jsonify([{'name': 0, '1000+': 2, '1000-': 1, '2000+': 3, '2000-': 2}, {'name': 1, '1000+': 3, '1000-': 0, '2000+': 4, '2000-': 1}, {'name': 2, '1000+': 2, '1000-': 1, '2000+': 3, '2000-': 2}])
    return res

@app.route('/getdata', methods = ['POST'])
def getData():
    '''
        Получение данных для построения графика (POST)
        ---
        ---
        Входные данные:
        {
            parameters: {
                tetta: [float],
                delta: float,
                : float
            } | 'default',
            model: 'LAR'|'L2',
            values: [float]
        }
        ---
        Выходные данные:
        {
            data: {
                [
                    name: float,
                    [string]: [float],
                    ...
                ]
            },
            headers: [string]
        }
    '''

    data = request.get_json()

    if data['model'] == 'LAR':
        if data['parameters'] == 'default':
            tetta = parameters.LAR
            delta = parameters.DELTA
            xmu = parameters.XMU
        else:
            tetta = list(map(lambda x: float(x), data['parameters'][:2]))
            delta = float(data['parameters'][0])
            xmu = float(data['parameters'][1])
        model = modeling.createLARModel(tetta, delta, xmu)
    elif data['model'] == 'L2':
        if data['parameters'] == 'default':
            qp = parameters.L2
        else:
            qp = list(map(lambda x: float(x), data['parameters']))
        model = modeling.createQuadroModel(qp)
    else:
        return 'Model not found', 401

    out = []
    for i in data['values']:
        solution = modeling.getSolutionOfModel(model, float(i))
        args, negative, positive = modeling.getPoints(solution, [-100, 100], 100)
        out.append({'value': i, 'args': args, 'pv': positive, 'nv': negative})
    respon = convertToRecharts(out)
    return jsonify(respon)


if __name__ == '__main__':
    app.run()
