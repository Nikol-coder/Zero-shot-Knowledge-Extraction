# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import numpy
import random

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="换为您自己的API", base_url="https://api.deepseek.com")
numpy.random.seed(42)

#组织机构3
example1={
"id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。\",\"schema\":[{\"entity_type\": \"公司\", \"attributes\": {\"地址\": \"某个实体（如公司、机构）的所在地或主要办公地点。\", \"成立时间\": \"一个组织或公司的创立日期。\", \"注册资金\": \"企业注册时所需的最低资金，反映其初始资本规模。\"}}],\"input\": \"莎车县隆基水泥有限责任公司成立于2001年，位于阿斯兰巴格重工业园，注册资金1900万元人民币，总投资2200多万元，年设计生产能力15万吨。公司现有员工138人。\"}",
    "output": "{\"公司\": {\"莎车县隆基水泥有限责任公司\": {\"地址\": \"阿斯兰巴格重工业园\", \"成立时间\": \"2001年\", \"注册资金\": \"1900万元人民币\"}}}"
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
with open('./组织机构3.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个新的json文件
with open('./deepseek_danci_组织机构3.json', 'w', encoding='utf-8') as new_file:
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