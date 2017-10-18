from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import IntegerRangeField
from io import BytesIO
import base64
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


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
            # Save the comment here.
            cuota, interes, histogramImage, pieChartImage = calc(cantidad, interes, plazo)
            flash('Tu cuota mensual es de ' + str(cuota) + " €")
            porcent = "{0:.2f}".format((interes*100)/(cantidad+interes))
            flash('Al final habrás pagado un total de intereses de '
                  + str(int(interes)) + " €, un "
                  + porcent + " % del total")
        else:
            flash('All the form fields are required. ')

    return render_template('hipoteca.html', form=form, histogram=histogramImage, pieChart=pieChartImage)


def calc(prestado, tae, plazoA):
    print(prestado, tae, plazoA)
    taeM = tae / 1200
    plazo = plazoA * 12
    restante = prestado
    interes = 0
    cuota = 0
    while restante > 0:
        restante = prestado
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
    return int(cuota), interes, histogram(interesList, cuota), pieChart(prestado, interes)


def pieChart(cantidad, intereses):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Intereses', 'Amortización'
    total = cantidad + intereses
    sizes = [intereses/total, cantidad/total]
    explode = (0.1, 0)  # only "explode" the 2nd slice
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ### Rendering Plot in Html
    plt.savefig('home/betados/mysite/pie.png')
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    return str(figdata_png)[2:-1]


def histogram(interesList, cuota):
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
    plt.text(len(interesList)/2, cuota/2,
             "Azul = Interés\nNaranja = Amortización\nCuota mensual = " + str(cuota) + " €",
             fontsize=14)
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)

    ### Rendering Plot in Html
    # En servidor:
    # plt.savefig('/home/betados/mysite/imagen.png')
    # en linux:
    plt.savefig('home/betados/mysite/histogram.png')
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    return str(figdata_png)[2:-1]


@app.route("/")
def home():
        return render_template('home.html')


@app.route("/otra")
def otra():
        return """otra cosa"""


if __name__ == "__main__":
    app.run()
    histogram()
