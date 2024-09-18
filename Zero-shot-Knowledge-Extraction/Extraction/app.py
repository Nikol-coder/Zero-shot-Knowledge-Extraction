import time
from flask import Flask, render_template, request, jsonify
import json
from openai import OpenAI
import numpy

app = Flask(__name__)

# OpenAI 配置
client = OpenAI(api_key="sk-ea4907f2d1ac4b79856d825f0ca9cc3d", base_url="https://api.deepseek.com")
numpy.random.seed(42)

# 示例数据
example1 = {
    "id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性值有多个以列表形式返回，并输出为可解析的json格式。\",\"schema\": [{\"entity_type\": \"运动员\", \"attributes\": {\"运动项目\": \"体育运动中的特定活动或比赛。\", \"主要奖项\": \"因卓越表现而获得的荣誉性奖项。\",  \"出生地\": \"人物出生的具体地点。\"}}],\"input\": \"全红婵，2007年3月28日出生于广东省湛江市，中国国家跳水队女运动员，主项为女子10米跳台。全红婵夺得2020全国跳水冠军赛暨东京奥运会、世界杯选拔赛女子单人10米跳台冠军。2021年3月，全红婵获2021年中国跳水明星赛女子单人、双人十米跳台亚军；5月，全红婵以440.85分蝉联2021年全国跳水冠军赛暨东京奥运会选拔赛、全运会跳水资格赛女子单人十米跳台冠军；8月，全红婵以五跳三跳满分总466.2分创女子10米跳台历史最高分纪录夺得2020东京奥运会跳水女子单人10米跳台金牌。\"}",
    "output": "{\"运动员\": {\"全红婵\": {\"运动项目\": \"跳水\", \"主要奖项\": [\"2020全国跳水冠军\", \"2020年世界杯选拔赛女子单人10米跳台冠军\", \"2021年中国跳水明星赛女子单人十米跳台亚军\", \"2021年中国跳水明星赛女子双人十米跳台亚军\", \"女子10米跳台历史最高分纪录\", \"2020东京奥运会跳水女子单人10米跳台金牌\"],  \"出生地\": \"广东省湛江市\"}}}"
}

example2 = {
    "id": 3,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性值有多个以列表形式返回，并输出为可解析的json格式。\",\"schema\":[{\"entity_type\": \"汽车\", \"attributes\": {\"所属品牌\": \"汽车所属的品牌或制造商。\", \"车型\": \"具体的汽车型号。\",\"年款\": \"汽车的生产年份或款式，表示其设计和制造的时期。\", \"推出年款\": \"汽车首次上市的年份。\"}}],\"input\": \"途观2015款，是大众旗下SUV，2015年上市，燃油经济性出色，90km/h的等速油耗仅为6.5升。\"}",
    "output": "{\"汽车\": {\"途观2015款\": {\"所属品牌\": \"大众\", \"车型\": \"途观2015款\", \"年款\": \"2015\", \"推出年款\": \"2015\"}}}"
}

# 从示例中获取"instruction"、"schema"和"input"的值
ex_instruction1 = example1['instruction']
instruction_dict = json.loads(ex_instruction1)
instruction = instruction_dict['instruction']
ex_output1 = example1['output']

ex_instruction2 = example2['instruction']
ex_output2 = example2['output']

# 将这些值转换为一个可以发送给OpenAI的消息
ex_message1 = "第一个示例为: " + ex_instruction1 + ", output:" + ex_output1
ex_message2 = "第二个示例为: " + ex_instruction2 + ", output:" + ex_output2
ex_message = ex_message1 + "\n" + ex_message2

def extract_knowledge(input_text):
    # 读取json文件
    with open('demo.json', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 创建一个新的json文件
    with open('deepseek_rag.json', 'w', encoding='utf-8') as new_file:
        # 遍历每一行
        for line in lines:
            # 解析JSON字符串
            data = json.loads(line)

            # 获取"instruction"字段的值
            line = data['instruction']
            line = json.loads(line)
            
            #看是否是csv文件自动化处理
            # line['input']=input_text
            
            line['instruction'] = instruction
            last_output = data['output']
            label = list((json.loads(data['label']).values()))[0]

            label = json.dumps(label, ensure_ascii=False)
            print("last_output:", last_output)
            print("label:", label)

            input_data = json.dumps(line, ensure_ascii=False)

            # 将"instruction"字段的值转换为一个可以发送给OpenAI的消息
            message = '[INST] ' + input_data + '[/INST]'

            try:
                # 使用OpenAI生成新的"output"
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "你是一个信息抽取专家与知识图谱专家。请根据要求及所提供的参考信息判断抽取结果是否正确，如果不正确，请重新抽取并补充完整。所有输出必须来自于输入input，当参考信息并不来源于输入信息时，舍弃掉参考信息，只注重输入信息。" + ex_message},
                        {"role": "user", "content": "上次抽取结果为:" + last_output + "参考信息为:" + label + '本次为：' + message},
                    ],
                    seed=2024,
                    top_p=0.7,
                    temperature=0.7,
                    stream=False
                )
            except:
                print(f"Skipped due to error: {data['id']}")
                continue

            # 获取生成的"output"
            first_output = response.choices[0].message.content
            # 去除 `json 和 `
            first_output = first_output.replace('```json', '').replace('```', '').replace("\n", "").replace("  ", "")
            print(first_output)

            try:
                # 使用OpenAI生成新的"output"
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system",
                         "content": "你是一个信息抽取专家与知识图谱专家。请根据要求及所提供的参考信息判断抽取结果是否正确，如果不正确，请重新抽取并补充完整。请注意所有输出必须来自于输入且只以json格式输出结果；当参考信息并不来源于输入信息时，请以输入信息为准。示例为：" + ex_message1},
                        {"role": "user", "content": "上次抽取结果为:" + first_output + '本次为：' + message + '。请根据要求及所提供的参考信息判断抽取结果是否正确，如果不正确，请重新抽取并补充完整。请注意所有输出必须来自于输入且只以json格式输出结果；当参考信息并不来源于输入信息时，请只以输入信息为准。'},
                    ],
                    seed=2024,
                    top_p=0.7,
                    temperature=0.7,
                    stream=False
                )
            except:
                print(f"Skipped due to error: {data['id']}")
                continue

            # 获取生成的"output"
            new_output = response.choices[0].message.content
            # 去除 `json 和 `
            new_output = new_output.replace('```json', '').replace('```', '').replace("\n", "").replace("  ", "")
            print(new_output)
            print('-----' * 5)

            # 将新的"output"添加到数据中
            data['output'] = new_output

            # 将数据写入新的json文件
            new_file.write(json.dumps(data, ensure_ascii=False) + '\n')

            return new_output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_route():
    input_text = request.form['input_text']
    if input_text:
        result = extract_knowledge(input_text)
        return jsonify({"status": "success", "data": json.loads(result)})
    else:
        return jsonify({"status": "error", "message": "请输入文本"})

if __name__ == '__main__':
    app.run(debug=True)