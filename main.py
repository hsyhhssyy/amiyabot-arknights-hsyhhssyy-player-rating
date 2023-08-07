import asyncio
import datetime
import os
import json
import hmac
import hashlib
import base64
import uuid
import requests
from typing import Optional

from amiyabot import PluginInstance
from core import log, Message, Chain
from core.resource.arknightsGameData import ArknightsGameData
from core import bot as main_bot


curr_dir = os.path.dirname(__file__)

last_upload_dates = {}  # Step 1: 创建一个全局的字典来跟踪用户的上次上传时间

class PlayerRatingPluginInstance(PluginInstance):
    def install(self):
        pass
                
bot = PlayerRatingPluginInstance(
    name='玩家Box评分',
    version='1.0',
    plugin_id='amiyabot-arknights-hsyhhssyy-player-rating',
    plugin_type='',
    description='利用森空岛API读取玩家Box然后打分',
    document=f'{curr_dir}/README.md'
)

def hash_uid(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()

def upload_data(data_dict,user_id):
    try:
        # 阿里云oss只写权限账户
        OSS_ACCESS_ID = 'LTAI5tFf4i8dvmmtLJXqA48X'
        OSS_ACCESS_KEY = 'u6yqUCZXtXTliRpf5fdhtCRFb8P3WD'
        OSS_ENDPOINT = 'oss-cn-beijing.aliyuncs.com'
        OSS_BUCKET = 'amiyabot-playerbox-collector'
        OBJECT_DIRECTORY = 'collected_data_v1'

        current_time = datetime.datetime.now().strftime('%Y%m%d.%H%M%S')

        hashed_uid = hash_uid(user_id)

        FILE_NAME = f"chars.{hashed_uid}.{current_time}.json"

        json_data = json.dumps(data_dict).encode('utf-8')

        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        string_to_sign = f'PUT\n\napplication/json\n{date}\n/{OSS_BUCKET}/{OBJECT_DIRECTORY}/{FILE_NAME}'
        h = hmac.new(OSS_ACCESS_KEY.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha1)
        signature = base64.encodebytes(h.digest()).strip()

        headers = {
            'Date': date,
            'Authorization': f'OSS {OSS_ACCESS_ID}:{signature.decode("utf-8")}',
            'Content-Type': 'application/json'
        }

        # 发送请求
        response = requests.put(f'http://{OSS_BUCKET}.{OSS_ENDPOINT}/{OBJECT_DIRECTORY}/{FILE_NAME}', data=json_data, headers=headers)

        log.info(f'发送用户box返回信息:{response.content}')
    except Exception as e:
        log.info(f"发送用户box时出错:{str(e)}")

def calculate_score(character,char_map_data):
    score_dict = {
        "total": 0,
        "base": 0,
        "level": 0,
        "specialize": 0,
        "equip": 0
    }
    
    if character["evolvePhase"] >= 2:
        if char_map_data["rarity"] == 3:
            score_dict["base"] += 40
        elif char_map_data["rarity"] == 4:
            score_dict["base"] += 70
        elif char_map_data["rarity"] == 5:
            score_dict["base"] += 100

        score_dict["level"] = character["level"]

        # 根据技能专精级别加分
        for skill in character["skills"]:
            if skill["specializeLevel"] == 1:
                score_dict["specialize"] += 20
            elif skill["specializeLevel"] == 2:
                score_dict["specialize"] += 60
            elif skill["specializeLevel"] == 3:
                score_dict["specialize"] += 100
        
        # 根据模组级别加分
        for equipment in character["equip"]:
            if equipment["level"] == 1:
                score_dict["equip"] += 0
            elif equipment["level"] == 2:
                score_dict["equip"] += 30
            elif equipment["level"] == 3:
                score_dict["equip"] += 50
        
        # 计算总分
        score_dict["total"] = score_dict["base"] + score_dict["level"] + score_dict["specialize"] + score_dict["equip"]

    return score_dict

@bot.on_message(keywords='查看计分规则', allow_direct=True)
async def _(data: Message):
    with open(f'{curr_dir}/README_RATING.md', mode='r', encoding='utf-8') as md:
        content = md.read()

    chain = Chain(data).text('博士，请阅读计分规则。').markdown(content)

    return chain

@bot.on_message(keywords=['给我打分'],level=5)
async def _(data: Message):
    
    try:
        # 先获取Token并获取干员数据

        if 'amiyabot-skland' not in main_bot.plugins:
            return Chain(data).text('没有安装/启用森空岛插件，无法获取玩家数据')
        
        plugin = main_bot.plugins['amiyabot-skland']

        token: Optional[str] = await plugin.get_token(data.user_id)

        if not token:
            return Chain(data).text('博士，您尚未绑定 Token，请发送 “兔兔绑定” 进行查看绑定说明。')

        eula = f'您确定要计算您的干员分数吗？回复“确定”开始查询您的干员练度并计算。\n注：使用该功能将默认允许我们匿名上传您的干员练度数据（不包含任何可以识别您的个人信息）到我们的服务器来统计干员培养数据从而改进计分规则。'

        wait = await data.wait(Chain(data).text(eula))

        if not wait or ("确定" not in wait.text):
            return

        user_info: Optional[dict] = await plugin.get_user_info(token)

        if user_info is None:
            return Chain(data).text('Token 无效/失效，无法获取信息，请重新绑定。')

        character_uid = user_info['gameStatus']['uid']
        character_info: Optional[dict] = await plugin.get_character_info(token, character_uid)

        character_data = character_info['chars']
        character_map = character_info['charInfoMap']    

        # 使用新的函数来计算得分
        total_scores = 0
        total_base_scores = 0
        total_level_scores = 0
        total_specialize_scores = 0
        total_equip_scores = 0

        detail_text = ""

        score_details = []

        for character in character_data:
            char_map_data = character_map[character["charId"]]
            score_dict = calculate_score(character, char_map_data)
            
            total_scores += score_dict["total"]
            total_base_scores += score_dict["base"]
            total_level_scores += score_dict["level"]
            total_specialize_scores += score_dict["specialize"]
            total_equip_scores += score_dict["equip"]

            if score_dict["total"] != 0:
                char_detail = f'{char_map_data["name"]}: \t总分:{score_dict["total"]}\t基础:{score_dict["base"]}\t等级:{score_dict["level"]}\t专精:{score_dict["specialize"]}\t模组:{score_dict["equip"]}\t\n'
                score_details.append((score_dict["total"], char_detail))

        # 按总分从大到小排序
        score_details.sort(key=lambda x: x[0], reverse=True)

        # 拼接已排序的文本到detail_text
        detail_text = ""
        for _, detail in score_details:
            detail_text += detail

        total_score_message = (
            f'博士，您的Box总计有{len(character_data)}位干员，'
            f'总分为：{total_scores}，其中：\n'
            f'干员深度分{total_base_scores}。\n'
            f'干员等级分{total_level_scores}。\n'
            f'干员专精分{total_specialize_scores}。\n'
            f'干员模组分{total_equip_scores}。\n'
            f'计分规则更新于2023-08-07，发送“兔兔查看计分规则”查看详情。\n'
            f'该分数仅供娱乐，请不要用这个分数来评判博士呦~~'
        )

        await data.send(Chain(data,at=False).at(data.user_id).text(total_score_message))

        if "详细" in data.text:
            await data.send(Chain(data,at=False).at(data.user_id).text(f'{detail_text}'))

        # Step 2: 在upload_data之前，检查用户的data.user_id是否在字典中，以及是否过了一天
        if data.user_id not in last_upload_dates or (datetime.datetime.now() - last_upload_dates[data.user_id]).days >= 1:
            upload_data(character_data, data.user_id+"|"+character_uid )
            last_upload_dates[data.user_id] = datetime.datetime.now()  # Step 3: 如果满足条件，则执行upload_data并更新上传日期

    except Exception as e:
        log.info(f"发送用户box时出错:{str(e)}")
        return Chain(data).text('出错了，请试试联系管理员或者重新设置token。')