# 计算玩家Box深度的有趣小工具

## 使用方法

- 发送`兔兔给我打分`
- 兔兔会告知您一段警告信息，回复确定开始计算。

- 如果发送`兔兔查看计分规则`，兔兔会输出计分的规则。

![兔兔给我打分](https://raw.githubusercontent.com/hsyhhssyy/amiyabot-arknights-hsyhhssyy-player-rating/master/example.jpg)

## 计分规则    
初版因为没有收集到足够的玩家练度数据，因此打分规则暂时固定如下：

1. 只有精二的干员才算分
2. 算分规则为 干员基础分（Box深度分）+干员等级分+干员专精分+干员模组分
3. 干员基础分：4星40分，5星70分，6星100分
4. 干员等级分：每1级1分
5. 干员专精分：每个技能 专1：20分 专2：60分，专3:100分
6. 干员模组分：每个模组 1级：0分 2级：30分，3级：50分

其中1模0分的原因是鹰角目前森空岛的接口有Bug，没开的模组也会显示1级，所以插件没办法知道你开没开1级模组，总不能每个有模组的人都有分吧，因此1模改为0分

目前的打分规则代表了养成投入的资源，未来会根据干员持有率来统计强度（大家都练的干员更强，大家都专的技能更强）然后根据强度加权计算平均强度分。

## 关于数据上传

使用打分功能时，会将打分玩家的干员box上传到服务器，上传的内容仅包含box，不含玩家个人信息。使用该功能打分则默认您同意此项数据分享。

## 其他

你需要更新兔妈的森空岛插件到1.4以上版本才能使用这个插件。

如果对分数有异议，可以询问兔兔`兔兔详细给我打分`，兔兔会返回每一个干员的分数，你可以对照查看问题在哪里。

> [项目地址:Github](https://github.com/hsyhhssyy/amiyabot-arknights-hsyhhssyy-player-rating/)

> [遇到问题可以在这里反馈(Github)](https://github.com/hsyhhssyy/amiyabot-arknights-hsyhhssyy-player-rating/issues/new/)

> [如果上面的连接无法打开可以在这里反馈(Gitee)](https://gitee.com/hsyhhssyy/amiyabot-plugin-bug-report/issues/new)

> [Logo作者:Sesern老师](https://space.bilibili.com/305550122)

|  版本   | 变更  |
|  ----  | ----  |
| 1.0  | 初版登录商店 |