[![Banner](https://res.sliphua.work/img/HeadsetControlsPC-banner.svg)](#readme)

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
通过分析耳机上不同按钮在不同时刻对具有 TRRS 接口 PC 设备的麦克风两个声道造成的不同影响来提供耳机线控支持。

更具体的实现方式可以转到这篇 [博文](https://sliphua.work/headset-controls-on-pc/) 阅读。

## 安装
以下两种方式都需要联网，会自动安装依赖包 `keyboard`，`numpy` 和 `sounddevice` 。

### PyPI
通过 [PyPI](https://pypi.org/project/trrsheadset/) 安装：
```commandline
pip install trrsheadset
```

### Clone

或者， 从 [这里](https://github.com/PaperStrike/HeadsetControlsPC/archive/main.zip) 下载在 GitHub 仓库中的压缩包，解压到一个记得住位置的地方。

> 这种安装方式目前有一个 bug（[PIP doesn't read setup.cfg in UTF-8, which causes UnicodeDecodeError · Issue #8931 · pypa/pip](https://github.com/pypa/pip/issues/8931)），安装前需要根据你使用的命令行环境设置环境变量 `PYTHONUTF8=1`：
>
> - PowerShell: `$env:PYTHONUTF8=1`
> - Shell: `export PYTHONUTF8=1`
> - CMD: `set PYTHONUTF8=1`

定位到解压文件夹中运行：

```powershell
pip install .
```

然后，就可以把解压文件夹删掉。

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
* 感谢 [Christian Barth Roligheten](https://github.com/roligheten) 大哥 👍

### 抓取日志
添加参数 `-l` 或 `--log` 启动可将运行时日志保存到**运行时文件夹**的 `debug.log.1` 和 `debug.log` 日志文件中。日志文件对定位 BUG 非常有帮助。

```commandline
python run.py -l
```

## 捐赠
如果你足够开心 🌹

![支付宝收款码](https://res.sliphua.work/img/Donate-Alipay.png?x-oss-process=image/resize,w_148) ![微信收款码](https://res.sliphua.work/img/Donate-WeChat.png?x-oss-process=image/resize,w_148)

## 许可
[GPL-3.0 License](https://github.com/PaperStrike/HeadsetControlsPC/blob/main/LICENSE)
