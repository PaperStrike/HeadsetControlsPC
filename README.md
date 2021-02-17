[![Banner](https://raw.githubusercontent.com/PaperStrike/picture-playground/master/img/HeadsetControlsPC-banner.svg)](#headset-controls)

# Headset Controls
为 PC 提供 3.5mm 耳机线控支持。

Python >= 3.6

### 目录
* [介绍](#介绍)
* [安装](#安装)
* [使用](#使用)
  * [可选参数](#可选参数)
  * [按键](#按键)
* [注意哦](#注意哦)
  * [抓取日志](#抓取日志)
* [捐赠](#捐赠)
* [许可](#许可)

## 介绍
3.5mm TRRS 有线耳机的麦克风与按钮并联，按钮按下时麦克风被短接，安卓设备通过检测电压差可以知道按下的按钮。

![Reference Headset Circuits](https://camo.githubusercontent.com/6b36b17c0f21a709fb67a704f21042f656e43eecd154ac10a84807315432f97f/687474703a2f2f7777772e726f6c6967686574656e2e6e6f2f696d616765732f686561647365742d63697263756974322e706e67)

多数 PC 设备无法获知电压差，但短接对麦克风两个声道产生的影响有些不同。这里使用 [Soundcard Oscilloscope](https://www.zeitnitz.eu/scms/scope) 的 x-y graph 功能对比最近 1s 内两个声道的信号幅度进行演示。为了更明显，我们只检视 0.1 范围内的 x 轴和 y 轴：

这是普通声音在极端情况下的声道对比图：

![极端声音的声道对比图](https://user-images.githubusercontent.com/22674396/107115380-42887b80-68a7-11eb-8651-ea599887e387.png)

这是 A 按钮（暂停开始键）的声道对比图：

![A 按钮的声道对比图](https://user-images.githubusercontent.com/22674396/107115426-a0b55e80-68a7-11eb-8410-149f866bd5b5.png)

其他情况的声道对比有兴趣的同志可以自己尝试。本项目正是在不同情况的不同声道对比中找不同，来尝试辨别不同按钮的点击、长按事件。

因此，运行时需要使用麦克风。

## 安装
以下两种方式都需要联网，会自动安装依赖包 `keyboard`，`numpy` 和 `sounddevice` 。

### PyPI
通过 PyPI 安装：
```commandline
pip install trrsheadset
```

### Clone
或者， 从 [这里](https://github.com/PaperStrike/HeadsetControlsPC/archive/main.zip) 下载本仓库的压缩包，将他解压到一个记得住位置的地方，作为安装文件夹。

在安装文件夹中运行：
```commandline
pip install .
```

## 使用
插入耳机后，在命令行中使用 Python 启动 `trrsheadset` 即可:

```commandline
python -m trrsheadset [参数]
```

关闭通常使用两种方式，一种是直接关闭命令行窗口，一种是按下并松开 `ctrl+shift+h` 后在 *1s* 内按下 `e` 键。

选用 `pythonw` 启动可在命令行关闭后保持运行，可通过任务管理器 `Python 3.x (Windowed)` 或上述热键关闭。

重插耳机需要重新启动。

### 可选参数
`-l` or `--log` 将运行日志保存至文件

`--no-hotkey` 禁用键盘快捷键

`-h` or `--help` 输出此列表后退出

### 按键
耳机按键映射和键盘快捷键响应。

#### 耳机
按键   | 短按            | 长按
:-----:|:-------------:|:--------------:
 A    | 继续 / 暂停      | 继续 / 暂停
 B    | 音量+           | 下一首
 C    | 音量-           | 上一首
 D    | 继续 / 暂停      | 继续 / 暂停

#### 键盘
基础快捷键： `ctrl+shift+h`

在基础快捷键触发后 *1s* 内按下以下按键可以触发相应操作：

`p` 暂停或继续

`e` 退出

## 注意哦
* 不要按得太快，招架不住。
* 技术问题欢迎提 issue，其他问题请进入 [讨论区（Discussions）](https://github.com/PaperStrike/HeadsetControlsPC/discussions) 进行交流。
* 如果放久后按钮辨别老错，可能是太久不放音乐了电压不高（？存疑，欢迎讨论）  
* 灵感源于：[roligheten/AndroidMediaControlsWindows](https://github.com/roligheten/AndroidMediaControlsWindows) 👍

### 抓取日志
添加参数 `-l` 或 `--log` 启动可将运行时日志保存到运行时文件夹的 `debug.log.1` 和 `debug.log` 日志文件中。日志文件对定位 BUG 非常有帮助。

```commandline
python run.py -l
```
## 捐赠
如果你足够开心 🌹

<img alt="支付宝收款码" src="https://raw.githubusercontent.com/PaperStrike/picture-playground/master/img/Donate-Alipay.png" width="148">  <img alt="微信收款码" src="https://raw.githubusercontent.com/PaperStrike/picture-playground/master/img/Donate-WeChat.png" width="148">

## 许可
[GPL-3.0 License](https://github.com/PaperStrike/HeadsetControlsPC/blob/main/LICENSE)
