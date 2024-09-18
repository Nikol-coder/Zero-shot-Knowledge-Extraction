import json

# 读取 oneke_danci_产品4.json 文件
with open('oneke_danci_人物0.json', 'r', encoding='utf-8') as f:
    data_人物0 = [json.loads(line) for line in f]
with open('oneke_danci_地点1.json', 'r', encoding='utf-8') as f:
    data_地点1 = [json.loads(line) for line in f]
with open('oneke_danci_自然科学2.json', 'r', encoding='utf-8') as f:
    data_自然科学2 = [json.loads(line) for line in f]
with open('oneke_danci_组织机构3.json', 'r', encoding='utf-8') as f:
    data_组织机构3 = [json.loads(line) for line in f]
with open('oneke_danci_产品4.json', 'r', encoding='utf-8') as f:
    data_产品4 = [json.loads(line) for line in f]
# 读取 oneke_danci_生物5.json 文件
with open('oneke_danci_生物5.json', 'r', encoding='utf-8') as f:
    data_生物5 = [json.loads(line) for line in f]
with open('oneke_danci_语言6.json', 'r', encoding='utf-8') as f:
    data_语言6 = [json.loads(line) for line in f]
with open('oneke_danci_食物7.json', 'r', encoding='utf-8') as f:
    data_食物7 = [json.loads(line) for line in f]
with open('oneke_danci_其他8.json', 'r', encoding='utf-8') as f:
    data_其他8 = [json.loads(line) for line in f]
    
# 合并数据
merged_data = data_地点1 + data_人物0 + data_产品4 + data_其他8 + data_组织机构3 + data_生物5 + data_自然科学2 + data_语言6 + data_食物7

# 按照 id 排序
sorted_data = sorted(merged_data, key=lambda x: x['id'])

# 将合并并排序后的数据写入新的 JSON 文件
with open('merged_oneke_data.json', 'w', encoding='utf-8') as f:
    for item in sorted_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print("合并并排序完成，结果已写入 merged_oneke_data.json 文件")