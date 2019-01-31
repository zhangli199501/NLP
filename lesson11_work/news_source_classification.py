import pandas as pd
import os
import numpy as np
import pickle

from sklearn.svm import SVC
from data_processing import DataProcessing
from sklearn.model_selection import train_test_split

class build_model():

    def __init__(self):
        self.model_svc = SVC(C=1000, gamma=0.001)
        self.svc_estimators = {}

    # 有放回采样，选8000个样本
    def sampling_with_return(self, train_data):
        seq = np.random.choice(range(len(train_data)), size=8000, replace=True)
        return train_data.iloc[seq, :]

    # 分层，从数据中选取正负标签各8000个样本，其中70%用作训练，30%用作测试
    def layer_sampling(self, train_data):
        data_0, data_1 = train_data[train_data['label'] == 0], train_data[train_data['label'] == 1]
        data = pd.concat((self.sampling_with_return(data_0), self.sampling_with_return(data_1)))
        features = data.drop('label', axis=1)
        labels = data['label']
        return train_test_split(features, labels, test_size=0.3)

    def fit(self, train_data):
        for i in range(3):
            X_train, X_test, y_train, y_test = self.layer_sampling(train_data)
            self.model_svc.fit(X_train, y_train)
            self.svc_estimators[i] = self.model_svc
            y_pred = self.svc_estimators[i].predict(X_test)
        return

    def predict(self, features):
        pred_labels = []
        for i in self.svc_estimators:
            pred_labels.append(self.svc_estimators[i].predict(features))
        y_hat = list(map(lambda x:1 if x>1 else 0,sum(pred_labels)))
        return y_hat

if __name__=="__main__":
    # 读取CSV
    news_data = pd.read_csv('..\\data\\export_sql_1558435\\sqlResult_1558435.csv', encoding='gb18030', index_col='id')
    if os.path.isfile('temp_file//train_data.pkl'):
        train_data = pickle.load(open('temp_file//train_data.pkl','rb'))
    else:
        processing = DataProcessing(news_data)
        train_data = processing.get_train_data()
    svc_model = build_model()
    svc_model.fit(train_data)
    features = train_data.drop(labels='label', axis=1)
    # 预测标签并存储
    predict_label = svc_model.predict(features)
    pickle.dump(predict_label, open('temp_file//predict_label.pkl', 'wb'))