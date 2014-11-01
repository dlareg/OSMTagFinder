# -*- coding: utf-8 -*-
'''
Created on 17.10.2014

@author: Simon Gwerder
'''
import os
from flask import Flask, session, send_from_directory, render_template, request, redirect, jsonify, Response
from flask_bootstrap import Bootstrap
import json

from utilities.configloader import ConfigLoader
from utilities import utils
from thesaurus.rdfgraph import RDFGraph
from website.tagresults import TagResults
from website.graphsearch import GraphSearch


rdfGraph = RDFGraph(utils.dataDir() + 'osm_tag_thesaurus_141030.rdf')

app = Flask(__name__)
app.config['SECRET_KEY'] = '#T0P#SECRET#'
Bootstrap(app)

def getLocale():
    if 'language' in session:
        return session['language']
    lang = request.accept_languages.best_match(['en', 'de'])
    if lang is None or lang == '':
        lang = 'en'
    setLocale(lang)
    return lang

def setLocale(lang=None):
    if lang is None or lang == '':
        session['language'] = 'en'
    else:
        session['language'] = lang

def searchCall(query):
    graphSearch = GraphSearch()
    if query is None or query == '':
        return None

    if getLocale() == 'de':
        translateDEToEN=True
    else:
        translateDEToEN=False
    rawResults = graphSearch.extendedSearch(query, translateDEToEN=False) # TODO e.g. "sport" scenario

    return TagResults(rdfGraph, rawResults)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(utils.staticDir(), '/ico/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods = ['GET'])
@app.route('/index', methods = ['GET'])
def index():
    return render_template('search.html', lang=getLocale())

@app.route('/lang', methods = ['POST'])
def changeLanguage():
    setLocale(request.form["lang"])
    return '200'

@app.errorhandler(405)
def methodNotAllowed(e):
    return render_template('404.html', lang=getLocale()), 404

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', lang=getLocale()), 404

@app.route('/search', methods = ['GET'])
def search():
    q = request.args.get('q', '')
    searchResults = searchCall(q)
    if searchResults is None:
        return redirect('/')
    return render_template('search.html', lang=getLocale(), q=q, results=searchResults.getResults())

@app.route('/api/search', methods = ['GET'])
def apiSearch():
    searchResults = searchCall(request.args.get('q', ''))
    if searchResults is None:
        return jsonify([])
    #return jsonify(results=searchResults.getResults())
    return Response(json.dumps(searchResults.getResults()),  mimetype='application/json')

if __name__ == '__main__':
    cl = ConfigLoader()
    tagFinderHost = cl.getWebsiteString('HOST')
    tagFinderPort = int(os.environ.get("PORT", cl.getWebsiteInt('PORT')))
    app.run(debug=True, host=tagFinderHost, port=tagFinderPort, threaded=True) # TODO debug=False, # Alternately app.run(..., processes=3)



