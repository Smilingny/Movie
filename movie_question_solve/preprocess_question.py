import os
import re
import jieba
from jieba import posseg
import joblib
from movie_question_solve.question_classifier import get_tv
from movie_question_solve.question_template_solve import QuestionTemplate


class question:
    def __init__(self):
        self.path_info = os.path.split(os.path.realpath(__file__))[0]  # python包位置
        moviedict = self.path_info + "/data/movieinfo.txt"
        peopledict = self.path_info + "/data/peopleinfo.txt"
        genredict = self.path_info + "/data/genreinfo.txt"
        jieba.load_userdict(moviedict)
        jieba.load_userdict(peopledict)
        jieba.load_userdict(genredict)

        self.init_config()

    def init_config(self):
        self.tv = get_tv()
        # 读取问题模板
        with open(self.path_info + "./data/question/question_classification.txt", "r", encoding="utf-8") as f:
            question_mode_list = f.readlines()
        self.question_mode_dict = {}
        for one_mode in question_mode_list:
            mode_id, mode_str = str(one_mode).strip().split(":")
            self.question_mode_dict[int(mode_id)] = str(mode_str)
        # 创建问题模板对象
        self.questiontemplate = QuestionTemplate()


    def dopredict(self, question):  # 调用分类模型判断问题类别
        model = joblib.load(self.path_info + "./model/question_classifier.model")
        question = [" ".join(list(jieba.cut(question)))]
        print("分词结果是：{0}".format(question))
        test_data = self.tv.transform(question).toarray()
        y_predict = model.predict(test_data)[0]
        return y_predict

    def question_posseg(self):
        # 进行问题的词性标注
        clean_question = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+", "", self.raw_question)
        self.clean_question = clean_question
        question_seged = posseg.cut(str(clean_question))

        result = []
        question_word, question_flag = [], []
        for w in question_seged:  # 词性标注的结果
            tmp_word = f"{w.word}/{w.flag}"
            result.append(tmp_word)
            word, flag = w.word, w.flag
            question_word.append(str(word).strip())
            question_flag.append(str(flag).strip())

        self.question_word = question_word
        self.question_flag = question_flag

        return result

    def get_question_template(self):
        # 将问题抽象成模板
        for item in ['nr', 'nm', 'ng']:
            while item in self.question_flag:
                ix = self.question_flag.index(item)
                self.question_word[ix] = item
                self.question_flag[ix] = item+"ed"
        # 将问题转化字符串
        str_question = "".join(self.question_word)
        print("抽象问题为：", str_question)
        # 通过分类器获取问题模板编号
        question_template_num = int(self.dopredict(str_question))
        print("使用模板编号：", question_template_num)
        question_template = self.question_mode_dict[question_template_num]
        print("问题模板：", question_template)
        question_template_id_str = str(question_template_num)+"\t"+question_template
        return question_template_id_str

    def query_template(self):
        # 调用问题模板类中查询答案的方法
        try:
            template_num = int(self.question_template_id_str.split("\t")[0])
            print(template_num)
            if template_num != 7:
                answer = self.questiontemplate.get_question_answer(self.pos_question, self.question_template_id_str)
            else:
                answer = self.questiontemplate.get_question_answer(self.pos_question, self.question_template_id_str)[0]
        except:
            answer = "小球暂未学习到问题的答案……期待我的成长吧！"
        return answer

    def question_process(self, question):
        self.raw_question = str(question).strip()  # 原始问题
        self.pos_question = self.question_posseg()  # 词性标注后的问题
        print("词性标注结果是：{0}".format(self.pos_question))
        self.question_template_id_str = self.get_question_template()  # 得到问题模板

        self.answer = self.query_template()  # 查询图数据库，得到答案

