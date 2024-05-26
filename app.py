from flask import Flask, render_template, request, url_for, jsonify
import pandas as pd
import requests
import random

app = Flask(__name__)

# Load the CSV file
titles = pd.read_csv('titles.csv')

# Constants
BASE_API_URL = "https://mzt.111404.xyz/api/nsfwid/"
IMAGE_SERVERS = [
    "https://i0.wp.com/tgproxy2.1258012.xyz",
    "https://i1.wp.com/tgproxy2.1258012.xyz",
    "https://i2.wp.com/tgproxy2.1258012.xyz",
    "https://i3.wp.com/tgproxy2.1258012.xyz"
]

def get_preview_image(id):
    response = requests.get(BASE_API_URL + str(id))
    if response.status_code == 200:
        data = response.json()
        if data and 'urls' in data[0] and data[0]['urls']:
            return f"{random.choice(IMAGE_SERVERS)}{data[0]['urls'][0]}"
    return None

@app.route('/')
@app.route('/<int:page>')
def index(page=1):
    per_page = 100
    start = (page - 1) * per_page
    end = start + per_page
    paginated_titles = titles[start:end]
    total_pages = (len(titles) + per_page - 1) // per_page

    # Pagination logic
    pages = []
    if total_pages <= 5:
        pages = range(1, total_pages + 1)
    else:
        if page <= 3:
            pages = range(1, 6)
        elif page > total_pages - 3:
            pages = range(total_pages - 4, total_pages + 1)
        else:
            pages = range(page - 2, page + 3)

    if 1 not in pages:
        pages = [1] + list(pages)
    if total_pages not in pages:
        pages = list(pages) + [total_pages]

    return render_template('index.html', titles=paginated_titles, page=page, pages=pages, total_pages=total_pages)

@app.route('/preview/<int:id>')
def preview(id):
    image_url = get_preview_image(id)
    return jsonify({'image_url': image_url})

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
        images = [f"{random.choice(IMAGE_SERVERS)}{url}" for url in data[0]['urls']]
        return render_template('images.html', title=title, images=images)
    else:
        return "Error: Could not retrieve images", 500

if __name__ == '__main__':
    app.run(debug=True)
