import pandas as pd

# 读取现有的 CSV 文件
df = pd.read_csv('titles.csv')

# 定义一个函数来提取时间信息
def extract_time(title):
    parts = title.split('-')
    if len(parts) >= 3:
        return parts[-2] + '-' + parts[-1]  # 假设时间信息在标题的最后两个部分
    return None

# 创建新的列 'Time' 并提取时间信息
df['Time'] = df['Title'].apply(extract_time)

# 保存新的 CSV 文件
df.to_csv('titles_with_time.csv', index=False)

print("New CSV file 'titles_with_time.csv' created successfully.")
