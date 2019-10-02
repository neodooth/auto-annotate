# Face image annotation website

## Screenshots

* List of annotated people

![Alt text](/screenshots-en/screenshot1.png?raw=true "Broken link")

* Images/Information of an annotated person

![Alt text](/screenshots-en/screenshot2.png?raw=true "Broken link")

* Interface for submitting names of people for annotating

![Alt text](/screenshots-en/screenshot3.png?raw=true "Broken link")

* The actual annotating interface in which valid images should be selected

![Alt text](/screenshots-en/screenshot4.png?raw=true "Broken link")

## Modules

The website consists of two modules, each in a folder:

- website: this module provides the frontend of the website (the annotation UI) and is responsible for storing the images
- downloader: this module receives names of people for downloading images from the website module, and then downloads images, launches the face detector against images, crops faces from images, and finally send them all back to the website module

## The website module

Images/People have 4 states in this module, each stored in a folder:

- unsubmitted: people whose names are submitted by the user but not transmitted to the downloader by the website module
- unreceived: people whose names have been submitted to the downloader module and is waiting to be downloaded
- unannotated: images of people received from the downloader, but are not annotated by the user
- annotated: images that are annotated and ready for use

## The downloader module

- undownloaded: people that are received from the website but are not being downloaded
- downloading: people whose images are being downloaded; may have incomplete images and can be paused/resumed/restarted
- downloaded: people whose images are fully downloaded but not face-detected
- detected: people whose images are face-detected and can be sent back to the website for annotating

After all images of a person are transmitted to the website module, their images will be deleted

# 标注网站

## 截图

![Alt text](/screenshots/screenshot1.png?raw=true "Broken link")
![Alt text](/screenshots/screenshot2.png?raw=true "Broken link")
![Alt text](/screenshots/screenshot3.png?raw=true "Broken link")
![Alt text](/screenshots/screenshot4.png?raw=true "Broken link")

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
