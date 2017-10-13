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
    interes = TextField('Interés:', validators=[validators.required()])
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
 
    print(form.errors)
    if request.method == 'POST':
        cantidad=request.form['cantidad']
        print(cantidad)
 
        if form.validate():
            # Save the comment here.
            flash('Hello ' + cantidad)
        else:
            flash('All the form fields are required. ')
 
    return render_template('hipoteca.html', form=form)
 
if __name__ == "__main__":
    app.run()
