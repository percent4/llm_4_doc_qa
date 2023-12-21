# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: server_gradio.py
# @time: 2023/9/8 23:11
import json
import re
import gradio as gr

from config.config_parser import MODEL_NAME_LIST
from qa.doc_qa import DocQA
from qa.doc_qa_evaluation import DocQAEvaluation


# single qa
def document_qa(model_list, is_show_reference, question):
    # print(model_list, is_show_reference, question)
    output = []
    for model_name in model_list:
        reply, contexts, sources = DocQA(question).answer(model_name)
        if is_show_reference:
            metric_result = DocQAEvaluation(question=question, answer=reply, context=contexts).evaluate()
            metric = "\n".join([f"{k}: {v}" for k, v in metric_result.items()])
            output.append([model_name, question, reply, contexts, sources, metric])
        else:
            output.append([model_name, question, reply, "", "", ""])
    return output


# find most like sentence
def find_most_like_sentence(answer, candidates):
    similarity_list = []
    for candidate in candidates:
        s1 = set(answer)
        s2 = set(candidate)
        similarity = len(s1 & s2) / len(s1 | s2)
        similarity_list.append(similarity)

    flag, max_num = 0, 0
    for i in range(len(similarity_list)):
        if similarity_list[i] > max_num:
            flag = i
            max_num = similarity_list[i]

    return flag


def highlight(df):
    reply = df.iloc[0, 2]
    contexts = df.iloc[0, 3]
    sents = [_ for _ in re.split(r"<\d>:", contexts) if _]
    flag = find_most_like_sentence(reply, sents)
    # for highlight
    compare = []
    for i, sent in enumerate(sents):
        compare.append((f"<{i+1}>", "other"))
        if i != flag:

            for char in sent:
                compare.append((char, "other"))
        else:
            for char in sent:
                if char in reply:
                    compare.append((char, "same"))
                else:
                    compare.append((char, "other"))

    return compare


with gr.Blocks() as demo:
    # 模型组件
    models = gr.CheckboxGroup(choices=MODEL_NAME_LIST,
                              value=MODEL_NAME_LIST[0],
                              type="value",
                              label="LLMs")
    # 追溯答案
    show_reference = gr.Checkbox(label="Show Answer Reference")
    # 设置输入组件
    q = gr.Textbox(lines=3, placeholder="Your question ...", label="doc qa")
    # 设置输出组件
    answer = gr.DataFrame(label='Answer',
                          headers=["model", "question", "answer", "reference", "source", "metric"],
                          wrap=True)
    outputs = gr.HighlightedText(label="Diff",
                                 combine_adjacent=True,
                                 show_legend=True
                                 ).style(color_map={"same": "yellow", "other": "white"})
    theme = gr.themes.Base()
    # 设置按钮
    greet_btn = gr.Button("Submit")
    # 设置按钮点击事件
    greet_btn.click(fn=document_qa, inputs=[models, show_reference, q], outputs=answer)
    # 文本高亮
    reference = gr.Button("Show Answer Reference")
    reference.click(fn=highlight, inputs=answer, outputs=outputs)


demo.launch()
