# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import numpy
import random

# for backward compatibility, you can still use `https://api.deepseek.com/v1` as `base_url`.
client = OpenAI(api_key="换为您自己的API", base_url="https://api.deepseek.com")
numpy.random.seed(42)

#其他8
example1 = {
    "id": 0,
    "instruction": json.dumps({
        "instruction": "你是一个图谱实体知识结构化专家。根据输入实体类型(entity type)的schema描述，从文本中抽取出相应的实体实例和其属性信息，不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。",
        "schema": [
            {
                "entity_type": "运动员",
                "attributes": {
                    "运动项目": "体育运动中的特定活动或比赛。",
                    "主要奖项": "因卓越表现而获得的荣誉性奖项。",
                    "毕业院校": "人物所毕业的学校。",
                    "出生地": "人物出生的具体地点。"
                }
            }
        ],
        "input": "叶乔波，女，1964年6月3日出生于吉林省长春市 。中国女子速滑运动员。北京冬奥组委运动员委员会委员 。 10岁进入长春市业余体校速滑班，12岁入选八一速滑队。1991年首次夺得500米短道速滑世界冠军；1992年获第十六届冬奥会两枚银牌 ，为中国冬季项目实现冬奥会上奖牌零的突破。同年在挪威举行的世界短距离速滑锦标赛上，获女子1000米速滑冠军，并夺得女子全能世界冠军，成为中国和亚洲第一个短距离速滑全能世界冠军；至1993年春季赛事结束，她共获得14个世界冠军，其中包括全部女子500米速滑金牌，创造了世界冰坛的“大满贯”战绩；1994年带伤夺得第17届冬奥会女子1000米速滑铜牌 ；冬奥会后因伤退役。1994年结束运动员生涯。 2000年清华大学经管学院毕业，少将（2006年晋升）。 2021年12月，由叶乔波等55位世界冠军共同唱响《我们北京见》MV发布。"
    }, ensure_ascii=False),
    "output": {
        "运动员": {
            "叶乔波": {
                "运动项目": "速滑",
                "主要奖项": ["500米短道速滑世界冠军", "第十六届冬奥会两枚银牌", "女子1000米速滑冠军", "女子全能世界冠军", "全部女子500米速滑金牌", "第17届冬奥会女子1000米速滑铜牌"],
                "毕业院校": "清华大学经管学院",
                "出生地": "吉林省长春市"
            }
        }
    }
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
ex_output1 = json.dumps(example1['output'], ensure_ascii=False)  # 转换为 JSON 字符串
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
with open('./其他8.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个新的json文件
with open('./deepseek_danci_其他8.json', 'w', encoding='utf-8') as new_file:
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