import traceback
import requests
from pbf.driver.Fastapi import description

from pbf.utils import MetaData
from pbf.setup import logger, pluginsManager, ListenerManager
from pbf.utils.Register import Command
from pbf.utils.Config import Config
from pbf.controller.Data import Event
from pbf.controller.Client import Msg
from pbf.statement import Statement
from pbf.statement.TextStatement import TextStatement
from pbf.config import plugins_config


class FaceStatement(Statement):
    id: str = None
    cqtype = "face"

    def __init__(self, id: str):
        self.id = str(id)

class MenuConfig(Config):
    originData = {
        "bot_name": "小猪比机器人",
        "hitokoto": {
            "enable": True,
            "api": "https://v1.hitokoto.cn/",
        },
    }


config = MenuConfig(plugins_config.get("menu", {}))


# 插件元数据
meta_data = MetaData(
    name="菜单",
    version="0.1.0",
    versionCode=10,
    description="A Menu Plugin",
    author="XzyStudio",
    license="MIT",
    keywords=["pbf", "plugin", "menu"],
    readme="""
    # A Menu Plugin
    to be continued.
    """
)


def getPluginName(plugin_id: str):
    return pluginsManager.plugins.get(plugin_id).meta_data.name

def getHitokoto():
    return requests.get(config.get("hitokoto.api")).json()


class Api:
    @staticmethod
    def text():
        msg_list: list = [
            FaceStatement(144),
            TextStatement(f" {config.get('bot_name')}菜单\n", enter_flag=True)
        ]
        iter: int = 1
        for k, v in ListenerManager.get_listeners_by_type("command").items():
            plugin_name = getPluginName(k)
            if iter % 2 == 1:
                # 左排
                msg_list.append(FaceStatement(147))
                msg_list.append(TextStatement(f" {plugin_name}  "))
            else:
                # 右排
                msg_list.append(TextStatement(f"{plugin_name} "))
                msg_list.append(FaceStatement(147))
                msg_list.append(TextStatement("", enter_flag=True))
            iter += 1

        if iter % 2 == 0:
            msg_list.append(TextStatement("", enter_flag=True))
        msg_list.append(TextStatement("\n发送“菜单 [上面的分类名]”就可以查看详细指令啦", enter_flag=True))

        if config.get("hitokoto.enable"):
            hitokoto: dict = getHitokoto()
            msg_list.append(TextStatement(f"\n{hitokoto.get('hitokoto')}\n    --{hitokoto.get('creator')}"))
        return msg_list



@Command(name="菜单", description="获取默认菜单！", usage="菜单 [指令分类]")
def menuCommand(event: Event):
    if len(event.message_list) == 1:
        Msg(*Api.text(), event=event).send()
    else:
        cmdList: list = ListenerManager.get_listeners_by_type("command")
        plugin = event.message_list[1]
        for i in cmdList.keys():
            if getPluginName(i) == plugin:
                msg_list: list = [
                    TextStatement(f"[{plugin}] 指令列表：", enter_flag=True)
                ]
                cmds = cmdList.get(i)
                for item in cmds:
                    msg_list.append(TextStatement(f"\n- {item.usage}\n  {item.description}", enter_flag=True))
                Msg(msg_list, event=event).send()
                break
        else:
            Msg(TextStatement("未找到该分类！", enter_flag=True), event=event).send()


@Command(name="扫描表情", description="扫描表情ID", usage="扫描表情 <起始ID> <终止ID>")
def scanCommand(event: Event):
    _, start, stop = event.message_list
    msg_list: list = []
    for i in range(int(start), int(stop)+1):
        msg_list.append(TextStatement(f" {i}:"))
        msg_list.append(FaceStatement(i))
    Msg(msg_list, event=event).send()

@Command(name="帮助", description="获取帮助", usage="帮助 <指令名>")
def helpCommand(event: Event):
    cmdList: list = ListenerManager.get_listeners_by_type("command")
    cmd = event.message_list[1]
    for i in cmdList.keys():
        cmds = cmdList.get(i)
        for item in cmds:
            if item.name == cmd:
                Msg([
                    FaceStatement(53), TextStatement(f"指令帮助", enter_flag=True),
                    TextStatement(f"指令：{item.name}", enter_flag=True),
                    TextStatement(f"描述：{item.description}", enter_flag=True),
                    TextStatement(f"用法：{item.usage}", enter_flag=True),
                    TextStatement(f"类型：{item.type}", enter_flag=True),
                    TextStatement(f"权限：{item.permission}", enter_flag=True),
                    TextStatement(f"隶属于插件：{getPluginName(i)}", enter_flag=True),
                ], event=event).send()
                break
        else:
            continue
        break
    else:
        Msg(TextStatement("未找到该指令！", enter_flag=True), event=event).send()
