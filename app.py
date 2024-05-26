from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import requests

app = Flask(__name__)

# Load the CSV file
titles = pd.read_csv('titles.csv')

# Constants
BASE_API_URL = "https://mzt.111404.xyz/api/nsfwid/"
IMAGE_BASE_URL = "https://i2.wp.com/tgproxy2.1258012.xyz"


@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    per_page = 100
    start = (page - 1) * per_page
    end = start + per_page
    paginated_titles = titles[start:end]
    total_pages = (len(titles) + per_page - 1) // per_page
    pages = range(1, total_pages + 1)

    return render_template('index.html', titles=paginated_titles, page=page, pages=pages, total_pages=total_pages)


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = titles[titles['Title'].str.contains(query, case=False, na=False)]
    return render_template('results.html', query=query, results=results.to_dict(orient='records'))


@app.route('/images/<int:id>')
def show_images(id):
    response = requests.get(BASE_API_URL + str(id))
    if response.status_code == 200:
        data = response.json()
        title = data[0]['title']
        images = [IMAGE_BASE_URL + url for url in data[0]['urls']]
        return render_template('images.html', title=title, images=images)
    else:
        return "Error: Could not retrieve images", 500


if __name__ == '__main__':
    app.run(debug=True)
