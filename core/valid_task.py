import abc
from typing import List, Type, Any, Optional, Union

from core.constant import NORMAL_COORD, HARD_COORD


class InputBoxBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def create(self) -> Union[int, float, list, dict, str]:
        pass

    @abc.abstractmethod
    def check(self, obj) -> str:
        """
        传入obj，如果没有问题输出""，否则输出错误信息
        """
        pass


class IntInputer(InputBoxBase):
    def create(self) -> int:
        while True:
            a = input("请输入一个整数 ")
            if a.isnumeric():
                return int(a)
            else:
                print("输入错误，请重新输入")

    def check(self, obj):
        if not isinstance(obj, int):
            return f"应是int类型，而不是{type(obj)}"
        return ""


class FloatInputer(InputBoxBase):
    def create(self) -> float:
        while True:
            a = input("请输入一个实数 ")
            try:
                return float(a)
            except:
                print("输入错误，请重新输入")

    def check(self, obj):
        if not isinstance(obj, (float, int)):
            return f"应是float类型，而不是{type(obj)}"
        return ""


class StrInputer(InputBoxBase):
    def create(self) -> str:
        a = input("请输入一个字符串 ")
        return a

    def check(self, obj):
        if not isinstance(obj, str):
            return f"应是str类型，而不是{type(str)}"
        return ""


class BoolInputer(InputBoxBase):
    def create(self) -> bool:
        while True:
            a = input("请输入True或False ")
            if a == "True":
                return True
            elif a == "False":
                return False
            else:
                print("输入错误，请重新输入")

    def check(self, obj):
        if not isinstance(obj, bool):
            return f"应是str类型，而不是{type(str)}"
        return ""


STANDARD_INPUTBOX = {
    int: IntInputer(),
    float: FloatInputer(),
    str: StrInputer(),
    bool: BoolInputer()
}


# 合法Task参数
class TaskParam:
    def __init__(self, key: str, typ: Optional[Type] = None, title: Optional[str] = None,
                 desc: Optional[str] = None,
                 default: Optional[Any] = None, inputbox=None, inputcheck=None):
        """
        构建一个合法Task的参数
        :param key:
            参数的名字，最终调用Automator的函数时，与函数参数的名字一一对应。
        :param typ:
            参数的类型，如果不是指定类型则判定不合法。
            默认为None，则任何类型均可
            可以指定为某一个type，则必须要求该参数类型为type
        :param title:
            参数的标题，显示给用户看。
        :param desc:
            参数的描述，显示给用户看。
        :param default:
            参数的默认值，默认为None，则表示强制输入该参数。
            如果设置了默认值，则该参数将以default进行初始化。
        :param inputbox:
            如果typ非int,float,bool，则需要专门制定inputbox。
            用来输入该类型
        """
        self.key = key
        self.typ = typ
        if title is None:
            self.title = self.key
        else:
            self.title = title
        if desc is None:
            self.desc = "没有描述"
        else:
            self.desc = desc
        self.default = default
        if inputbox is None:
            if typ in STANDARD_INPUTBOX:
                self.inputbox = STANDARD_INPUTBOX[typ]
            else:
                raise Exception(f"参数{key}必须为类型{typ}指定输入方法！")
        else:
            self.inputbox = inputbox

    def check(self, obj, is_raise=True):
        s = self.inputbox.check(obj)
        if s != "":
            if is_raise:
                raise Exception(f"参数{self.key}填写错误：{s}")
            else:
                return False
        return True


class ValidTask:
    def __init__(self):
        self.T = {}  # 存放合法Task记录

    def add(self, abbr: str, funname: str, title: str, desc: str, params: Optional[List[TaskParam]] = None):
        """
        增加一条Task规则
        :param abbr:
            Task的简写，在json文件中唯一表示一个Task。
        :param funname:
            对应到Automator中指定函数的名称
        :param title:
            Task的标题，显示给用户看
        :param desc:
            Task的描述，显示给用户看
        :param params:
            Task的参数，如果为None，则没有参数
            或者为List[TaskParam]，一个列表，里面为TaskParam类型。
            表示所有合法的参数
        """
        if params is None:
            params = []
        self.T[abbr] = {
            "funname": funname,
            "title": title,
            "desc": desc,
            "params": params
        }
        return self


def ShuatuToTuple(lst: list) -> list:
    l = []
    for i in lst:
        try:
            ss = i.strip().split("-")
            l += [(int(ss[0]), int(ss[1]), int(ss[2]))]

        except:
            pass
    l.sort()
    return l


class ShuatuBaseBox(InputBoxBase):
    def __init__(self):
        self.tu_dict = {}

    def transform(self):
        d = []
        for (A, B), T in self.tu_dict.items():
            d += [f"{A}-{B}-{T}"]
        return d

    def Help(self):
        print("帮助（命令用空格隔开）：")
        print("add (A) (B) (Times): 增加刷图：A-B Times次")
        print("add (A) all (Times): 增加刷图：A-全部 Times次")
        print("del (A) (B) (Times): 减少刷图：A-B Times次")
        print("file (FileAddress): 从文件导入")
        print("   该文件由多行组成，每行三个整数A,B,T，表示刷A-B T次")
        print("clear: 清空记录")
        print("show: 显示当前记录")
        print("end: 保存并退出编辑")

    def check(self, obj) -> str:
        if not isinstance(obj, list):
            return f"应是list类型，而不是{type(obj)}"
        for i in obj:
            if not isinstance(i, str):
                return f"list的每一项都应是str类型，但检测到{type(i)}"
            if '-' not in i:
                return f"list的每一项都应是A-B-T的格式，但{i}中不含'-'。"
            ii = i.split('-')
            if len(ii) != 3:
                return f"必须用-分割三个整数，但检测到{i}不符合要求"
            try:
                A = int(ii[0])
                B = int(ii[1])
                T = int(ii[2])
            except:
                return f"必须用-分割三个整数，但检测到{i}不符合要求"
        return ""

    @abc.abstractmethod
    def add(self, A, B, T):
        pass

    @abc.abstractmethod
    def del_(self, A, B, T):
        pass

    def create(self) -> list:
        self.tu_dict = {}
        print("输入图号 (help 查看帮助)")
        while True:
            try:
                cmd = input("> ")
                cmds = cmd.split(" ")
                order = cmds[0]
                if order == "clear":
                    self.tu_dict = {}
                elif order == "add":
                    self.add(cmds[1], cmds[2], cmds[3])
                elif order == "del":
                    self.del_(cmds[1], cmds[2], cmds[3])
                elif order == "show":
                    for A, B, T in ShuatuToTuple(self.transform()):
                        print(f"{A}-{B} {T} 次")
                elif order == "end":
                    return self.transform()
                elif order == "help":
                    self.Help()
                elif order == "file":
                    with open(cmds[1], "r", encoding="utf-8") as f:
                        for line in f:
                            l = line.strip().split(" ")
                            self.add(l[0], l[1], l[2])
                else:
                    print("未知的命令")
            except:
                print("命令输入错误，请重新输入")


class ShuatuNNBox(ShuatuBaseBox):

    def add(self, A, B, T):
        A = int(A)
        if A not in NORMAL_COORD:
            print(f"图号 {A} 未录入")
            return
        T = int(T)
        if B == "all":
            for cat in ['left', 'right']:
                for bb in NORMAL_COORD[A][cat].keys():
                    self.tu_dict.setdefault((A, bb), 0)
                    self.tu_dict[(A, bb)] += T
        else:
            B = int(B)
            if B not in NORMAL_COORD[A]["left"] and B not in NORMAL_COORD[A]["right"]:
                print(f"图号 {A} - {B} 未录入")
                return
            self.tu_dict.setdefault((A, B), 0)
            self.tu_dict[(A, B)] += T

    def del_(self, A, B, T):
        A = int(A)
        if A not in NORMAL_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        T = int(T)
        if (A, B) in self.tu_dict:
            self.tu_dict[(A, B)] -= T
            if self.tu_dict[(A, B)] <= 0:
                del self.tu_dict[(A, B)]


class ShuatuHHBox(ShuatuBaseBox):
    def Help(self):
        print("输入图号")
        print("帮助（命令用空格隔开）：")
        print("add (A) (B) (Times): 增加刷图：A-B Times次")
        print("del (A) (B) (Times): 减少刷图：A-B Times次")
        print("file (FileAddress): 从文件导入")
        print("   该文件由多行组成，每行三个整数A,B,T，表示刷A-B T次")
        print("clear: 清空记录")
        print("show: 显示当前记录")
        print("end: 保存并退出编辑")

    def add(self, A, B, T):
        A = int(A)
        if A not in HARD_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        if B not in HARD_COORD[A]:
            print(f"图号H{A} - {B} 未录入")
            return
        T = int(T)
        self.tu_dict.setdefault((A, B), 0)
        self.tu_dict[(A, B)] += T

    def del_(self, A, B, T):
        A = int(A)
        if A not in NORMAL_COORD:
            print(f"图号 {A} 未录入")
            return
        B = int(B)
        T = int(T)
        if (A, B) in self.tu_dict:
            self.tu_dict[(A, B)] -= T
            if self.tu_dict[(A, B)] <= 0:
                del self.tu_dict[(A, B)]


class TeamInputer(InputBoxBase):
    def __init__(self):
        self.l = []

    def create(self) -> list:
        print("请输入队号")
        print("输入 A-B 表示使用编组A队伍B，其中A为1~5整数，B为1~3整数")
        print("输入 zhanli 表示按照战力排名取前五位组队")
        print("输入 end 结束编辑")
        count = 1
        self.l = []
        while True:
            try:
                s = input(f"队伍 {count}:")
                if s == "zhanli":
                    self.l += ["zhanli"]
                    count += 1
                    continue
                if s == "end":
                    return self.l
                ss = s.split("-")
                assert len(ss) == 2
                assert 1 <= int(ss[0]) <= 5
                assert 1 <= int(ss[1]) <= 3
                count += 1
                self.l += [s]
            except:
                print("输入有误，请重新输入")

    def check(self, obj) -> str:
        if not isinstance(obj, list):
            return f"应是list类型，而不是{type(obj)}"
        for i in obj:
            if not isinstance(i, str):
                return f"list的每一项都应是str类型，但检测到{type(i)}"
            if i == "" or i == "zhanli":
                continue
            if '-' not in i:
                return f"list的每一项都应是A-B的格式，或者为zhanli，但{i}不满足要求。"
            ii = i.split('-')
            if len(ii) != 2:
                return f"必须用-分割两个整数，但检测到{i}不符合要求"
            try:
                A = int(ii[0])
                B = int(ii[1])
            except:
                return f"必须用-分割两个整数，但检测到{i}不符合要求"
            if A < 1 or A > 5:
                return f"队号A-B中编组A必须为1~5的整数，但{i}不满足要求"
            if B < 1 or B > 3:
                return f"队号A-B中队伍B必须为1~3的整数，但{i}不满足要求"
        return ""


VALID_TASK = ValidTask() \
    .add("h1", "hanghui", "行会捐赠", "小号进行行会自动捐赠装备") \
    .add("h2", "tichuhanghui", "踢出行会", "将战力排名第一人踢出行会") \
    .add("h3", "yaoqinghanghui", "邀请行会", "邀请指定成员进入行会",
         [TaskParam("inviteUID", str, "UID", "被邀请者的UID号")]) \
    .add("h4", "jieshouhanghui", "接受行会", "接受行会的邀请信息") \
    .add("h5", "joinhanghui", "加入行会", "主动搜索并加入行会",
         [TaskParam("clubname", str, "行会名称", "要加入行会的名称")]) \
    .add("h6", "dianzan", "行会点赞", "给指定人点赞",
         [TaskParam("sortflag", int, "给谁点赞", "只能为0或者1的值\n0：给副会长点赞。\n1：给战力最高者点赞。", 0)]) \
    .add("h7", "zhiyuan", "支援设定", "按照战力排行设定支援（最高的）") \
    .add("h8", "joinhanghui", "加入行会", "主动搜索并加入行会（全识图版）",
         [TaskParam("clubname", str, "行会名称", "要加入行会的名称")]) \
    .add("d1", "dixiacheng_ocr", "地下城(使用OCR)", "小号地下城借人换mana",
         [TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。")]) \
    .add("d2", "dixiacheng", "地下城", "小号地下城借人换mana",
         [TaskParam("skip", bool, "跳过战斗", "设置为True时，第一层不打直接撤退。\n设置为False时，打完第一层。")]) \
    .add("d3", "dixiachengYunhai", "打云海关", "打通云海关【细节待补充】") \
    .add("d4", "dixiachengDuanya", "打断崖关", "打通断崖关【细节待补充】") \
    .add("d5", "shuatuDD", "通关地下城", "通用的打通地下城函数",
         [TaskParam("dxc_id", int, "地下城图号", "刷哪个地下城。\n目前支持:3"),
          TaskParam("mode", int, "模式", "mode 0：不打Boss，用队伍1只打小关\n"
                                       "mode 1：打Boss，用队伍1打小关，用队伍[1,2,3,4,5...]打Boss\n"
                                       "mode 2：打Boss，用队伍1打小关，用队伍[2,3,4,5...]打Boss"),
          TaskParam("stop_criteria", int, "终止条件", "设置为0时，只要战斗中出现人员伤亡，直接结束\n"
                                                  "设置为1时，一直战斗到当前队伍无人幸存，才结束\n"
                                                  "注：如果在小关遇到停止条件，则直接结束\n"
                                                  "打Boss时，如果选用mode 2，则当一个队触发停止条件后会更换下一个队伍\n"
                                                  "直到队伍列表全部被遍历完毕才结束。", 0),
          TaskParam("after_stop", int, "停止之后做什么", "设置为0时，直接回到主页\n"
                                                  "设置为1时，撤退并回到主页\n"
                                                  "注：如果mode==1（不打Boss），则打完小关之后是否撤退仍然受到该参数的影响", 0),
          TaskParam("teams", list, "编队列表", "编队列表，参战地下城所使用的编队\n"
                                           "按照列表顺序分别表示编队1号，2号，3号……\n"
                                           "每一个元素为一个字符串\n"
                                           "若为空字符串，则表示不进行队伍更改，沿用上次队伍\n"
                                           "若为\"zhanli\"，则按照战力排序，选择前五战力为当前队伍\n"
                                           "若为\“a-b\",其中a为1~5的整数，b为1~3的整数，则选择编组a队伍b", inputbox=TeamInputer())]) \
    .add("j1", "doJJC", "竞技场", "竞技场白给脚本") \
    .add("j2", "doPJJC", "公主竞技场", "公主竞技场白给脚本") \
    .add('r1', "gonghuizhijia", "家园领取", "收取公会之家的奖励") \
    .add("r2", "mianfeiniudan", "免费扭蛋", "抽取免费扭蛋") \
    .add("r3", "mianfeishilian", "免费10连", "抽取免费十连（如果有的话）") \
    .add("r4", "shouqu", "收取礼物", "收取全部礼物") \
    .add("r5", "shouqurenwu", "收取任务", "收取全部任务奖励。\n如果日常任务和主线任务都存在，需要收取两遍。") \
    .add("r6", "goumaitili", "购买体力", "购买一定次数的体力",
         [TaskParam("times", int, "购买次数", "购买体力的次数")]) \
    .add("r7", "goumaimana", "购买MANA", "购买指定次数的mana",
         [TaskParam("mode", int, "模式", "如果mode为0，则为购买mana的次数；\n如果mode为1，则为购买10连mana的次数。【宝石警告】", 1),
          TaskParam("times", int, "购买mana的次数", "购买mana的次数(第一次单抽不计入)")]) \
    .add("r8", "buyExp", "购买经验", "买空商店里的经验药水") \
    .add("r9", "tansuo", "探索", "进行探索活动",
         [TaskParam("mode", int, "模式", "只能为0~3的整数\n"
                                       "mode 0: 刷最上面的\n"
                                       "mode 1: 刷次上面的\n"
                                       "mode 2: 第一次手动过最上面的，再刷一次次上面的\n"
                                       "mode 3: 第一次手动过最上面的，再刷一次最上面的")]) \
    .add("t1", "rename", "重命名", "给自己换个名字",
         [TaskParam("name", str, "新名字", "你的新名字")]) \
    .add("s1", "shuajingyan", "刷经验1-1", "刷图1-1，经验获取效率最大。",
         [TaskParam("map", int, "主图", "如果你的号最远推到A-B,则主图为A。")]) \
    .add("s1-3", "shuajingyan3", "刷经验3-1", "刷图3-1，比较节省刷图卷。",
         [TaskParam("map", int, "主图", "如果你的号最远推到A-B,则主图为A。")]) \
    .add("s2", "shuatuNN", "刷N图", "使用扫荡券刷指定普通副本",
         [TaskParam("tu_dict", list, "刷图列表", "要刷的普通图", inputbox=ShuatuNNBox())]) \
    .add("s3", "shuatuHH", "刷H图", "使用扫荡券刷指定困难副本",
         [TaskParam("tu_dict", list, "刷图列表", "要刷的困难图", inputbox=ShuatuHHBox())]) \
    .add("s4", "doActivityHard", "刷活动图", "使用扫荡券刷活动副本（慎用，因为每次活动坐标都不同）")
