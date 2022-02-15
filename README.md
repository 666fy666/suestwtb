# Shanghai University Of Engineering Science 体温填报脚本
## 本地部署方法（小提示）：
（注：request文件夹里已提供谷歌浏览器安装包、谷歌浏览器驱动和VC_redist.x64安装包）

1、安装好 Python3.8环境、谷歌浏览器 和 VC_redist.x64！！

2、安装opencv，ddddocr，selenium框架，电脑win+r 运行cmd 复制输入：pip install selenium 然后回车！！以此类推，等待安装完成，可能时间较长
（1，2两步如有问题，百度即可）

3、下载谷歌驱动chrome driver（版本号一定要对应，例如你安装97.0.4692.71的谷歌浏览器，就下载4692的驱动，这四位一样就行）
   并分别解压到谷歌浏览器和python3.8的根目录！！ 

4、去login.py（右键选择edit with IDLE）里面修改自己的学校账号和密码

5、可以先进行测验运行login.py （login.py和base_64.py必须在同一文件夹里）

6、去此电脑 右键->管理->左边的“计划任务程序”->点击右边的创建基本任务，按照导引创建每天定时的任务，运行程序login.py
   需要创建两个定时任务，一个在上午，一个在下午，间隔时间都是一天
  （如果是部署在个人服务器也是同样操作）
