# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import numpy
import random

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="换为您自己的API", base_url="https://api.deepseek.com")
numpy.random.seed(42)

#人物0
example1={
"id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。\",\"schema\": [{\"entity_type\": \"运动员\", \"attributes\": {\"运动项目\": \"体育运动中的特定活动或比赛。\", \"主要奖项\": \"因卓越表现而获得的荣誉性奖项。\",  \"出生地\": \"人物出生的具体地点。\"}}],\"input\": \"全红婵，2007年3月28日出生于广东省湛江市，中国国家跳水队女运动员，主项为女子10米跳台。全红婵夺得2020全国跳水冠军赛暨东京奥运会、世界杯选拔赛女子单人10米跳台冠军。2021年3月，全红婵获2021年中国跳水明星赛女子单人、双人十米跳台亚军；5月，全红婵以440.85分蝉联2021年全国跳水冠军赛暨东京奥运会选拔赛、全运会跳水资格赛女子单人十米跳台冠军；8月，全红婵以五跳三跳满分总466.2分创女子10米跳台历史最高分纪录夺得2020东京奥运会跳水女子单人10米跳台金牌。\"}",
"output": "{\"运动员\": {\"全红婵\": {\"运动项目\": \"跳水\", \"主要奖项\": [\"2020全国跳水冠军\", \"2020年世界杯选拔赛女子单人10米跳台冠军\", \"2021年中国跳水明星赛女子单人十米跳台亚军\", \"2021年中国跳水明星赛女子双人十米跳台亚军\", \"女子10米跳台历史最高分纪录\", \"2020东京奥运会跳水女子单人10米跳台金牌\"],  \"出生地\": \"广东省湛江市\"}}}"
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
with open('./人物0.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个新的json文件
with open('./deepseek_danci_人物0.json', 'w', encoding='utf-8') as new_file:
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
                    {"role": "user", "content": "上次抽取结果为:" + last_output + "参考信息为:" + label + '本次任务为：' + message},
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