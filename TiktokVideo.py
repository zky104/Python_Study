import os
import requests
import time
from bs4 import BeautifulSoup


class viode_ini:
    # 初始化游标
    max_cursor = 0
    # 初始化视频数量
    video_count = 0
    # 成功下载的视频数量
    success = 0
    # 失败下载的视频数量
    error = 0

    # 初始化类型
    video = 0
    image = 0

    # 全局请求头
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36'
    }
    path = ''

    # 初始化文件夹
    def __init__(self):
        # 判断文件夹是否存在
        if not os.path.exists('video'):
            os.mkdir('video')
        if not os.path.exists('video/主页'):
            os.mkdir('video/主页')
        if not os.path.exists('video/喜欢'):
            os.mkdir('video/喜欢')
        if not os.path.exists('video/合集'):
            os.mkdir('video/合集')

    # 链接重定向
    def redirect(self, url):
        response = requests.get(url, headers=self.header)
        return response.url

    # 获取sec_uid
    @staticmethod
    def get_sec_uid(url):
        return url.split('user/')[1].split('?')[0]

    # 获取mix_id
    @staticmethod
    def get_mix_id(url):
        return url.split('detail/')[1].split('/')[0]

    # 获取用户信息
    def get_user_info(self, sec_uid):
        url = f'https://www.iesdouyin.com/web/api/v2/user/info/?sec_uid={sec_uid}'
        response = requests.get(url, headers=self.header)
        return response.json()['user_info']['nickname']

    # 特殊字符处理
    @staticmethod
    def replace(title):
        title = title.replace('\\', '')
        title = title.replace('/', '')
        title = title.replace(':', '')
        title = title.replace('*', '')
        title = title.replace('?', '')
        title = title.replace('"', '')
        title = title.replace('<', '')
        title = title.replace('>', '')
        title = title.replace('|', '')
        title = title.replace('\n', '')
        return title

    # 验证是否为视频
    @staticmethod
    def is_video(data):
        try:
            video = data['video']['download_addr']
            return True
        except KeyError:
            return False

    # 结束输出
    def end(self):
        print('=====================================================')
        print(f'* 视频总数：{self.video_count}')
        print(f'* 成功下载：{self.success}')
        print(f'* 失败下载：{self.error}')
        print('=====================================================')
        s = input('回车退出')
        exit(0)


# 视频下载
def download(ini, video, title):
    try:
        # 请求视频
        response = requests.get(video, headers=ini.header)
        # 写入视频
        with open(f'{ini.path}/{title}.mp4', 'wb') as f:
            f.write(response.content)
        # 成功下载数量
        ini.success += 1
    except Exception as e:
        log_name = ErrorLog(e)
        # 失败下载数量
        ini.error += 1
        print(title + f'下载失败，详细请查看/video/Log/{log_name}.log文件')


# 写入日志
def ErrorLog(error):
    if not os.path.exists('video/Log'):
        os.mkdir('video/Log')
    # 获取当前时间
    log_name = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    Errror = f'====================={date}=====================\n' \
             f'{error}\n' \
             f'=============================================================\n'
    # 写入错误日志
    with open(f'video/Log/{log_name}.log', 'a', encoding='utf-8') as f:
        f.write(Errror)
    return log_name


# 程序主入口
def Start():
    ini = viode_ini()
    print('=====================================================')
    print('***************** 抖音视频爬虫工具 *********************')
    print('=====================================================')
    print('1.下载用户主页视频\t\t2.下载用户喜欢视频\n3.下载视频合集\t\t4.退出程序')
    print('=====================================================')
    choice = input('请输入序号选择类型：')
    try:
        if choice == '1':
            HomeAndLike(ini, choice)
        elif choice == '2':
            HomeAndLike(ini, choice)
        elif choice == '3':
            Collection(ini)
        elif choice == '4':
            exit()
        else:
            print('输入错误，请重新输入！')
            Start()

    except Exception as e:
        log_name = ErrorLog(e)
        input(f'程序出现错误，错误日志已保存至 video/Log 文件夹，联系作者请提交log_name.log文件！')


# 主页And喜欢
def HomeAndLike(ini, Type):
    # 获取真实链接
    url = ini.redirect(input('请输入用户主页链接：'))
    # 获取sec_uid
    sec_uid = ini.get_sec_uid(url)
    # 获取用户昵称
    nickname = ini.get_user_info(sec_uid)
    nickname = ini.replace(nickname)
    # 下载路径
    if Type == '1':
        ini.path = f'video/主页/{nickname}'
    elif Type == '2':
        ini.path = f'video/喜欢/{nickname}'
    # 创建文件夹
    if not os.path.exists(ini.path):
        os.makedirs(ini.path)
    print('*****************   开始下载视频  *********************')
    # 开始执行任务
    while True:
        # 接口设置
        if Type == '1':
            url = f'https://m.douyin.com/web/api/v2/aweme/post/?reflow_source=reflow_page&sec_uid={sec_uid}&count=21&max_cursor={ini.max_cursor}'
        elif Type == '2':
            url = f'https://m.douyin.com/web/api/v2/aweme/like/?reflow_source=reflow_page&sec_uid={sec_uid}&count=21&max_cursor={ini.max_cursor}'
        data = requests.get(url, headers=ini.header).json()
        # 获取视频列表
        aweme_list = data['aweme_list']
        # 读取视频
        for aweme in aweme_list:
            # 更新视频数量
            ini.video_count += 1
            # 视频标题
            title = f'【{ini.video_count}】 {ini.replace(aweme["desc"])}'
            # 视频链接
            try:
                video_url = aweme['video']['play_addr']['url_list'][0]
            except KeyError:
                ini.error += 1
                print('下载失败: ' + title)
                print('原因: 视频链接获取失败，可能是因为视频已被删除！')
                continue
            # 验证视频是否存在
            if ini.is_video(aweme):
                print('正在下载：' + title)
                # 下载视频
                download(ini, video_url, title)
            else:
                # 下载失败
                ini.error += 1
                print('下载失败：' + title)
                print('失败原因：图文视频，跳过下载')
        # 判断是否还有下一页
        if data['has_more']:
            # 更新max_cursor
            ini.max_cursor = data['max_cursor']
        else:
            print('*****************   视频下载结束  *********************')
            ini.end()


# 下载视频合集
def Collection(ini):
    # 获取真实链接
    url = ini.redirect(input('请输入视频合集链接：'))
    mix_id = url.split('detail/')[1].split('/')[0]
    # 获取合集信息
    url = f'https://www.iesdouyin.com/share/mix/detail/{mix_id}'
    response = requests.get(url, headers=ini.header)
    # 获取合集信息
    soup = BeautifulSoup(response.text, 'html.parser')
    # 获取用户昵称
    nickname = ini.replace(soup.select('span[class="font-small color-yellow mr-10"]')[0].text).replace('@', '')
    # 获取合集名称
    collection_name = ini.replace(soup.select('span[class="mix-info-name-text"]')[0].text)
    # 下载路径
    ini.path = f'video/合集/{nickname}/{collection_name}'
    # 创建文件夹
    if not os.path.exists('video/合集/{nickname}'):
        os.makedirs('video/合集/{nickname}')
    if not os.path.exists(ini.path):
        os.makedirs(ini.path)
    print('*****************   开始下载视频  *********************')
    # 开始执行任务
    while True:
        url = f'https://www.iesdouyin.com/web/api/mix/item/list/?reflow_source=reflow_page&mix_id={mix_id}&count=10&cursor={ini.max_cursor}'
        data = requests.get(url, headers=ini.header).json()
        # 获取视频列表数据
        aweme_list = data['aweme_list']
        for aweme in aweme_list:
            # 更新视频总数
            ini.video_count += 1
            # 视频标题
            title = f'【第{ini.video_count}集】 {ini.replace(aweme["desc"])}'
            # 视频链接
            try:
                video_url = aweme['video']['play_addr']['url_list'][0]
            except KeyError:
                ini.error += 1
                print('下载失败: ' + title)
                print('原因: 视频链接获取失败，可能是因为视频已被删除！')
                continue
            # 验证视频是否存在
            if ini.is_video(aweme):
                print('正在下载：' + title)
                # 下载视频
                download(ini, video_url, title)
            else:
                # 下载失败
                ini.error += 1
                print('下载失败：' + title)
                print('失败原因：图文视频，跳过下载')
        # 判断是否还有下一页
        if data['has_more']:
            # 更新游标
            ini.max_cursor = data['cursor']
        else:
            print('*****************   视频下载结束  *********************')
            ini.end()


if __name__ == '__main__':
    Start()
