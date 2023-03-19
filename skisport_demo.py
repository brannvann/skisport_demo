#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import json
import matplotlib.pyplot as plt

# "демографический срез" пользователей сайта www.skisport.ru (https://www.skisport.ru/forum/other/92285/) 
class skisportUserDemoParser():
    driver = None
    startPage = 'https://www.skisport.ru/forum/all-no-trade/'
    users = {}
    filename = 'users.json'

    def __init__(self)->None:
        chrome_options = webdriver.ChromeOptions()
        prefs = { 'profile.managed_default_content_settings.images' : 2 }
        chrome_options.add_experimental_option("prefs", prefs)
        service = Service(executable_path='/usr/local/bin/chromedriver')
        self.driver = webdriver.Chrome(options=chrome_options, service=service)

    # проход по последним темам форума с фильтром "Все темы, кроме толкучки"
    def start(self):
        self.loadUsers()
        self.driver.get(self.startPage)
        self.driver.maximize_window()
        for index in range(2, 5):
            topics = [t.get_attribute('href') for t in self.driver.find_elements(By.XPATH, '//*/td/a') if ('skisport.ru/forum' in t.get_attribute('href'))]
            for topic in topics:
                self.processTopic(topic)
                self.saveUsers()
            pass
            next_page = f"https://www.skisport.ru/forum/all-no-trade/?PAGEN_1={index}"
            self.driver.get(next_page)
        pass
        self.processData()

    # проход по ссылкам на профили пользователей в теме форума
    def processTopic(self, link):
        self.driver.get(link)
        profile_xpath = "//*[@class='forum-comment-info']/div[1]/a"
        profiles = [p.get_attribute('href') for p in self.driver.find_elements(By.XPATH, profile_xpath)]
        for link in profiles:
            if link and '/profile/' in link:
                id = link.split('/')[-2]
                if not (id in self.users.keys()):
                    self.processProfile(id, link)
                pass    
            pass
        pass

    # если в профиле указана дата рождения, то сохранить её
    def processProfile(self, id, profile):
        bdata = ''
        self.driver.get(profile)
        rows = self.driver.find_elements(By.CLASS_NAME, 'profile-content-row')
        if len(rows) > 3 :
            if divs := rows[3].find_elements(By.CLASS_NAME, 'profile-content-data'):
                bdata = divs[0].text
                print(bdata)
            pass
        pass
        self.users[id] = bdata

    # график количества пользователей по году рождения
    def processData(self):
        years = {}
        max_count = 0
        for _, age in self.users.items():
            if age:
                year = age.split('.')[-1]
                if year in years.keys():
                    years[year] = years[year] + 1    
                else:
                    years[year] = 1
                pass
                if years[year] > max_count:
                    max_count = years[year]
                pass
            pass
        pass
        years = dict(sorted(years.items()))
        labels = years.keys()
        users = years.values()
        fig, ax = plt.subplots()
        ax.bar(labels, users, color='Red', label = '', width=1.0, edgecolor='Black')
        ax.set_ylabel('Количество пользователей', fontsize=16)
        ax.set_title('Возраст пользователей форума сайта www.skisport.ru', fontsize=16)
        ax.legend(fontsize=16)
        xpos = range(len(labels))
        ypos = range(0, max_count)
        plt.xticks(xpos, labels, rotation=60)
        plt.yticks(ypos)
        plt.show()
        pass

    def saveUsers(self):
        with open(self.filename, 'w') as ofs:
            json.dump(self.users, ofs)
        pass

    def loadUsers(self):
        try:
            with open(self.filename, "r") as ifs:
                self.users = json.load(ifs)
        except:
            print(f"cannot read data from {self.filename}")
        pass   

def main(args):
    m = skisportUserDemoParser()
    m.start()
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))