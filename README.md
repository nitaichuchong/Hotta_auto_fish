**这是一个可以自动进行幻塔中钓鱼小游戏的自动脚本，具体的使用手册就不写了，主要介绍这个项目有什么，详细的有点懒得写在 readme 里**

---



**安装依赖**的 requirements.txt 中，由于 paddle ocr 的特殊性，我保留但注释掉了安装命令，请一定要在 pip install -r requirements.txt 后打开该文件查看被注释掉的命令并执行

---



**主程序入口**：src/main.py，运行这个文件就是主程序，注意要用管理员身份运行，包括后面打包后的程序，也需要用管理员运行，否则是无法在幻塔中控制键鼠的，这点一定要注意。

---



src 下的其它文件，分别对应各自的功能，供其它函数、类等调用，但需要注意的是，收杆并再次抛竿的操作并未写在 fish_auto 内，而是在主 UI 内

---



**配置文件**：config/config，所有的常量等都被写到了该配置文件中，想要做调整一定要记得查看，并且通过 config/__init__向外暴露

---



**test 下有三类测试**：打包测试、检测功能测试、ocr 功能测试，注意看名称区分，在对应的功能后加 _test 后缀，唯一需要注意的是检测功能测试的启动在 detect_test_run，这是最初为了规避循环依赖做的拆分

---



**UI** 目录下实际上不是纯 UI，有大量执行逻辑，tk 库不像 PyQT 一样方便做进一步拆分，在修改主程序逻辑时一定要注意

---



**utils** 下有两个方便的功能：

    build 可以将主程序打包为可执行的 exe，结果在 build/dist 下，要转移打包内容，是把 dist 目录下的那个文件夹一起转移，而不是 dist 目录，build 里面的内容懂 Pyinstall 的可以做修改，但是一定要小心，涉及到 paddle ocr 相关的打包内容，请参考官方文档，这里附上两处链接：



    [https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/deployment/packaging.md]()
    [https://github.com/PaddlePaddle/PaddleOCR/issues/15918#issuecomment-3023825346]()



    get_mouse_coordinate 可以实时获取鼠标位置，方便调整 config 配置中关于区域的设置，当然要注意，区域使用的格式要符合 PIL 格式，以及后续的跟 opencv相关的操作

---
