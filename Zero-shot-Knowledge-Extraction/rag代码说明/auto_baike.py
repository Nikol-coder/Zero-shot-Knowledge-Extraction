import json
import os
from auto_search_baidu import search
import time
from auto import autosearch
# 读取JSON文件
with open('best.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 初始化分类字典
classified_data = []

# 打开文件准备写入
with open('baike_data_demo.json', 'w', encoding='utf-8') as output_file:
    # 遍历每一行数据
    for line in lines:
        data = json.loads(line)
        instruction = json.loads(data['instruction'])
        entity_type = instruction['schema'][0]['entity_type']
        attributes = instruction['schema'][0]['attributes']
        input = instruction['input']
        print("input:",input)
        # exit()
        output = json.loads(data['output'])
        
        # 提取output中的实体和属性
        entities = output.get(entity_type.strip(), {})
        if entities:
            entity_name = list(entities.keys())[0]
            href = autosearch(input)
            print("hred:",href)
            label = search(entity_type, entity_name, href)
            print(label)
            data['label'] = label
            classified_data.append(data)
            # 立即写入文件
            output_file.write(json.dumps(data, ensure_ascii=False) + '\n')
        else:
            print(f"No entities found for entity type: {entity_type.strip()}")
        
        # 等待5秒钟
        time.sleep(5)