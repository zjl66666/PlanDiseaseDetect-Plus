import requests as rq
from apig_sdk import signer
import streamlit as st
import json
from keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

identification_scope = """
南瓜白粉病
柑橘黄龙病（柑橘绿化）
桃树叶斑病
樱桃白粉病
没有叶子
玉米北方叶枯病
玉米尾孢叶斑病 灰斑病
玉米锈病
甜椒菌斑病
番茄叶斑病
番茄叶螨、二斑叶螨病
番茄叶霉菌
番茄斑点疫霉病
番茄早疫病
番茄晚疫病
番茄细菌斑
番茄花叶病毒病
番茄黄化曲叶病毒病
苹果雪松苹果锈病
苹果黑星病
苹果黑腐病
草莓叶枯病
葡萄叶枯病（叶斑病）
葡萄埃斯卡（黑麻疹）
葡萄黑腐病
马铃薯早疫病
马铃薯晚疫病
"""


def get_pridcition(img):  # 传入图片，
    # 加载模型
    model = load_model('my_model.h5')
    # 根据训练数据的形式，对test.jpg进行预处理
    img = image.load_img(img, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255
    # 预测
    preds = model.predict(x)
    # 根据json文件，class_names.json是索引对应的类别名
    # 给输出概率排序，获取前五个，最大的在前面
    # 最终以字典形式返回{'predicted_label': 预测结果, 'scores': [可能的病害，概率]}，概率格式修改为xx.xx%
    class_names = json.load(open('class_names.json'))
    top_5 = preds[0].argsort()[-5:][::-1]
    scores = []
    for i in top_5:
        scores.append([class_names[str(i)], str(round(preds[0][i] * 100, 2)) + '%'])
    pridition = {'predicted_label': class_names[str(top_5[0])], 'scores': scores}
    return pridition


st.set_page_config(page_title='植物病虫害识别', page_icon='🌼', layout='centered', initial_sidebar_state='auto')
st.balloons()
st.title("植物病虫害识别🌼 ")
st.sidebar.subheader('识别范围🔍')
st.sidebar.text(identification_scope)
uploaded_file = st.file_uploader('选择一张植物病虫害叶子照片🐛')
if uploaded_file:
    st.image(uploaded_file, caption='上传的文件')
    # img_data = uploaded_file.read()
    with st.spinner('识别中...'):
        pred = get_prediction(uploaded_file)
    pred_label = pred['predicted_label']
    st.success('✅识别成功')
    st.subheader(f'识别结果为{pred_label}')
    with st.expander('查看更多信息'):
        st.write('预测结果及其可能的概率')
        for data in pred['scores']:
            st.write('可能的病害:', data[0], '概率:', data[1])
    # 读取json文件并展示info
    if '健康' in pred_label:
        st.subheader('该叶子健康😃')
    elif '没有'in pred_label:
        st.subheader('请上传含有叶子的图片')
    else:
        with open(f'./json数据/{pred_label}.json', 'r') as f:
            data = json.load(f)
            st.text(data['info'])
