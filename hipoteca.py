from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from wtforms.fields.html5 import IntegerRangeField
 
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
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        plazo = int(request.form['plazo'])
        interes = float(request.form['interes'])
        # print(request.form['age'])
 
        if form.validate():
            # Save the comment here.
            cuota = str(calc(cantidad, interes, plazo))
            flash('Tu cuota mensual es de ' + cuota + " €")
        else:
            flash('All the form fields are required. ')
 
    return render_template('hipoteca.html', form=form)


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
        cuota += 0.5
        interesList = []
        for _ in range(plazo):
            # FIXME esto seguro que puede ser más eficiente
            interesM = restante * taeM
            interes += interesM
            interesList.append(interesM)
            restante -= (cuota - interesM)
    print(restante, interes, cuota)
    histogram(interesList, cuota)
    return int(cuota)

def histogram(interesList, cuota):
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
    plt.text(60, 60, "Azul = Interés\nNaranja = amortización\nCuota mensual = " + str(cuota) + " €")
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)
    plt.savefig('static/imagen.png')
    # plt.show()


@app.route("/")
def home():
        return render_template('home.html')


@app.route("/otra")
def otra():
        return """otra cosa"""


if __name__ == "__main__":
    app.run()
    histogram()
