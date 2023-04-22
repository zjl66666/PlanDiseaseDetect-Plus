import datetime
import requests

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components  # 可用于定义图表长宽
from pyecharts.charts import *
from pyecharts.globals import ThemeType
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import emoji

Temp_emo = emoji.emojize('气温' + ':sunflower:')
BodyTemp_emo = emoji.emojize('Body Temperature' + ':maple_leaf:')
Humidity_emo = emoji.emojize('湿度' + ':droplet:')
Weather_emo = emoji.emojize('天气' + ':balloon:')
Weather_day_emo = emoji.emojize('天气' + '":balloon::sun:')
Weather_night__emo = emoji.emojize('WeatherNight' + ':balloon::milky_way:')
Wind_emo = emoji.emojize('风力' + ':wind_chime:')
Wind_day_emo = emoji.emojize('风力' + ':wind_chime::sun:')
Wind_night_emo = emoji.emojize('WindNight' + ':wind_chime::milky_way:')

def main():
    st.set_page_config(page_title="天气预报", page_icon=":rainbow:", layout="wide", initial_sidebar_state="auto")
    st.title('天气预报🌈 ')
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    charts_mapping = {
        'Line': 'line_chart', 'Bar': 'bar_chart', 'Area': 'area_chart', 'Hist': 'pyplot', 'Altair': 'altair_chart',
        'Map': 'map', 'Graphviz': 'graphviz_chart', 'Pyechart': ''
    }

    if 'first_visit' not in st.session_state:
        st.session_state.first_visit = True
    else:
        st.session_state.first_visit = False

    if st.session_state.first_visit:
        st.session_state.date_time = datetime.datetime.now()
        st.session_state.city_mapping, st.session_state.random_city_index = get_city_mapping()
        st.balloons()
        st.snow()

    d = st.sidebar.date_input('日期 📆', st.session_state.date_time.date())
    # 显示时间并且随时间变化
    t  = st.sidebar.time_input('时间⏳', datetime.datetime.now().time())
    # t = st.sidebar.time_input('时间⏳', st.session_state.date_time.time())
    t = f'{t}'.split('.')[0]  # datetime.date_time.time()最后面会显示'.xxx'
    nighttime = ['00', '01', '02', '03', '04', '05', '18', '19', '20', '21', '22', '23']  # 后面判断是否为晚上
    # city的默认值为当前用户所在城市
    city = st.sidebar.selectbox(emoji.emojize('选择城市(按首字母顺序) 🏠 '),
                                st.session_state.city_mapping.keys(),
                                index=st.session_state.random_city_index)
    with st.container():
        if t[:2] in nighttime:
            st.markdown(f'### {city}:star::moon:')
        else:
            st.markdown(f'### {city}:sunrise::palm_tree:')
        forecastToday, df_forecastHours, df_forecastDays = get_city_weather(st.session_state.city_mapping[city])
        col1, col2= st.columns(2)
        col3, col4 = st.columns(2)
        col1.metric('天气', forecastToday['weather'])
        col2.metric('气温', forecastToday['temp'])
        col3.metric('湿度', forecastToday['humidity'])
        col4.metric('风力', forecastToday['wind'])

        option = (
        'LIGHT', 'CHALK', 'DARK', 'ESSOS', 'INFOGRAPHIC', 'MACARONS', 'PURPLE_PASSION', 'ROMA', 'ROMANTIC', 'SHINE',
        'VINTAGE', 'WALDEN', 'WESTEROS', 'WONDERLAND')
        options = st.selectbox("选择图表颜色🎨", option)


        c1 = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.DARK if t[:2] in nighttime else ThemeType.LIGHT))
                .add_xaxis(df_forecastHours.index.to_list())  # 添加x,y轴
                .add_yaxis('气温', df_forecastHours[Temp_emo].values.tolist())
                .add_yaxis('体感温度', df_forecastHours[BodyTemp_emo].values.tolist())
                .set_global_opts(
                title_opts=opts.TitleOpts(title="24小时预报"),  # 标题
                xaxis_opts=opts.AxisOpts(type_="category"),  # 坐标轴类型,'category'适用于离散的数据
                yaxis_opts=opts.AxisOpts(type_="value", axislabel_opts=opts.LabelOpts(formatter="{value} °C")),  # 连续数据
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")  # 坐标轴触发提示框，’十字‘瞄准线
            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
            # ?
        )
        c2 = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.CHALK if t[:2] in nighttime else ThemeType.LIGHT))
                .add_xaxis(xaxis_data=df_forecastDays.index.to_list())
                .add_yaxis(series_name="最高温度",
                           y_axis=df_forecastDays[Temp_emo].apply(lambda x: int(x.replace('°C', '').split('~')[1])))
                .add_yaxis(series_name="最低温度",
                           y_axis=df_forecastDays[Temp_emo].apply(lambda x: int(x.replace('°C', '').split('~')[0])))
                .set_global_opts(
                title_opts=opts.TitleOpts(title="7天预报"),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(type_="value", axislabel_opts=opts.LabelOpts(formatter="{value} °C")),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross")

            )
                .set_series_opts(label_opts=opts.LabelOpts(formatter=JsCode("function(x){return x.data[1] + '°C';}")))
        )
        t = Timeline(
            init_opts=opts.InitOpts(theme=eval(f'ThemeType.{options}')))
        t.add_schema(play_interval=10000)
        t.add(c1, "24小时预报")
        t.add(c2, "7天预报")
        components.html(t.render_embed(), width=1000, height=520)  # 调整大小

        with st.expander("24小时天气数据",expanded=True):
            # 去除体感温度列
            df_forecastHours = df_forecastHours.drop(columns=[BodyTemp_emo])
            st.table(df_forecastHours)
        with st.expander("未来七天天气数据",expanded=True):  # 默认为展开
            st.table(df_forecastDays)

def weather_emoji(x):
    if '晴' in x:
        return emoji.emojize(':sun:')
    if '云' in x or '阴' in x:
        return emoji.emojize(':cloud:')
    if '雪' in x:
        return emoji.emojize(':snowflake:')
    if '雨' in x:
        return emoji.emojize(':umbrella:')
    else:
        return ''


@st.cache_data(ttl=3600)
def get_city_mapping():
    url = 'https://h5ctywhr.api.moji.com/weatherthird/cityList'
    r = requests.get(url)
    data = r.json()
    city_mapping = dict()
    guangzhou = 0
    flag = True
    for i in data.values():
        for each in i:
            city_mapping[each['name']] = each['cityId']
            if each['name'] != '广州市' and flag:
                guangzhou += 1
            else:
                flag = False

    return city_mapping, guangzhou



@st.cache_data(ttl=3600)
def get_city_weather(cityId):
    url = 'https://h5ctywhr.api.moji.com/weatherDetail'
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    data = {"cityId": cityId, "cityType": 0}
    r = requests.post(url, headers=headers, json=data)
    result = r.json()

    # today forecast
    forecastToday = dict(
        humidity=f"{result['condition']['humidity']}%",
        temp=f"{result['condition']['temp']}°C",
        realFeel=f"{result['condition']['realFeel']}°C",
        weather=result['condition']['weather'],
        wind=f"{result['condition']['windDir']}{result['condition']['windLevel']}级",
        updateTime=(datetime.datetime.fromtimestamp(result['condition']['updateTime']) + datetime.timedelta(
            hours=8)).strftime('%H:%M:%S')
    )




    # 24 hours forecast
    forecastHours = []
    for i in result['forecastHours']['forecastHour']:
        tmp = {}
        tmp['PredictTime'] = (datetime.datetime.fromtimestamp(i['predictTime']) + datetime.timedelta(hours=8)).strftime(
            '%H:%M')
        tmp[Temp_emo] = i['temp']
        tmp[BodyTemp_emo] = i['realFeel']
        tmp[Humidity_emo] = i['humidity']
        tmp[Weather_emo] = i['weather'] + weather_emoji(i['weather'])
        tmp[Wind_emo] = f"{i['windDesc']}{i['windLevel']}级"
        forecastHours.append(tmp)
    df_forecastHours = pd.DataFrame(forecastHours).set_index('PredictTime')



    # 7 days forecast
    forecastDays = []
    day_format = {1: '昨天', 0: '今天', -1: '明天', -2: '后天'}
    for i in result['forecastDays']['forecastDay']:
        tmp = {}
        now = datetime.datetime.fromtimestamp(i['predictDate']) + datetime.timedelta(hours=8)
        diff = (st.session_state.date_time - now).days
        festival = i['festival']
        tmp['PredictDate'] = (day_format[diff] if diff in day_format else now.strftime('%m/%d')) + (
            f' {festival}' if festival != '' else '')
        tmp[emoji.emojize('气温'+':sunflower:')] = f"{i['tempLow']}~{i['tempHigh']}°C"
        tmp[Humidity_emo] = f"{i['humidity']}%"
        tmp[Weather_emo] = i['weatherDay'] + weather_emoji(i['weatherDay'])
        # tmp[Weather_night__emo] = i['weatherNight'] + weather_emoji(i['weatherNight'])
        tmp[Wind_emo] = f"{i['windDirDay']}{i['windLevelDay']}级"
        # tmp[Wind_night_emo] = f"{i['windDirNight']}{i['windLevelNight']}级"
        forecastDays.append(tmp)
    df_forecastDays = pd.DataFrame(forecastDays).set_index('PredictDate')
    return forecastToday, df_forecastHours, df_forecastDays


if __name__ == '__main__':
    main()