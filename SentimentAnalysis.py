from flask import Flask, render_template, request, jsonify, redirect
from flask_api import status
from flask_cors import CORS, cross_origin
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
from nltk.tokenize import sent_tokenize
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def get_hsl(val):
    value = float(val)
    H = int((value + 1) * 120/2 - 1)
    S = 70
    L = 35

    return "hsl(" + str(H) + ", " + str(S) + "%, " + str(L) + "%)"

@app.route('/', methods=['GET'])
def index():
    return redirect('developer')

@app.route('/developer', methods=['GET'])
def developer():
    return render_template("developer.html")

@app.route('/instructor', methods=['GET'])
def instructor():
    return render_template("instructor.html")

@app.route('/visualize_sentiment', methods=['GET', 'POST'])
@cross_origin()
def visualize_sentiment():
    if request.method == 'GET':
        review = request.args.get('review')
    elif request.method == 'POST':
        review = request.json['review']

    if review != '':
        sentences = sent_tokenize(review)

        overall_compound = 0.0;

        for sentence in sentences:

            sa = vaderSentiment(sentence)


            sentiment = round(float(sa['compound']),1)
            review = review.replace(sentence, '<font style="color:' + get_hsl(sa['compound']) + ';">' + sentence + '</font>')
            overall_compound += float(sa['compound'])



        return review, status.HTTP_200_OK

@app.route('/analyze_reviews_bulk', methods=['POST'])
@cross_origin()
def analyze_review_bulk():
    review = ''
    results = {}

    reviews = request.json['reviews']

    if len(reviews) > 0:

        overall_compounds = []

        for review in reviews:
            overall_compound = 0.0;
            overall_neg_compound = 0.0
            overall_neu_compound = 0.0
            overall_pos_compound = 0.0
            sentences = []

            if review['text'] != None and review['text'] != '':
                sentences = sent_tokenize(review['text'].encode('utf-8').strip())

                for sentence in sentences:
                    sa = vaderSentiment(sentence)
                    results[sentence] = sa
                    overall_compound += float(sa['compound'])
                    overall_neg_compound += float(sa['neg'])
                    overall_neu_compound += float(sa['neu'])
                    overall_pos_compound += float(sa['pos'])
            else:
                review['text'] == ' '

            c = {}
            c['id'] = review['id']
            c['text'] = review['text']
            c['sentiment'] = 0 if len(sentences) == 0 else format(overall_compound / len(sentences), '.2f')
            c['neg'] =  0 if len(sentences) == 0 else format(overall_neg_compound / len(sentences), '.2f')
            c['neu'] =  0 if len(sentences) == 0 else format(overall_neu_compound / len(sentences), '.2f')
            c['pos'] =  0 if len(sentences) == 0 else format(overall_pos_compound / len(sentences), '.2f')
            overall_compounds.append(c)

    return jsonify(sentiments=overall_compounds), status.HTTP_200_OK

@app.route('/analyze_review', methods=['GET', 'POST'])
@cross_origin()
def analyze_review():
    review = ''
    results = []

    if request.method == 'GET':
        review = request.args.get('review')
    elif request.method == 'POST':
        review = request.json['review']

    if review != '':

        sentences = sent_tokenize(review.encode('utf-8').strip())

        overall_compound = 0.0;

        for sentence in sentences:
            sa = vaderSentiment(sentence)
            sa['text'] = sentence
            results.append(sa)
            overall_compound += float(sa['compound'])

        return jsonify(overall_compound = (overall_compound/len(results)), sentiments = results), status.HTTP_200_OK

@app.route('/analyze_sentences', methods=['GET', 'POST'])
@cross_origin()
def analyze_sentences():
    review = ''
    results = {}
    sentences = []
    if request.method == 'GET':
        sentences = request.args.getlist('sentences')
    elif request.method == 'POST':
        sentences = request.json['sentences']

    if len(sentences) > 0:
        overall_compound = 0.0;

        for sentence in sentences:
            sa = vaderSentiment(sentence)
            results[sentence] = sa
            overall_compound += float(sa['compound'])

        return jsonify(overall_compound = overall_compound, sentiments=results), status.HTTP_200_OK

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3008, threaded=True)
