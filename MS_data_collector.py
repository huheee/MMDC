#-*- coding:utf-8 -*-
import errno
import os
import shutil

# from selenium import webdriver
from bs4 import BeautifulSoup
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import urllib.request
import requests
from urllib.request import urlretrieve
from time import sleep
import re
import datetime
import time
import multiprocessing
from multiprocessing import Process, Pool, freeze_support
from functools import partial

import sys
import pickle


# from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget
# from PyQt5.QtCore import QCoreApplication

MS_DOMAIN = 'https://mangashow.me'
# MS_DOMAIN2 = 'https://mangashow2.me'
# MS_DOMAIN2 = 'https://mangashow3.me'
# MS_DOMAIN2 = 'https://188.214.128.5'
# MS_DOMAIN2 = 'https://mangashow5.me'
MS_DOMAIN2 = 'https://manamoa3.net'
ABS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER_NAME = "/완결"


##################################################################
# MangaShowMe 완결 화 채집 툴
#
# 2019.01.28 알파버전 배포
# 2019.02.28 도메인 주소 변경으로 기본 도메인 수정
# 로컬에 완결 페이지 번호랑 만화 이름 또는 순서 저장해서 쓰면됨
#
#
#
#
##################################################################


# 각 화 별 url 리스트 형태로 저장
def set_list(slot_list):
    idx_list = 0
    list_c = []
    for slot_num in slot_list:
        try:
            check_slot = slot_num.get('href')
            # if check_slot is not None and check_slot.find("wr_id") != -1:
            if check_slot is not None and check_slot.find("manga") != -1 and check_slot.find("wr_id") != -1:
                check_slot = check_slot.replace(MS_DOMAIN, MS_DOMAIN2)
                if MS_DOMAIN2 not in check_slot:
                    check_slot = MS_DOMAIN2 + check_slot
                list_c.append(check_slot)
        except UnicodeEncodeError:
            print("Error : %d" % idx_list)
        except IndexError:
            print("이 a 태그 아님")
        finally:
            idx_list += 1

    # sleep(0.2)
    # print(list_c)
    return list_c


# 각 화를 기준으로 이미지 저장
def save_image(c_name, i_list):
    idx = 0
    c_name = ABS_FILE_PATH + c_name
    for img in i_list:

        try:
            # check = img.get('class')
            # img_src = img.get('src')
            # if check != None and check.pop(0).find("page-") != -1:
            com_file = c_name + "/" + str(idx) + ".jpg"

            if not os.path.isfile(com_file):
                r = requests.get(img, allow_redirects=True)
                open(com_file, 'wb').write(r.content)

        except UnicodeEncodeError:
            print("Error : %d" % idx)
        except IndexError:
            print("이 a 태그 아님")
        finally:
            idx += 1


# 폴더 생성 메소드. name에 경로 넣어서 생성
def create_folder(name):
    name = ABS_FILE_PATH + name
    try:
        if not (os.path.isdir(name)):
            os.makedirs(os.path.join(name))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
    except StopIteration as e:
        # print("create_folder stoplteration : "+e)
        pass

# 폴더 삭제 메소드. name에 경로 넣어서 삭제(하위 파일 모두 삭제)
def delete_folder(name):
    name = ABS_FILE_PATH + name
    try:
        shutil.rmtree(name)
        print("기존 하위 폴더 삭제("+name+")")
    except OSError as e:
        if e.errno == 2:
            # 파일이나 디렉토리가 없음!
            print
            'No such file or directory to remove'
            pass
        else:
            raise
    except StopIteration as e:
        # print("delete_folder stoplteration : "+e)
        pass


def chap_process_list(pchapUrl, pchapNum, pmName):
    # driver.get(chap)
    # html = driver.page_source  # 페이지의 elements 모두 가져오기
    req_chap = requests.get(pchapUrl)
    html_chap = req_chap.text  # 페이지의 elements 모두 가져오기

    soup = BeautifulSoup(html_chap, 'html.parser')  # BeautifulSoup 사용하기
    # img_Cname = re.compile('page*')  # 이미지 태그 중 클래스가 'page'로 시작하는 텍스트 정규식
    # img_list = soup.find_all('img', {'class': {img_Cname}}) # 이미지 태그 중 클래스가 'pageiu'로 시작하는거 다 긁어옴
    html_script = soup.select('script')
    script_str = str(html_script)
    img_Cname = re.compile(r"https:(?:[^>\"']+).jpg")
    # (?<=img_list = \[).*\"
    # img_Cname = re.compile(r"http:([^>\"']+).jpg")

    img_list = img_Cname.findall(script_str)

    if len(img_list) == 0:
        img_Cname = re.compile(r"http:(?:[^>\"']+).jpg")
        img_list = img_Cname.findall(script_str)

    for re_num, result in enumerate(img_list):
        img_list[re_num] = str(result).replace("\\", '')

    # img_list = soup.find_all('script')  # 이미지 태그 중 클래스가 'page'로 시작하는거 다 긁어옴
    chap_name = pmName + "/" + str(pchapNum)

    create_folder(chap_name)
    check_fname = ABS_FILE_PATH + chap_name
    print(check_fname)

    # print("next   "+os.walk(check_fname).__next__()[1])
    # print("len    "+len(img_list))
    # if os.walk(check_fname).__next__()[1] == len(img_list):
    # 	continue

    save_image(chap_name, img_list)
    # print("*******************************************")
    # print("proc save list by - " + str(os.getpid()))
    # print("*******************************************")



def main():
    # setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    # options = webdriver.ChromeOptions()
    # options.add_argument('--ignore-certificate-errors')

    # headless 형태로 진행
    # options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument('window-size=1920x1080')
    # #options.add_argument("disable-gpu")
    # driver = webdriver.Chrome('chromedriver', chrome_options=options)

    # 브라우저 띄운 형태로 진행
    # driver = webdriver.Chrome('./chromedriver', chrome_options=options)

    # https://188.214.128.5
    # driver.implicitly_wait(6) # 암묵적으로 웹 자원을 (최대) 3초 기다리기
    # MS_URL = ['https://mangashow.me/bbs/page.php?hid=manga_list&page=', '0', '&sfl=2&stx=7']

    MS_URL = [MS_DOMAIN2+'/bbs/page.php?hid=manga_list&page=', '0', '&sfl=2&stx=7']

    # 2019.03.13 세이브포인트 제작
    save_path = ABS_FILE_PATH + "/save.pickle"
    if os.path.isfile(save_path):
        with open(save_path, 'rb') as f:
            i = pickle.load(f)
            print("체크포인트 로딩완료. - "+str(i)+" 페이지")
    else:
        i = -1

    while True:

        i += 1
        MS_URL[1] = str(i)

        try:
            # driver.get(MS_URL[0]+MS_URL[1]+MS_URL[2])  # URL로 이동하기
            req = requests.get(MS_URL[0]+MS_URL[1]+MS_URL[2])  # URL로 이동하기
            # sleep(5.5)
        except IOError as e:
            print("프로그램종료 : 모든 항목 완료. ({0}): {1}".format(e.errno, e.strerror))
            if i != 0:
                os.remove(save_path)
            break

        # html = driver.page_source  # 페이지의 elements 모두 가져오기
        html = req.text  # 페이지의 elements 모두 가져오기
        soup = BeautifulSoup(html, 'html.parser')  # BeautifulSoup 사용하기
        MS_list = soup.find_all('a', {'class': 'ellipsis'})  # 완결 항목의 각 만화 URL

        MS_names = soup.find_all('div', {'class': 'manga-subject'}) # 만화 이름
        tags = soup.find_all('div', {'class': 'tags'})  # 만화의 장르 저장
        # create_folder(SAVE_FOLDER_NAME) #'완결' 폴더 생성. 하위 디렉토리 경로로 생성하면 상위는 자동으로 생성됨
        tags_num = 0
        list_m = []  # 만화 url 담아두는 리스트
        list_m_names = [] # 만화 이름 담아두는 리스트
        list_m_tags = []  # 태그 담아두는 리스트
        idx = 0

        for s in MS_list:
            try:
                prop = s.get('class')
                # print(prop)
                if prop is not None and prop[0] == "ellipsis":
                    url = MS_DOMAIN2 + s.get('href')
                    man_name = MS_names[tags_num].find('a').text
                    man_name = man_name.strip()

                    t_name = tags[tags_num].find('a').text
                    if t_name == "":
                        t_name = 'etc'

                    # url_encode = urlretrieve(urllib.parse.quote(url.encode('utf8'), '/:'))
                    # query = parse.parse_qs(url.query)
                    # list_m.append(url_encode) ##

                    # print(url)
                    list_m.append(url)
                    list_m_names.append(man_name)
                    list_m_tags.append(t_name)
                    tags_num += 1
            except UnicodeEncodeError:
                print("Errror : %d" % idx)
            except IndexError:
                print("이 a 태그 아님")
            finally:
                idx += 1

        # 폴더 이름 끝에 공백 들어간 경우 경로를 찾지 못해 파일 제대로 생성되지 않던 상황 테스트용
        # list_m = ["https://mangashow3.me/bbs/page.php?hid=manga_detail&manga_name=오늘 밤은 당신에게 굶주려 있어♥ "]
        # list_m_tags = ["BL"]

        print("#############################################################################################")
        # print(str(multiprocessing.cpu_count()))
        list_chap = []  # 만화의 챕터 별로 URL 저장하는 리스트
        for num, m_url in enumerate(list_m):

            m_name = SAVE_FOLDER_NAME + "/" + list_m_tags[num] + "/" + list_m_names[num]
            m_name = m_name.strip()

            # m_name = re.sub('[=+,#^$.@*\"※~&%♥☆★♡ㆍ…》]', '', m_name)
            # 폴더 이름 끝에 공백 들어간 경우 경로를 찾지 못해 파일 제대로 생성되지 않던 상황 테스트용
            # if "오늘 밤은 당신에게 굶주려 있어" in m_name :
            #     print("********************************")
            #     print(m_url)
            #     open(ABS_FILE_PATH+m_name+".txt", 'w').write(m_url)
            #     print("********************************")

            # driver.get(m_url)
            # html = driver.page_source # 페이지의 elements 모두 가져오기
            req_list = requests.get(m_url)
            html = req_list.text # 페이지의 elements 모두 가져오기
            soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup 사용하기
            # slot = soup.find_all('div',{'class':'slot'}) # ellipsis
            slot = soup.find_all('a')

            # create_folder(m_name) #상위 디렉토리는 하위 디렉토리 생성시 자동으로 생성됨
            list_chap = set_list(slot)  # 챕터 URL 리스트 저장

            chap_num = len(list_chap)  # 챕터 갯수 저장
            chk_path = ABS_FILE_PATH + m_name

            # 완결만 적용되도록 나중에 수정 예정
            try:
                # print(chk_path)
                if os.path.isdir(chk_path):
                    cur_folder = next(os.walk(chk_path))[1]
                    cur_folder_num = len(cur_folder)
                    if chap_num < cur_folder_num:
                        delete_folder(m_name) # 모든 폴더 생성 메소드는 메소드 안에서 절대 경로 붙이기 때문에 상대
                    # 개별로 지우기 안씀
                    # for idx in range(chap_num, cur_folder_num):
                    # 	d_name = chk_path + "/" + cur_folder[idx]
                    # 	delete_folder(d_name)
            except OSError as e:
                if e.errno == 2:
                    # 파일이나 디렉토리가 없음!
                    pass
                else:
                    raise
            except StopIteration as e:
                print(e)
                pass

            print("제목 : " + list_m_names[num] + ", 총 " + str(chap_num) + " 권(화)")
            s = datetime.datetime.now()
            print(s)

            procs = []
            startTime = time.time()
            for c_num, chap in enumerate(list_chap):
                cpl_num = chap_num - c_num
                # chap_process_list(chap, cpl_num, m_name)
                proc = Process(target=chap_process_list, args=(chap, cpl_num, m_name,), daemon=True)  # 멀티프로세싱 준비 # 20190220 수정 daemon 확인해봐야됨
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()

                # pool
                # p = Pool(multiprocessing.cpu_count())
                #
                # func = partial(chap_process_list, chap, cpl_num)
                # p.map(func, m_name)
                # p.close()
                # p.join()
            print("완료 - "+str("{0:.2f}".format(time.time() - startTime))+"초")
            print("-------------------------------------------------------------")
            sleep(2)

        with open(save_path, 'wb') as f:
                pickle.dump(i, f, pickle.HIGHEST_PROTOCOL)
                print("체크포인트 저장 - " + str(i))


if __name__ == '__main__':
    freeze_support()
    MS_DOMAIN2 = input("마나모아 현재 url을 입력해주세요(default - https://manamoa3.net) : ")
    if MS_DOMAIN2 == "" or MS_DOMAIN2 is None:
        MS_DOMAIN2 = 'https://manamoa3.net'
    main()
    os.system('Pause')
