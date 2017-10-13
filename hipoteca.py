from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
 
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class ReusableForm(Form):
    cantidad = TextField('Cantidad:', validators=[validators.required()])
    plazo = TextField('Plazo:', validators=[validators.required()])
    interes = TextField('Interés (TAE):', validators=[validators.required()])

 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
 
    print(form.errors)
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        plazo = int(request.form['plazo'])
        interes = float(request.form['interes'])
        print(cantidad)
 
        if form.validate():
            # Save the comment here.
            cuota = str(calc(cantidad, interes, plazo))
            flash('Tu cuota mensual es: ' + cuota)
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
        cuota += 0.1
        for _ in range(plazo):
            interesM = restante * taeM
            interes += interesM
            restante -= (cuota - interesM)
    print(restante, interes, cuota)
    return cuota
 
if __name__ == "__main__":
    app.run()
