import tkinter as tk
import tkinter.filedialog
import os
import random
import codecs
import pyaudio
import numpy as np
import wave
import pandas as pd
import tkinter.font as tkFont
from tkinter import messagebox
import time


class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        master.title("ベースウィンドウ")
        master.withdraw()
        self.fontStyle = tkFont.Font(family=u'ＭＳ ゴシック', size=30)
        self.choice = tk.Toplevel()
        self.choice.state('zoomed')  # 画面を最大化
        self.length = 0  # テストデータの総数
        self.counter = 0  # 現在のワードを表すインデックス
        self.endflag = 0
        self.isInitialized = 0
        self.ap = pyaudio.PyAudio()
        self.showFilename = True  # ファイルネームを表示するかどうか

        # newボタンの配置クリックでinfoウインドウ生成
        self.choice.button_new = tk.Button(
            self.choice, text="New", command=self.openInfoWindow, font=self.fontStyle)
        self.choice.button_new.place(x=10, y=150)
        self.choice.button_new.config(fg="black", bg="skyblue")

        # Contineボタンの配置クリックでcontinueウインドウ生成
        self.choice.button_cnt = tk.Button(self.choice, text="Continue", command=self.openContinueWindow,
                                           font=self.fontStyle)
        self.choice.button_cnt.place(x=110, y=150)
        self.pack()
        self.choice.button_cnt.config(fg="black", bg="skyblue")

        # ボタンやラベルの表示変数
        self.text_file_name = tk.StringVar()
        self.sound_dir_name = tk.StringVar()
        self.csv_file_name = tk.StringVar()
        self.label1 = tk.StringVar()
        self.label2 = tk.StringVar()
        self.restlabel = tk.StringVar()

        # リストの宣言
        self.list_filename = []  # list1
        self.list_correct_answer_num = []
        self.list_class = []
        self.list_left_word_num = []
        self.list_left_word = []
        self.list_right_word_num = []
        self.list_right_word = []
        self.list_user_response = []
        self.list_play_times = []

    def openInfoWindow(self):

        # 入力画面の作成
        newflame = tk.Toplevel()
        newflame.state('zoomed')
        # newflame.geometry("300x300")
        newflame.title('new')
        # クリックでtxtを読み込むボタン
        newflame.button1 = tk.Button(
            newflame, text='testfile', command=lambda: self.loadfile('csv'), font=self.fontStyle)
        newflame.button1.pack()
        # 読み込んだtxtファイル名の表示
        newflame.label = tk.Label(
            newflame, textvariable=self.text_file_name, font=('', 12))
        newflame.label.pack()
        # クリックで音声ディレクトリを読み込むボタン
        newflame.button2 = tk.Button(
            newflame, text='sound_dir', command=lambda: self.loaddir(), font=self.fontStyle)
        newflame.button2.pack()
        # 読み込んだ音声ディレクトリの表示
        newflame.label2 = tk.Label(
            newflame, textvariable=self.sound_dir_name, font=('', 12))
        newflame.label2.pack()
        # 名前入力ボックス
        newflame.labelname = tk.Label(
            newflame, text='名前を入力してください（空白なしで）', font=('', 12))
        newflame.labelname.pack()
        newflame.name = tk.Entry(newflame)
        newflame.name.pack()

        # 年齢入力ボックス
        newflame.labelage = tk.Label(
            newflame, text='年齢を入力してください（空白なしで）', font=('', 12))
        newflame.labelage.pack()
        newflame.age = tk.Entry(newflame)
        newflame.age.pack()

        newflame.button2 = tk.Button(
            newflame, text='start', command=lambda: self.checkInfo(newflame), font=self.fontStyle)
        newflame.button2.pack()
        self.choice.destroy()

    def checkInfo(self, flame):
        self.name = flame.name.get()
        self.age = flame.age.get()
        if len(self.name) != 0 and len(self.age) != 0 and len(self.text_file_name.get()) != 0:
            self.csv_file_save_name = os.path.splitext(os.path.basename(self.text_file_name.get()))[
                0] + '_' + self.name + '_' + self.age + '.csv'
            self.openTestwindow(flame)
        else:
            res = messagebox.showwarning("title", "入力漏れがあります")
            print("showwarning", res)
            print(self.name)
            print(self.age)

    def openTestwindow(self, f):

        # テスト画面の作成
        # fontStyle = tkFont.Font(family=u'ＭＳ ゴシック', size=20)
        # Newの場合初期化
        self.setListFromText()
        if self.isInitialized == 0:
            self.initializeTestdata()
        else:
            self.recoverFromCsv()
        f.destroy()
        self.newflame = tk.Toplevel()
        self.newflame.state('zoomed')
        # self.newflame.geometry("300x300")

        label1 = tk.StringVar()
        label2 = tk.StringVar()
        self.restlabel.set(str(self.length - self.counter))
        self.newflame.title('test')
        print(self.list_filename[self.counter])
        self.label1.set(self.list_left_word[self.counter])
        self.label2.set(self.list_right_word[self.counter])

        # 外部クラスで音を制御する場合
        # self.ap = AudioPlayer(self.list_filename[self.counter])
        # 内部関数で制御

        # self.PlayWavFie()

        # 右側単語ボタンの配置
        self.newflame.firstword = tk.Button(
            self.newflame, text=self.list_left_word[self.counter], font=self.fontStyle, height=2, width=15, command=lambda: self.change_label('4'))
        self.newflame.firstword.grid(row=0, column=0)
        # 左側単語ボタンの配置
        self.newflame.secondword = tk.Button(
            self.newflame, text=self.list_right_word[self.counter], font=self.fontStyle, height=2, width=15, command=lambda: self.change_label('6'))
        self.newflame.secondword.grid(row=0, column=1)
        # リピートボタンの配置
        self.newflame.repeat = tk.Button(
            self.newflame, text='repeat', font=self.fontStyle, command=self.button_diactive_and_wavplay)
        self.newflame.repeat.grid(row=1, column=0)
        # セーブボタンの配置
        self.newflame.save = tk.Button(
            self.newflame, text='save', font=self.fontStyle, command=self.saveTest)
        self.newflame.save.grid(row=1, column=1)
        # 残り数表示
        self.newflame.restnumber = tk.Label(
            self.newflame, textvariable=self.restlabel, font=self.fontStyle)
        self.newflame.restnumber.grid(row=1, column=2)

        # 戻るボタンの配置
        self.newflame.abs = tk.Button(
            self.newflame, text='return', font=self.fontStyle, command=lambda: self.change_label('2'))
        self.newflame.abs.grid(row=1, column=3)
        # 音声流す
        self.newflame.bind(
            "<KeyPress-5>", lambda e: self.newflame.repeat.invoke())
        self.newflame.bind(
            "<KeyPress-4>", lambda e: self.newflame.firstword.invoke())
        self.newflame.bind(
            "<KeyPress-6>", lambda e: self.newflame.secondword.invoke())  # 右を選択
        self.newflame.bind(
            "<KeyPress-s>", lambda e: self.newflame.save.invoke())  # 右を選択
        self.newflame.protocol(
            "WM_DELETE_WINDOW", lambda: self.on_closing(self.newflame))

    def openContinueWindow(self):
        flame = tk.Toplevel()
        flame.state('zoomed')
        flame.title('Continew')
        self.isInitialized = 1
        csvFilename = tk.StringVar()
        # テキストロードボタンの配置
        flame.button_loadtxt = tk.Button(
            flame, text="LoadText", command=lambda: self.loadfile('csv'), font=self.fontStyle)
        # flame.button_loadtxt.place(x=10, y=150)
        flame.button_loadtxt.config(fg="black", bg="skyblue")
        flame.button_loadtxt.pack()

        flame.labelTextname = tk.Label(
            flame, textvariable=self.text_file_name, font=('', 12))
        flame.labelTextname.pack()

        # セーブデータ読み込みボタンの配置
        flame.button_loadsave = tk.Button(
            flame, text="LoadCsv", command=lambda: self.loadfile_savecsv('csv'), font=self.fontStyle)
        # flame.button_loadsave.place(x=110, y=150)
        flame.button_loadsave.config(fg="black", bg="skyblue")
        flame.button_loadsave.pack()

        flame.labelCsvname = tk.Label(
            flame, textvariable=self.csv_file_name, font=('', 12))
        flame.labelCsvname.pack()

        # クリックで音声ディレクトリを読み込むボタン
        flame.button_sounddir = tk.Button(
            flame, text='sound_dir', command=lambda: self.loaddir(), font=self.fontStyle)
        flame.button_sounddir.pack()

        # 読み込んだ音声ディレクトリの表示
        flame.label_sounddir = tk.Label(
            flame, textvariable=self.sound_dir_name, font=('', 12))
        flame.label_sounddir.pack()

        flame.button2 = tk.Button(
            flame, text='start test', command=lambda: self.openTestwindow(flame), font=self.fontStyle)
        flame.button2.pack()
        self.choice.destroy()

    def on_closing(self, flame):
        if messagebox.askokcancel("はい", "セーブせずに終了しますか?"):
            flame.destroy()

    def loadfile(self, filetipe):
        fTyp = [(filetipe+"file", filetipe)]
        iDir = os.path.abspath(os.path.dirname(__file__))
        file_name = tk.filedialog.askopenfilename(
            filetypes=fTyp, initialdir=iDir)
        if filetipe == 'csv':
            if len(file_name) == 0:
                self.text_file_name.set('選択をキャンセルしました')
            else:
                self.text_file_name.set(file_name)
        else:
            if len(file_name) == 0:
                self.csv_file_name.set('選択をキャンセルしました')
            else:
                self.csv_file_name.set(file_name)
                self.csv_file_save_name = file_name

    def loadfile_savecsv(self, filetipe):
        fTyp = [(filetipe+"file", filetipe)]
        iDir = os.path.abspath(os.path.dirname(__file__))
        file_name = tk.filedialog.askopenfilename(
            filetypes=fTyp, initialdir=iDir)
        if filetipe == 'csv':
            if len(file_name) == 0:
                self.text_file_name.set('選択をキャンセルしました')
            else:
                self.csv_file_name.set(file_name)
                self.csv_file_save_name = file_name

        

    def loaddir(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        dir_name = tk.filedialog.askdirectory(initialdir=iDir)
        if len(dir_name) == 0:
            self.sound_dir_name.set('選択をキャンセルしました')
        else:
            self.sound_dir_name.set(dir_name)

    # セーブデータから読み込み
    def recoverFromCsv(self):
        testTable = pd.read_csv(self.csv_file_name.get(),
                                index_col=0, encoding="shift-jis")
        # ファイル長の指定
        self.length = len(testTable)
        # 未回答番号の取得（最初の＃の位置の取得)しcounterに設定
        self.list_user_response = testTable['response'].values
        i = 0
        # 最初のシャープの位置を見つけたらcounterの番号を設定
        while self.counter == 0:
            if self.list_user_response[i] == '#':
                self.counter = i
            i = i + 1
        # 順番ランダム化のインデックス
        self.randomed_index = testTable['index'].values
        # 左右入れ替えランダム化のフラグ
        self.isSwap = testTable['isSwap'].values
        self.list_play_times = testTable['Play'].values

        # txtを前回と同じようにランダム化
        self.shutflleWord(self.randomed_index, self.isSwap)

    def shutflleWord(self, randomed_index, isSwap):

        # 順番の入れ替え
        print(randomed_index)
        list_filename_rand = []  # list1
        list_correct_answer_num_rand = []
        list_class_rand = []
        list_left_word_num_rand = []
        list_left_word_rand = []
        list_right_word_num_rand = []
        list_right_word_rand = []

        for i in range(self.length):
            list_filename_rand.append(
                self.list_filename[randomed_index[i]])  # list1
            list_correct_answer_num_rand.append(
                self.list_correct_answer_num[randomed_index[i]])
            list_class_rand.append(self.list_class[randomed_index[i]])
            list_left_word_num_rand.append(
                self.list_left_word_num[randomed_index[i]])
            list_left_word_rand.append(self.list_left_word[randomed_index[i]])
            list_right_word_num_rand.append(
                self.list_right_word_num[randomed_index[i]])
            list_right_word_rand.append(
                self.list_right_word[randomed_index[i]])

        self.list_filename = list_filename_rand
        self.list_correct_answer_num = list_correct_answer_num_rand
        self.list_class = list_class_rand
        self.list_left_word_num = list_left_word_num_rand
        self.list_left_word = list_left_word_rand
        self.list_right_word_num = list_right_word_num_rand
        self.list_right_word = list_right_word_rand
        print(self.list_correct_answer_num)

        # 位置（左右）の入れ替え

        sutfledWordLeft = []
        sutfledWordRight = []
        sutfledWordLeftNum = []
        sutfledWordRightNum = []
        sutfleFlag = 0
        for i, flag in enumerate(isSwap):
            if flag == 0:
                sutfledWordLeft.append(self.list_left_word[i])
                sutfledWordRight.append(self.list_right_word[i])
                sutfledWordLeftNum.append(self.list_left_word_num[i])
                sutfledWordRightNum.append(self.list_right_word_num[i])
            else:
                sutfledWordLeft.append(self.list_right_word[i])
                sutfledWordRight.append(self.list_left_word[i])
                sutfledWordLeftNum.append(self.list_right_word_num[i])
                sutfledWordRightNum.append(self.list_left_word_num[i])
        print(sutfledWordLeft)
        print(sutfledWordRight)
        self.list_left_word_num = []
        self.list_left_word = []
        self.list_right_word_num = []
        self.list_right_word = []
        self.list_left_word_num = sutfledWordLeftNum
        self.list_left_word = sutfledWordLeft
        self.list_right_word_num = sutfledWordRightNum
        self.list_right_word = sutfledWordRight

    def initializeTestdata(self):
        # シャッフルし初期化する

        # ランダム化するためのインデックス
        self.randomed_index = random.sample(range(self.length), self.length)
        # 左右入れ替えランダム化のフラグ
        self.isSwap = random.choices([0, 1], k=self.length)
        # ランダム化
        self.shutflleWord(self.randomed_index, self.isSwap)
        # pandasデータフレームの作成
        self.saveTest()
        self.isInitialized = 1

    def setListFromText(self):
        # テキストからデータを読み込む
        data = pd.read_csv(self.text_file_name.get(), encoding='shift-jis')

        self.length = len(data)
        self.list_filename = []  # list1
        self.list_correct_answer_num = []
        self.list_class = []
        self.list_left_word_num = []
        self.list_left_word = []
        self.list_right_word_num = []
        self.list_right_word = []
        self.list_user_response_num = []
        self.list_user_response_word = []

        # リストに一行分ずつ追加

        self.list_filename = [self.sound_dir_name.get(
        )+'/'+data.wavname.values[i] for i in range(len(data))]
        self.list_correct_answer_num = data.word_num
        self.list_class = data.group_num
        self.list_left_word_num = data.correct_num
        self.list_left_word = data.correct_word
        self.list_right_word_num = data.wrong_num
        self.list_right_word = data.wrong_word
        [self.list_user_response.append('#') for i in range(len(data))]
        [self.list_play_times.append(0) for i in range(len(data))]

    def change_label(self, clicked_number):

        self.master.after(1, self.setNextword, clicked_number)

        # self.master.after(10,self.PlayWavFie)
        # self.master.after(10,self.buttton_active())
        # self.setNextword()
        # self.PlayWavFie()

        # self.master.after(10, self.ap.setFile, self.list_filename[self.counter])
        # self.master.after(10, self.ap.stopAudio)
        #self.master.after(10, self.ap.playAudio(event))

    def setNextword(self, clicked_number):
        # 表示ラベルと音声の制御と回答の保存
        print(clicked_number)
        # 戻るかどうか
        isReturn = 0

        # 右を選択
        if clicked_number == '6':
            self.list_user_response[self.counter] = self.list_right_word_num[self.counter]
        # 左を選択
        elif clicked_number == '4':
            self.list_user_response[self.counter] = self.list_left_word_num[self.counter]
        # 戻るを選択
        elif clicked_number == '2':
            isReturn = 1

        # 最後の回答だった場合修了
        if self.counter == self.length - 1:
            messagebox.showinfo("お疲れ様です", "ご協力ありがとうございました")
            self.saveTest()
            self.newflame.destroy()
            self.master.destroy()
        # 左右を選択の場合回答をリストに追加し次に進む
        elif isReturn:
            self.counter = self.counter - 1
            self.newflame.firstword.config(
                text=self.list_left_word[self.counter])
            self.newflame.secondword.config(
                text=self.list_right_word[self.counter])
            self.restlabel.set(str(self.length - self.counter))
            self.master.after(1, self.button_diactive_and_wavplay)
        else:
            self.counter = self.counter + 1
            self.newflame.firstword.config(
                text=self.list_left_word[self.counter])
            self.newflame.secondword.config(
                text=self.list_right_word[self.counter])
            self.restlabel.set(str(self.length - self.counter))
            self.master.after(1, self.button_diactive_and_wavplay)

    def button_diactive_and_wavplay(self):
        self.newflame.firstword.config(state='disable')
        self.newflame.secondword.config(state='disable')
        self.newflame.repeat.config(state='disable')
        self.newflame.save.config(state='disable')
        self.master.after(1, self.PlayWavFie)
        self.list_play_times[self.counter] = str(
            int(self.list_play_times[self.counter])+1)

    # def debug_setNextword(self,clicked_number):
    #     # 表示ラベルと音声の制御と回答の保存
    #     print(clicked_number)
    #     if clicked_number == '6':
    #         #print('右を選択:番号')
    #         # self.list_user_response[self.counter] = self.list_right_word_num[self.counter]
    #         self.testTable.iloc[self.counter, 1] = self.list_right_word_num[self.counter]
    #         #print(self.list_right_word_num[self.counter])
    #     elif clicked_number == '4':
    #         #print('左を選択；番号')
    #         # self.list_user_response[self.counter] = self.list_left_word_num[self.counter]
    #         self.testTable.iloc[self.counter, 1] = self.list_left_word_num[self.counter]
    #         #print(self.list_left_word_num[self.counter])
    #     # print('右番号')
    #     # print(self.list_right_word_num[self.counter])
    #     # print('左番号')
    #     # print(self.list_left_word_num[self.counter])
    #     # print('正解番号')
    #     # print(self.list_correct_answer_num[self.counter])
    #     # 表示ラベルの変更
    #     #self.testTable.to_csv("employee.sjis.csv", encoding="shift_jis")
    #     self.counter = self.counter + 1
    #     # self.label1.set(self.list_first_word[self.counter])
    #     # self.label2.set(self.list_second_word[self.counter])
    #     self.master.after(1,self.abc)
    #     # self.newflame.firstword.config(text=self.list_left_word[self.counter])
    #     # self.newflame.secondword.config(text=self.list_right_word[self.counter])
    #     # self.restlabel.set(str(self.length - self.counter))
    #     # self.button_deactive()
    #     # self.master.after(5,self.PlayWavFie)
    #     #self.PlayWavFie()

    def saveTest(self):  # クラス、回答番号、正解番号を保存

        testTable = pd.DataFrame({
            'class': self.list_class,
            'response': self.list_user_response,
            'answer': self.list_correct_answer_num,
            'index': self.randomed_index,
            'isSwap': self.isSwap,
            'Lword': self.list_left_word,
            'Rword': self.list_right_word,
            'Play': self.list_play_times})
        testTable.to_csv(self.csv_file_save_name, encoding="shift_jis")

    def PlayWavFie(self):
        #p = pyaudio.PyAudio()
        if self.showFilename:
            print(self.list_filename[self.counter])
        wf = wave.open(self.list_filename[self.counter], "rb")
        stream = self.ap.open(format=self.ap.get_format_from_width(wf.getsampwidth()),
                              channels=wf.getnchannels(),
                              rate=wf.getframerate(),
                              output=True,
                              start=True)

        # 音声を再生
        CHUNK_SIZE = 1024
        #data = wf.readframes(chunk)
        data = wf.readframes(CHUNK_SIZE)

    ############################
    #これだとエラー出ない再生方法#####
    ###############################
    # Streamに読み取ったデータを書き込む＝再生する
        while len(data) > 0:
            # Streamに書き込む
            stream.write(data)

            # 再度チャンクサイズだけ読み込む。これを繰り返す
            data = wf.readframes(CHUNK_SIZE)
        stream.close()
        self.master.after(1, self.buttton_active)

        # p.terminate()

    # ボタンを使用不可にする
    def button_deactive(self):
        self.newflame.firstword.config(state='disable')
        self.newflame.secondword.config(state='disable')
    # ボタンを使用可能にする

    def buttton_active(self):
        self.newflame.firstword.config(state='normal')
        self.newflame.secondword.config(state='normal')
        self.newflame.repeat.config(state='normal')
        self.newflame.save.config(state='normal')


'''音声再生方法候補だがエラーが出る
class AudioPlayer():
    """ A Class For Playing Audio """

    def __init__(self, filename):
        self.filename = filename

    def setFile(self, filename):
        self.filename = filename

    # def setStream(self):
    #     print(type(self.filename))
    #     print(self.filename)
    #     self.wf = wave.open(self.filename, "rb")
    #     self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
    #                               channels=self.wf.getnchannels(),
    #                               rate=self.wf.getframerate(),
    #                               output=True,
    #                               )

    def playAudio(self, e):
        p = pyaudio.PyAudio()
        wf = wave.open(self.filename, "rb")
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,

                        )
        chunk = 1024
        data = wf.readframes(chunk)
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)
        stream.close()
        p.terminate()
'''


def main():
    win = tk.Tk()
    app = Application(win)
    app.mainloop()


if __name__ == '__main__':
    main()
