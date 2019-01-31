import pandas as pd
import numpy as np
import jieba
import pickle
from gensim.models import Word2Vec


class DataProcessing():
    '''
    输入原数据，处理成机器学习模型训练需要的数据
    '''

    def __init__(self, original_data):
        self.original_data = original_data
        self.WikiWord2vecModel = Word2Vec.load('..\\data\\WikipediaWord2ec\\word2vec_model')
        self.data = pd.DataFrame([])
        # 导入停用词字典
        with open('..\\data\\stopwords.txt') as fi:
            self.stopwords = fi.read().split()

    def cut(self, string):
        return ' '.join(jieba.cut(string)).split()

    def label_extract(self, source):
        '''
        如果存在新闻来源，且为含有'新华'则标签为1
        :param source: 新闻来源
        :return:
        '''
        if isinstance(source, str) and '新华' in source:
            return 1
        return 0

    def need2vec(self, word):
        '''
        排除新闻中的停用词、含有新华的词、不在word2vec模型中的词
        :param word:
        :return:
        '''
        if word in self.stopwords:
            return False
        if '新华' in word:
            return False
        if self.WikiWord2vecModel.wv.__contains__(word):
            return True
        else:
            return False

    def content2vec(self, string):
        '''
        将文本转化为向量，使用word2vec的值累加求平均
        :param string:
        :return:
        '''
        words = self.cut(string)
        all_vec = [self.WikiWord2vecModel.wv.get_vector(i) for i in words if self.need2vec(i)]
        if all_vec: #判断词向量是否为空
            return sum(all_vec)/len(all_vec)
        else:
            return np.zeros(self.WikiWord2vecModel.vector_size)

    def get_train_data(self):
        '''
        处理原有数据，返回可供训练的数据
        :return:
        '''
        # 处理空值、索引
        self.original_data = self.original_data[['source', 'content']].dropna(subset=['source', 'content'])
        self.original_data = self.original_data.reset_index(drop=True)

        # 处理标签列和特征
        self.data['label'] = self.original_data['source'].apply(self.label_extract)
        self.data['content'] = self.original_data['content']
        features = pd.DataFrame(list(map(self.content2vec, self.original_data['content'])))
        self.data = pd.concat((self.data, features),axis=1)

        # 将含有content的data保存
        pickle.dump(self.data, open('temp_file//data_processing.pkl', 'wb'))

        # 返回只含labels和features的数据
        self.train_data = self.data.drop(labels='content', axis=1)
        pickle.dump(self.data, open('temp_file//train_data.pkl', 'wb'))
        return self.train_data






