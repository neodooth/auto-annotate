# 标注网站

分为website和downloader两部分

website作为网站前端和数据存储

downloader作为下载器，从website接收要下载的名单，下载图片、识别出人脸框，然后发回给website

## website部分

images里存放图片

* unsubmitted里放没发给downloader的
* unreceived里放发送给downloader但还没收到发回的图片的
* unannotated里放收到downloader发回的图片，但用户还没标注的
* annotated里放用户标注完的

提交的人的id的设定为，unsubmitted/unreceived/unannotated作为整体，annotated单独生成id

在各文件夹里，第一级文件夹是用户名，第二级是这个用户标注、没标注过的人的各自的文件夹

## downlaoder部分

* undownloaded存放收到但还没下载的人
* downloading存放正在下载的
* downloaded：已经下载了的
* detected存放已经检测完，可以发回website的

把文件夹传回到website后就删除detected里对应文件夹

## 如何添加用户

在unsubmitted里建文件夹，文件夹名就是用户名。密码是config.PWD_PREFIX+用户名