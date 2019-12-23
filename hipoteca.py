from flask import Flask, render_template, flash, request, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import IntegerRangeField
from io import BytesIO
import base64
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class Hipoteca(object):
    def __init__(self, prestado=0, tae=0, plazoA=0):
        self.prestado = prestado
        self.tae = tae
        self.plazoA = plazoA
        # print(prestado, tae, plazoA)

    def calc(self):
        taeM = self.tae / 1200
        plazo = self.plazoA * 12
        restante = self.prestado
        interes = 0
        cuota = 0
        while restante > 0:
            restante = self.prestado
            interes = 0
            cuota += 1
            interesList = []
            for _ in range(plazo):
                # FIXME esto seguro que puede ser más eficiente
                interesM = restante * taeM
                interes += interesM
                interesList.append(interesM)
                restante -= (cuota - interesM)
        print(restante, interes, cuota)
        return int(cuota), interes, self.histogram(interesList, cuota), self.pieChart(self.prestado, interes)

    def pieChart(self, cantidad, intereses):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        labels = 'Intereses', 'Amortización'
        total = cantidad + intereses
        sizes = [intereses / total, cantidad / total]
        explode = (0.1, 0)  # only "explode" the 2nd slice
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ### Rendering Plot in Html
        plt.savefig('site/pie.png')
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        return str(figdata_png)[2:-1]

    def histogram(self, interesList, cuota):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        counts = [x for x in range(len(interesList))]
        counts = [counts, counts]
        amortizacion = [cuota - x for x in interesList]
        lista = [interesList, amortizacion]
        plt.figure(figsize=(10, 5))
        plt.hist(counts, bins=range(1, max(counts[0]) + 2), align='left', weights=lista, stacked=True)
        plt.xticks(range(1, max(counts[0]) + 1, 12))
        # the histogram of the data
        # n, bins, patches = plt.hist(x, 6, normed=1, facecolor='g', alpha=0.75)
        plt.xlabel('Cuota (mes)')
        plt.ylabel('Cantidad (€)')
        plt.title('Interés + amortización ')
        # TODO mejorar la leyenda
        plt.text(len(interesList) / 2, cuota / 2,
                 "Azul = Interés\nNaranja = Amortización\nCuota mensual = " + str(cuota) + " €",
                 fontsize=14)
        # plt.axis([40, 160, 0, 0.03])
        plt.grid(True)

        ### Rendering Plot in Html
        # En servidor:
        # plt.savefig('/site/imagen.png')
        # en linux:
        plt.savefig('site/histogram.png')
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue())
        return str(figdata_png)[2:-1]

hipoteca = Hipoteca()

class ReusableForm(Form):
    cantidad = TextField('Cantidad (€):', validators=[validators.required()])
    plazo = TextField('Plazo (años):', validators=[validators.required()])
    interes = TextField('Interés (TAE, %):', validators=[validators.required()])
    age = IntegerRangeField('Cantidad (€)', default=90000)

 
@app.route("/cuota", methods=['GET', 'POST'])
def cuota():
    form = ReusableForm(request.form)
    print(form.errors)
    histogramImage = None
    pieChartImage = None
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        plazo = int(request.form['plazo'])
        interes = float(request.form['interes'])

        if form.validate():
            hipoteca.prestado = cantidad
            hipoteca.tae = interes
            hipoteca.plazoA = plazo
            cuota, interes, histogramImage, pieChartImage = hipoteca.calc()
            flash('Tu cuota mensual es de ' + str(cuota) + " €")
            porcent = "{0:.2f}".format((interes*100)/(cantidad+interes))
            flash('Al final habrás pagado un total de '
                  + str(int(interes)) + " € de intereses, un "
                  + porcent + " % del total")
        else:
            flash('All the form fields are required. ')

    return render_template('hipoteca.html', form=form, histogram=histogramImage, pieChart=pieChartImage)


@app.route("/")
def home():
        return render_template('home.html')


@app.route("/otra")
def otra():
    pieChartImage = None
    return render_template('otra.html', pieChart=pieChartImage)

@app.route('/ajax', methods = ['POST'])
def ajax_request():
    username = request.form['username']
    print(username)
    pieChartImage = hipoteca.pieChart(156000, int(username))
    histo = hipoteca.histogram([i for i in range(int(int(username)/1000))], 500)
    return jsonify(pie = '<div><img src="data:image/png;base64,'+pieChartImage+'" alt="pie"</div>',
                   histo = '<div><img src="data:image/png;base64,' + histo + '" alt="histo"</div>')

@app.route('/hipoAjax', methods = ['POST'])
def hipoAjax():
    cantidad = request.form['cantidadS']
    print(cantidad)
    hipoteca.prestado = int(cantidad)
    retorno = hipoteca.calc()
    histo = retorno[2]
    pieChartImage= retorno[3]
    return jsonify(pie='<div><img src="data:image/png;base64,' + pieChartImage + '" alt="pie"</div>',
                   histo='<div><img src="data:image/png;base64,' + histo + '" alt="histo"</div>')


if __name__ == "__main__":
    app.run()
