# -*- coding: utf-8 -*-
from openai import OpenAI
import json
import numpy
import random
import torch
import itertools
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    BitsAndBytesConfig
)

#生物5
example1={
"id": 1,
    "instruction": "{\"instruction\":\"你是一个图谱实体信息抽取与知识结构化专家。请根据输入的schema描述，从输入（input）文本中抽取出entity type对应的实体和其属性信息（attributes）。其中，schema中的entity type表示实体类型，attributes表示实体的属性。输出的格式要求为：不存在的属性不输出, 属性存在多值就返回列表，并输出为可解析的json格式。\",\"schema\":[{\"entity_type\": \"植物\", \"attributes\": {\"科\": \"植物分类中的科，指一类植物的科学分类群。\", \"拉丁学名\": \"生物的科学命名，遵循林奈双名法，由属名和种加词组成。\", \"目\": \"生物分类中的目，比纲小，比科大的分类级别。\", \"属\": \"生物分类中的属，位于科之下，种之上。\", \"分布区域\": \"物种自然存在的地理区域或分布范围。\"}}],\"input\": \"白鳞莎草（Cyperus nipponicus Franch. & Sav.）是禾本目、莎草科、莎草属一年生草本，一年生草本，具许多细长的须根。秆密丛生，细弱，高5-20厘米，扁三棱形，平滑，基部具少数叶。叶通常短于秆,或有时与秆等长，宽1.5-2毫米，平时或有时折合；叶鞘膜质，淡棕红色或紫褐色。苞片3-5枚；小穗无柄，背面沿中脉处绿色，两侧白色透明，有时具疏的锈色短条纹，具多数脉；雄蕊2，小竖果长圆形，平凸状或有时近于凹凸状，长约鳞片的1/2，黄棕色。花果期8-9月。 生长在空旷的地方。产于中国江苏、河北、山西等省。国外分布于朝鲜、日本。\"}",
    "output": "{\"植物\": {\"白鳞莎草\": {\"科\": [\"莎草科\"],  \"拉丁学名\": [\"Cyperus nipponicus Franch. & Sav.\"],  \"目\": [\"禾本目\"],  \"属\": [\"莎草属\"],  \"分布区域\": [\"中国江苏\", \"河北\", \"山西等省\", \"朝鲜\", \"日本\"]}}}"
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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = '../../models/OneKE'
config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    config=config,
    device_map="auto",  
    torch_dtype=torch.float,
    trust_remote_code=True,
)

model.eval()

# 读取json文件
with open('./生物5.json', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建一个新的json文件
with open('./oneke_danci_生物5.json', 'w', encoding='utf-8') as new_file:
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
            system_sintruct = "你是一个信息抽取专家与知识图谱专家。请根据要求及所提供的参考信息判断抽取结果是否正确，如果不正确，请重新抽取并补充完整，输出json形式的结果。所有输出必须来自于输入input，当参考信息并不来源于输入信息时，舍弃掉参考信息，只注重输入信息。" + ex_message
            prompt = "上次抽取结果为:" + last_output + "参考信息为:" + label + '本次任务为：' + message
            sintruct = system_sintruct + prompt
            input_ids = tokenizer.encode(sintruct, return_tensors="pt").to(device)
            input_length = input_ids.size(1)
            generation_output = model.generate(input_ids=input_ids, generation_config=GenerationConfig(max_length=1024, max_new_tokens=512, return_dict_in_generate=True), pad_token_id=tokenizer.eos_token_id)
            generation_output = generation_output.sequences[0]
            generation_output = generation_output[input_length:]
            output = tokenizer.decode(generation_output, skip_special_tokens=True)          
        except :
            print(f"Skipped due to error: {data['id']}")
            continue
        
        # print(response.model_dump_json())
        # 获取生成的"output"
        first_output = output
        # 去除 `json 和 `
        first_output = first_output.replace('```json', '').replace('```', '').replace("\n","").replace("  ","")
        print(first_output)
        # exit()

        # exit()
        # 将新的"output"添加到数据中
        data['output'] = first_output

        # 将数据写入新的json文件
        new_file.write(json.dumps(data, ensure_ascii=False) + '\n')

        # Skipped due to error: 334”的基础上，将deepseek换为代码“import json
