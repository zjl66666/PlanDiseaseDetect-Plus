# 加载 my_model.h5 模型(一个训练好的resnet50模型)，然后进行预测test.jpg图片
import json

from keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np


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










