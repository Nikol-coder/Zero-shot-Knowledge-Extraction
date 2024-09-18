# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import numpy
import random

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="换为您自己的API", base_url="https://api.deepseek.com")
numpy.random.seed(42)

#地点1
example1={
"id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。\",\"schema\": [{\"entity_type\": \"街道\", \"attributes\": {\"所属地区\": \"行政区域隶属于的更高一级的地理区域或行政单位。\", \"政府驻地\": \"地方政府机构所在地。\", \"行政区类别\": \"行政区域的级别，如县、市、区等。\", \"地理位置\": \"一个地方在地球表面的具体位置描述。\", \"下辖地区\": \"行政单位下属的社区、城镇或村庄等。\", \"人口\": \"一个地区或行政单位的总人口数。\", \"面积\": \"地理区域的总面积。\"}}],\"input\": \"垦利街道，山东省东营市垦利区下辖街道，是垦利区人民政府驻地，地处垦利区中部，东与兴隆街道、永安镇相邻，南与东营区胜利街道、文汇街道接壤，西与胜坨镇相连，北与利津县陈庄镇隔黄河相望，东北与黄河口镇相接，辖区总面积202平方千米。  民国十七年（1928年），薛氏移民来此垦荒建立民丰村；2009年8月，西宋乡并入垦利镇，并改垦利街道。截至2011年末，垦利街道总人口70065人。 截至2020年6月，垦利街道下辖12个社区、82个行政村，另辖1个村级单位。  2011年，垦利街道财政收入1.04亿元，比上年增长21.75%。农民人均纯收入10595元。\"}",
    "output": "{\"街道\": {\"垦利街道\": {\"所属地区\": \"山东省东营市垦利区\",  \"政府驻地\": \"垦利街道\",  \"行政区类别\": \"街道\",  \"地理位置\": \"地处垦利区中部，东与兴隆街道、永安镇相邻，南与东营区胜利街道、文汇街道接壤，西与胜坨镇相连，北与利津县陈庄镇隔黄河相望，东北与黄河口镇相接\",  \"下辖地区\": [\"12个社区\", \"82个行政村\", \"1个村级单位\"],  \"人口\": \"70065\",  \"面积\": \"202平方千米\"}}}"
}

#反例
example2={
"id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。\",\"schema\":[{\"entity_type\": \"小说\", \"attributes\": {\"作者\": \"创作小说的作者姓名。\", \"小说类型\": \"小说的类别，如言情、科幻、悬疑等。\", \"连载网站\": \"网络小说在哪个网站进行连载更新。\"}}],\"input\": \"《施太太，我没你不行》是一部连载于云中书城的小说，作者袖水。\"}",
    "output": "{\"小说\": {\"施太太，我没你不行\": {\"作者\": [\"袖水\"],  \"连载网站\": [\"云中书城\"]}}}"
}


# 从示例中获取"instruction"、"schema"和"input"的值
id1=example1["id"]
ex_instruction1 = example1['instruction']
instruction_dict=json.loads(ex_instruction1)
instruction=instruction_dict['instruction']
# print(instruction)
# print(type(instruction))
# print(ex_instruction1)
# print(type(ex_instruction1))
ex_output1 = example1['output']
# print(ex_output1)
# print(type(ex_output1))

id2=example2["id"]
ex_instruction2 = example2['instruction']
ex_output2 = example2['output']

# 将这些值转换为一个可以发送给OpenAI的消息
ex_message1 =  "第一个示例为: "+ex_instruction1 +", output:"+ ex_output1
# print(ex_message1)
ex_message2 =  "第二个示例为: "+ex_instruction2 +", output:"+ ex_output2
# print(ex_message2)
ex_message=ex_message1+"\n"+ex_message2
# print(ex_message)
# exit()


# 读取json文件
with open('./地点1.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个新的json文件
with open('./deepseek_danci_地点1.json', 'w', encoding='utf-8') as new_file:
    # 遍历每一行
    for line in lines:
    # 解析JSON字符串
        data = json.loads(line)

        # 获取"instruction"字段的值
        line = data['instruction']
        line=json.loads(line)

        line['instruction']=instruction
        last_output = data['output']
        label = list((json.loads(data['label']).values()))[0]
        
        # try:
        #     for k,v in label.items():
        #         v_key = list(v.keys())
        #         for item in v_key:
        #             if item not in ref_list:
        #                 v.pop(item)
        # except:
        #     pass

        # print(label)

        label = json.dumps(label, ensure_ascii=False)
        # print("last_output:",last_output)
        # print("label:",label)

        input=json.dumps(line,ensure_ascii=False)


        # 将"instruction"字段的值转换为一个可以发送给OpenAI的消息
        message = '[INST] ' + input + '[/INST]'

        try:
            # 使用OpenAI生成新的"output"
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system",
                    "content": "你是一个信息抽取专家与知识图谱专家。请根据要求及所提供的参考信息判断抽取结果是否正确，如果不正确，请重新抽取并补充完整，输出json形式的结果。所有输出必须来自于输入input，当参考信息并不来源于输入信息时，舍弃掉参考信息，只注重输入信息。" + ex_message},
                     {"role": "user", "content": "上次抽取结果为:" + last_output + "参考信息为:" + label + '本次为：' + message},
                ],
                seed=2024,
                top_p=0.7,
                temperature=0.7,
                stream=False
            )
        except :
            print(f"Skipped due to error: {data['id']}")
            continue
        
        # print(response.model_dump_json())
        # 获取生成的"output"
        first_output = response.choices[0].message.content
        # 去除 `json 和 `
        first_output = first_output.replace('```json', '').replace('```', '').replace("\n","").replace("  ","")
        print(first_output)
        # exit()

        # exit()
        # 将新的"output"添加到数据中
        data['output'] = first_output

        # 将数据写入新的json文件
        new_file.write(json.dumps(data, ensure_ascii=False) + '\n')

        # Skipped due to error: 334