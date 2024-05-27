import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 基础 URL
api_url = "https://mzt.111404.xyz/api/nsfwid/{}"

# 最大 ID 值
# 这里自己尝试最大值
max_id = 17923

# 存储 ID 和 title 的列表
data_list = []

def fetch_data(id):
    try:
        response = requests.get(api_url.format(id))
        response.raise_for_status()
        data = response.json()
        if data:
            for item in data:
                title = item['title']
                time = '-'.join(title.split('-')[-2:])  # 获取 title 的最后两个部分作为时间
                data_list.append({'ID': item['id'], 'Title': title, 'Time': time})
    except requests.RequestException as e:
        print(f"Error fetching data for ID {id}: {e}")

def main():

    #修改下一行的数字来修改线程数 100以内均可
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(fetch_data, id) for id in range(1, max_id + 1)]
        for future in tqdm(as_completed(futures), total=len(futures)):
            future.result()  # 等待所有任务完成

    # 将数据保存到 CSV 文件
    df = pd.DataFrame(data_list)
    df.to_csv('titles.csv', index=False)

if __name__ == "__main__":
    main()
