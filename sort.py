import pandas as pd

def sort_csv_by_id(file_path):
    # 读取 CSV 文件
    df = pd.read_csv(file_path)

    # 按 ID 列从大到小排序
    df_sorted = df.sort_values(by='ID', ascending=False)

    # 将排序后的数据覆盖保存到原始 CSV 文件
    df_sorted.to_csv(file_path, index=False)

if __name__ == "__main__":
    file_path = 'titles.csv'  # 替换为你的文件名
    sort_csv_by_id(file_path)
    print(f"CSV file {file_path} has been sorted by ID in descending order.")
