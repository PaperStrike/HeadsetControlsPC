[![Banner](https://res.sliphua.work/img/HeadsetControlsPC-banner.svg)](#headset-controls)

# Headset Controls
为 PC 提供 3.5mm 耳机线控支持。

Python >= 3.6

**项目目前严重缺乏测试，不同设备、不同耳机很可能有不同表现。**

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
TRRS 接口的有线耳机的麦克风与按钮并联，按钮按下时麦克风被短接，安卓设备通过检测电压差可以知道按下的按钮。

![Reference Headset Circuits](https://res.sliphua.work/img/headset-circuit.png)

多数 PC 设备无法获知电压差，但短接对麦克风两个声道产生的影响有规律可循。这里使用 [`plot_input.py`](https://gist.github.com/PaperStrike/5f5b75edf7f175064699d3c35208c751) 实时输出麦克风**声道一**的波形（橙线 `Channel 1`）和**两声道差值**（蓝线 `diff`，`Channel 2` - `Channel 1`）的波形进行演示。

横轴表示时间，单位为毫秒（ms），纵轴表示声音的变化。
**数据在不同设备上可能有所不同**，另外，演示中排除了轻按的情况。

无声音时，两条波均呈现为一条直线。而极端噪声环境下，`Channel 1` 震动剧烈，`diff` 保持稳定：

![极端噪声波形图](https://res.sliphua.work/img/HeadsetControlsPC-noise.png)

短按按钮时，处于安静环境（0-1000ms）和处于噪声环境（1300-4000ms）的两条波呈现的变化中，有规律的至少有：

* `diff` 在按下瞬间增长至 0.06(±0.05) 并持续 40(±30)ms，在松开瞬间下降。
* `Channel 1` 在按下瞬间，下降并保持在 -0.6 以下 100(±30)ms，经 30(±20)ms 增长至 0.45 以上并保持 230(±60)ms，经 30(±20)ms 下降至 -0.40(±5) 以下。

![短按波形图](https://res.sliphua.work/img/HeadsetControlsPC-click.png)

短按（0-800ms）和长按（850-2400ms）时，两条波在上述规律基础上又呈现出了不同变化：

* `diff` 在长按过程中在 -0.17-0.17 范围内随机波动，在长按松开瞬间再次拉升，后下降，详细见图，不再赘述。
* `Channel 1` 在长按过程中保持在 -0.30(±5) 以上，在长按松开瞬间再次拉升，后下降，详细见图。

![短按和长按波形图](https://res.sliphua.work/img/HeadsetControlsPC-long-press.png)

放大到纵轴 0.1 范围内，观察 `diff` 的变化。注意到不同按钮的按下瞬间 `diff` 呈的波动幅度有所不同：

* 按钮 A 按下瞬间（700-900ms）`diff` 波动峰值在 0.075 以上，按钮 B（1700-1900ms）为 0.025-0.075，按钮 C（3000-3200ms）为 0.016-0.025。

![不同按钮短按波形图](https://res.sliphua.work/img/HeadsetControlsPC-buttons.png)

其他情况的声道对比有兴趣的同志可以自己下载 [`plot_input.py`](https://gist.github.com/PaperStrike/5f5b75edf7f175064699d3c35208c751) 尝试。本项目正是在不同情况的不同声道对比中找不同，来尝试辨别不同按钮的点击、长按事件。

因此，运行时需要使用麦克风。

## 安装
以下两种方式都需要联网，会自动安装依赖包 `keyboard`，`numpy` 和 `sounddevice` 。

### PyPI
通过 [PyPI](https://pypi.org/project/trrsheadset/) 安装：
```commandline
pip install trrsheadset
```

### Clone
或者， 从 [这里](https://github.com/PaperStrike/HeadsetControlsPC/archive/main.zip) 下载本仓库的压缩包，解压到一个记得住位置的地方，作为安装文件夹。

在安装文件夹中运行：
```commandline
pip install .
```

## 使用
插入耳机后，在命令行中使用 Python 启动 `trrsheadset` 即可:

```commandline
python -m trrsheadset [参数]
```

>   * 关闭可以使用两种方式，一种是直接关闭命令行，一种是按下 `ctrl+break` 快捷键强制退出。
>   * 选用 `pythonw` 启动可在命令行关闭后保持运行，可在任务管理器中找到 `Python 3.x (Windowed)` 关闭。

重插耳机需要重新启动。

### 可选参数
`-l` or `--log` 将运行日志保存至文件

`--use-hotkey` 开启[键盘快捷键](#键盘)

`-h` or `--help` 输出此列表后退出

### 按键
耳机按键映射 & 键盘快捷键响应。基于 Python 库 [keyboard](https://github.com/boppreh/keyboard) 。

#### 耳机
 按键  | 短按            | 长按          | 双击
:----:|:--------------:|:-------------:|:-----------:
 A    | 继续 / 暂停      | 继续 / 暂停    | 静音
 B    | 音量+           | 下一首         | /
 C    | 音量-           | 上一首         | /
 D    | /              | /             | /

**双击操作处于早期开发阶段**

#### 键盘
*需在启动时使用 `--use-hotkey` 参数。*

基础快捷键 `ctrl+shift+h` ，在基础快捷键触发后 *1s* 内按下以下按键可以触发相应操作：

`p` 暂停或继续

`e` 退出

> ！部分设备在开启上述快捷键后，检测不到右 shift、右 ctrl 的释放动作，此时可以按击键盘左边对应按键恢复。

## 注意哦
* 不要按得太快，招架不住。
* 技术问题欢迎提 issue，其他问题请进入 [讨论区（Discussions）](https://github.com/PaperStrike/HeadsetControlsPC/discussions) 进行交流。
* 如果放久后按钮辨别老错，可能是太久不放音乐了电压不高（？存疑，欢迎讨论）  
* 感谢 [roligheten/AndroidMediaControlsWindows](https://github.com/roligheten/AndroidMediaControlsWindows) 👍

### 抓取日志
添加参数 `-l` 或 `--log` 启动可将运行时日志保存到**运行时文件夹**的 `debug.log.1` 和 `debug.log` 日志文件中。日志文件对定位 BUG 非常有帮助。

```commandline
python run.py -l
```

## 捐赠
如果你足够开心 🌹

<img alt="支付宝收款码" src="https://res.sliphua.work/img/Donate-Alipay.png" width="148">  <img alt="微信收款码" src="https://res.sliphua.work/img/Donate-WeChat.png" width="148">

## 许可
[GPL-3.0 License](https://github.com/PaperStrike/HeadsetControlsPC/blob/main/LICENSE)
