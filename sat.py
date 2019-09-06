import requests
import sys
from bs4 import BeautifulSoup
import time
import json
import pathlib
import getpass
from logger import logger
import argparse
soup1 = None
def loadUser():
    p = pathlib.Path("user.json")
    if p.is_file():
        try:
            with p.open() as f:
                user_info = json.load(f)
                return user_info
        except OSError:
            logger.error("Error trying to open the user info file (user.json)!")
            return 255
    else:
        return -1

def deleteConfig():
    p = pathlib.Path("user.json")
    if p.is_file():
        p.unlink()

def handle_config():
    if pathlib.Path("user.json").is_file():
        logger.info("Loading CollegeBoard account info from file \"user.json\"...")
        user_info = loadUser()
        u = user_info.get("username")
        p = user_info.get("password")
        logger.info("Logging in as: " + u)
    else:
        u = input("Your username: ")
        p = getpass.getpass("Your password (input won't be echoed): ")
        acct_dict = {
            "username": u,
            "password": p
        }
        f = open("user.json", "w+")
        json.dump(acct_dict, f)
        f.close()
    return u, p

def checkScores(usr, pwd):
    global soup1
    url = "https://account.collegeboard.org/login/authenticateUser"
    headers = {
        "authority": "account.collegeboard.org",
        "scheme": "https",
        "origin": "https://account.collegeboard.org",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Referer": "https://account.collegeboard.org/login/authenticateUser"
        }
    data = {
        "DURL": "https://nsat.collegeboard.org/satweb/satHomeAction.action",
        "appId": "319",
        "formState": "1",
        "username": usr,
        "password": pwd,
        "sign-in": ""
        }
    s = requests.Session()
    #print(headers)
    r = s.post(url, data=data, headers=headers)
    if r.status_code == 200:
        if "don\'t recognize" in r.text:
            deleteConfig()
            logger.error("Your login credentials are invalid. Try again?")
            exit(255)
        else:
            logger.info("Login successful!")
    else:
        logger.error("Login failed! Exiting...")
        # a non-200 response code means errors other than incorrect username/pwd
        logger.debug(r.text)
        exit(255)
    soup = BeautifulSoup(r.text, features="html.parser")
    ## DEBUG:
    soup1 = soup
    scores = soup.find_all("div", {"class": "col-sm-7 col-xs-12 cb-base-font-size"})
    header_content = soup1.find_all("div", {"class":"header-content"})
    #print(header_content)
    is_sat = []
    for i in range(0,len(header_content)):
        header_content_text = header_content[i].find_all("h3")[0].get_text()
        #print(a)
        if header_content_text.find("SAT with Essay —") != -1 or a.find("SAT —") != -1:
            is_sat.append(True)
        else:
            is_sat.append(False)
    #print(is_sat)
    offset = 0
    score_report = "\nYour scores:"
    score_sat = ""
    for i in range(0, len(header_content)):
        if is_sat[i] == False:
            #print(i+offset)
            temp = header_content[i].find_all("h3")[0].get_text()
            temp2 = soup1.find_all("div", {"class":"score"})[i+offset].get_text()
            score_report += "\n"
            score_report += temp
            score_report += ": "
            score_report += temp2
        else:
            new_offset = offset + 2
            temp = header_content[i].find_all("h3")[0].get_text()
            score_report += "\n "
            score_report += temp
            score_report += ", Total: "
            score_report += soup1.find_all("div", {"class":"score"})[i+offset].get_text()
            score_report += ", EBRW: "
            score_report += soup1.find_all("div", {"class":"score"})[i+offset+1].get_text()
            score_report += ", Math: "
            score_report += soup1.find_all("div", {"class":"score"})[i+offset+2].get_text()
            offset = new_offset

    logger.info(score_report)
    '''for i in range(len(scores)):
        tmp = scores[i].get_text()
        tmp = tmp.replace("\n\n\n\n\n \n", "")
        tmp = tmp.replace("\n\n\n", "")
        tmp = tmp.replace(" \n", "")
        tmp = tmp.replace("\n\n", "")
        tmp = tmp.replace(" SAT", "SAT")
        tmp = tmp.replace("Total Score", "")
        logger.info(str(i+1) + ": " + tmp + "\n")'''

def checkScoresDiff(usr, pwd):
    url = "https://account.collegeboard.org/login/authenticateUser"
    headers = {
        "authority": "account.collegeboard.org",
        "scheme": "https",
        "origin": "https://account.collegeboard.org",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
        "Referer": "https://account.collegeboard.org/login/authenticateUser"
        }
    data = {
        "DURL": "https://nsat.collegeboard.org/satweb/satHomeAction.action",
        "appId": "319",
        "formState": "1",
        "username": usr,
        "password": pwd,
        "sign-in": ""
        }
    #print(headers)
    s = requests.Session()
    r = s.post(url, data=data, headers=headers)

    if r.status_code == 200:
        if "don\'t recognize" in r.text:
            deleteConfig()
            logger.error("Your login credentials are invalid. Try again?")
            exit(255)
        else:
            logger.info("Login successful!")
    else:
        logger.error("Request failed with a status code of " + str(r.status_code) + ". Exiting...")
        # a non-200 response code means errors other than incorrect username/pwd
        logger.debug(r.text)
        exit(255)
    soup = BeautifulSoup(r.text, features="html.parser")
    scores = soup.find_all("div", {"class": "col-sm-7 col-xs-12 cb-base-font-size"})
    header_content = soup.find_all("div", {"class":"header-content"})
    is_sat = False
    #print(soup)
    header_content_text = header_content[0].find_all("h3")[0].get_text()
    if header_content_text.find("SAT with Essay —") != -1 or header_content_text.find("SAT —") != -1:
        is_sat = True
    else:
        is_sat = False
    #print(is_sat)
    score_report = "\nYour scores:"
    #score_sat = ""
    if is_sat == False:
        temp = header_content_text
        temp2 = soup.find_all("div", {"class":"score"})[0].get_text()
        score_report += "\n"
        score_report += temp
        score_report += ": "
        score_report += temp2
    else:
        #new_offset = offset + 2
        temp = header_content_text
        score_report += "\n "
        score_report += temp
        score_report += ", Total: "
        score_report += soup.find_all("div", {"class":"score"})[0].get_text()
        score_report += ", EBRW: "
        score_report += soup.find_all("div", {"class":"score"})[1].get_text()
        score_report += ", Math: "
        score_report += soup.find_all("div", {"class":"score"})[2].get_text()
        offset = new_offset

    #logger.info(score_report)
    '''tmp1 = scores[0]
    tmp = scores[0].get_text()
    #print(scores[0])
    tmp = tmp.replace("\n\n\n\n\n \n", "")
    tmp = tmp.replace("\n\n\n", "")
    tmp = tmp.replace(" \n", "")
    tmp = tmp.replace("\n\n", "")
    tmp = tmp.replace(" SAT", "SAT")
    tmp = tmp.replace("Total Score", "")
    res = tmp'''
    return score_report

def main():
    parser = argparse.ArgumentParser(description='Checks collegeboard.org periodically for new (P)SAT scores.')
    parser.add_argument("-c", "--check", help="periodically check new scores", action="store_true")
    parser.add_argument("-co", "--check-once", help="check all scores and exit", action="store_true")
    args = parser.parse_args()
    if len(sys.argv)==1:
        args.check = True
        print("Checking new scores periodically. For help, add \"-h\" or \"--help\" for available options.")
    if args.check_once:
        #print("oof")
        u, p = handle_config()
        checkScores(u, p)
        return
    if args.check:
        u, p = handle_config()
        #print(p, u)
        prevResults = checkScoresDiff(u, p)
        logger.info(prevResults)
        time.sleep(20)
        iter = 0
        while True:
            #print(p, u)
            curResults = checkScoresDiff(u, p)

            if curResults != prevResults:
                logger.warning("New scores posted!")
                logger.info(curResults)
                if os.name == "nt":
                    os.system("pause")
                else:
                    exit(0)
            time.sleep(20)

if __name__ == "__main__":
    main()
