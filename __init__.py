from flask import Flask, render_template, request, redirect, url_for, Markup
import parse_pdf
import numpy as np
import pandas as pd
import json
import plotly
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import plotly.express as px
from app import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/upload', methods = ["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        file.save('uploaded/file.pdf')
        pdf_txt = parse_pdf.parser('uploaded/file.pdf')
        out_dict, word_f = runapp(pdf_txt)
        return render_template('content.html', filename=file.filename, out_dict=out_dict, plot_div=Markup(create_plot(word_f))) 

def create_plot(word_f):

    df = pd.DataFrame(dict(
        r=[word_f[key] for key in word_f],
        theta=[key for key in word_f]))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')

    return py.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)


if __name__=="__main__":
    app.run(debug=True)
