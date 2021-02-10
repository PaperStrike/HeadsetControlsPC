# PC 上的有线耳机线控
为 PC 提供 3.5mm 耳机线控支持。

目前仅支持 Windows 平台，Python 3.x。

### 目录
* [介绍](#介绍)
* [安装](#安装)
* [使用](#使用)
* [注意哦](#注意哦)
* [许可](#许可)

## 介绍
3.5mm 有线耳机的麦克风与按钮并联，按钮按下时麦克风被短接，安卓设备通过检测电压差可以知道按下的按钮。

![Reference Headset Circuits](https://camo.githubusercontent.com/6b36b17c0f21a709fb67a704f21042f656e43eecd154ac10a84807315432f97f/687474703a2f2f7777772e726f6c6967686574656e2e6e6f2f696d616765732f686561647365742d63697263756974322e706e67)

Windows 平台无法获知电压差，但短接对麦克风两个声道产生的影响有些不同。这里使用 [Soundcard Oscilloscope](https://www.zeitnitz.eu/scms/scope) 的 x-y graph 功能对比最近 1s 内两个声道的信号幅度进行演示。为了更明显，我们只检视 0.1 范围内的 x 轴和 y 轴：

这是普通声音在极端情况下的声道对比图：

![极端声音的声道对比图](https://user-images.githubusercontent.com/22674396/107115380-42887b80-68a7-11eb-8651-ea599887e387.png)

这是 A 按钮（暂停开始键）的声道对比图：

![A 按钮的声道对比图](https://user-images.githubusercontent.com/22674396/107115426-a0b55e80-68a7-11eb-8410-149f866bd5b5.png)

其他情况的声道对比有兴趣的同志可以自己尝试。本项目正是在不同情况的不同声道对比中找不同，来尝试辨别不同按钮的点击、长按事件。

## 安装
确保 Python 中有 `pywin32`，`numpy` 和 `sounddevice` 软件包。不确定或没有的话，可通过下面的命令来检查或安装：

```
pip install pywin32 numpy sounddevice
```

从 [这里](https://github.com/PaperStrike/HeadsetControlsPC/archive/main.zip) 下载本仓库的压缩包，并将他解压到一个记得住位置的地方，作为安装文件夹。

## 使用
插入耳机后，在安装文件夹中使用 Python 运行 `run.py` 即可:

```
python run.py
```

拔耳机后重插需要重跑。（日后改善）

## 注意哦
* 不要按得太快，招架不住。
* 技术问题欢迎提 issue，其他问题请进入 [Discussions](https://github.com/PaperStrike/HeadsetControlsPC/discussions) 进行交流。
* 跑本软件后再插耳机无效。
* 项目精确度还不算高。

灵感源于：[roligheten/AndroidMediaControlsWindows](https://github.com/roligheten/AndroidMediaControlsWindows) 👍

## 许可
[GPL-3.0 License](https://github.com/PaperStrike/HeadsetControlsPC/blob/master/LICENSE)
