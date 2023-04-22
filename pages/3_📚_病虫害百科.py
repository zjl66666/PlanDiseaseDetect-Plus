""""测试streamlit效果"""
import streamlit as st
import json
from PIL import Image
from io import BytesIO
import base64
import os

identification_scope = """
苹果🍎
番茄🍅
葡萄🍇
马铃薯🥔
草莓🍓
柑橘🍊
樱桃🍒
玉米🌽
甜椒🌶️
南瓜🎃
"""
st.set_page_config(page_title='病虫害百科', page_icon='📚', layout='centered', initial_sidebar_state='auto')
st.title('病虫害百科📚')
# 写一个侧边栏，含有一个selectbox，让用户选择要展示的植物种类
st.sidebar.title('选择要展示的植物种类☘️')
fruites = ('苹果', '番茄', '葡萄', '马铃薯', '草莓', '柑橘', '樱桃', '玉米', '甜椒', '南瓜')
option = st.sidebar.selectbox('选择植物', fruites)
st.sidebar.title('植物种类🔍')
st.sidebar.text(identification_scope)
# 读取json文件,例如：option是葡萄，那么就读取所有关于葡萄的json文件,包括葡萄叶枯病（叶斑病）.json，葡萄叶枯病（叶斑病）.json等
for file in os.listdir('./json数据'):
    if option in file:
        with open(f'json数据/{file}', 'r') as f:
            data = json.load(f)
            st.subheader(data['name'])
            img_num = len(data['img'])
            col1, col2, col3 = st.columns(3)
            # 将图片分为三列展示
            for i, img in enumerate(data['img']):
                eval(f'col{i % 3 + 1}').image(Image.open(BytesIO(base64.b64decode(img))))
            # with st.expander('更多信息'):
            #     st.text(data['info'])
            with st.expander('基本信息',expanded=True):
                st.text(data['info'])




