from flask import Flask, render_template, request, url_for, jsonify, redirect
import pandas as pd
import requests
import random
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

app = Flask(__name__)

# Constants
BASE_API_URL = "https://mzt.111404.xyz/api/nsfwid/"
IMAGE_SERVERS = [
    "https://i0.wp.com/tgproxy2.1258012.xyz",
    "https://i1.wp.com/tgproxy2.1258012.xyz",
    "https://i2.wp.com/tgproxy2.1258012.xyz",
    "https://i3.wp.com/tgproxy2.1258012.xyz"
]

# Load the CSV file
titles = pd.read_csv('titles.csv')

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

    # 获取当天更新的内容
    today = datetime.datetime.now().strftime("%m-%d")
    daily_updates = titles[titles['Time'] == today]

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

    return render_template('index.html', titles=paginated_titles, page=page, pages=pages, total_pages=total_pages, daily_updates=daily_updates)

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

@app.route('/update', methods=['POST'])
def update():
    # 手动更新数据
    def fetch_data(id):
        try:
            response = requests.get(BASE_API_URL + str(id))
            response.raise_for_status()
            data = response.json()
            if data:
                for item in data:
                    title = item['title']
                    time = title.split('-')[-2:]  # 假设时间信息在标题的最后两个部分
                    time = '-'.join(time)
                    data_list.append({'ID': item['id'], 'Title': title, 'Time': time})
            return bool(data)
        except requests.RequestException as e:
            print(f"Error fetching data for ID {id}: {e}")
            return False

    data_list = []
    id = 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        while True:
            future = executor.submit(fetch_data, id)
            futures.append(future)
            id += 1
            if not future.result():  # 如果没有数据，则停止
                break
        for future in as_completed(futures):
            future.result()  # 等待所有任务完成

    # 将数据保存到 CSV 文件
    df = pd.DataFrame(data_list)
    df.to_csv('titles.csv', index=False)

    global titles
    titles = pd.read_csv('titles.csv')  # 重新加载更新后的数据

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
