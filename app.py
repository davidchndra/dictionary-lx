from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests
from datetime import datetime


app = Flask(__name__)
client = MongoClient('mongodb+srv://iloveyou3000:1l0v3you@cluster0.adux7fs.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta_plus_week2

#biasanya dipanggil dengan nama index / default
@app.route('/')  
def main():
    words_result = db.words.find({},{'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
        msg = request.args.get('msg')
    return render_template("index.html",
                           words=words,
                           msg=msg)


@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = '92bcb633-0433-4166-9ea0-2ad471e9453b'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response = requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'main',
            msg=f'Could not find {keyword}'
        ))
    if type(definitions[0]) is str:
        return redirect(url_for(
            'main',
            msg=f'Could not find {keyword}, did you mean {",".join(definitions)}?'
        ))
    return render_template("detail.html", 
                           word=keyword,
                           definitions=definitions,
                           status=request.args.get('status_give','new'))


@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d'),
    }

    db.words.insert_one(doc)

    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was deleted',
    })

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)