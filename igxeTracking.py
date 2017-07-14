#!/usr/bin/env python
# -*- coding:utf-8 -*-
from selenium import webdriver
import sys
import os 
import time 
import re
import urllib2
import urllib
import requests
import json

global loginFlag
loginFlag = 0

global trackList
trackList = [
	# Karambit, Gamma Doppler, Factory New
	"https://www.igxe.cn/csgo/search/5_38?keyword=%E4%BC%BD%E7%8E%9B&search_page_no=1&search_relate_price=&search_is_sticker=0&search_price_gte=&search_price_lte=&search_rarity_id=&search_exterior_id=&search_is_stattrak=0&search_sort_key=2&search_sort_rule=0",
	# Moto Gloves, Mint/Cool Mint, Field Tested
	"http://www.igxe.cn/csgo/search/13_109?keyword=%E6%91%A9%E6%89%98%E6%89%8B%E5%A5%97%EF%BC%88%E2%98%85%EF%BC%89+%7C+%E8%96%84%E8%8D%B7&search_page_no=1&search_relate_price=&search_is_sticker=0&search_price_gte=&search_price_lte=&search_rarity_id=&search_exterior_id=601&search_is_stattrak=0&search_sort_key=2&search_sort_rule=0",
	# M9, Slaughter, Factory New
	"http://www.igxe.cn/csgo/search/0_0?keyword=M9+%E5%88%BA%E5%88%80%EF%BC%88%E2%98%85%EF%BC%89+%7C+%E5%B1%A0%E5%A4%AB&search_page_no=1&search_relate_price=&search_is_sticker=0&search_price_gte=&search_price_lte=&search_rarity_id=&search_exterior_id=589&search_is_stattrak=0&search_sort_key=2&search_sort_rule=0",
	# AWP, Graphite, Factory New
	"https://www.igxe.cn/csgo/search/4_28?keyword=%E7%9F%B3%E5%A2%A8%E9%BB%91&search_page_no=1&search_relate_price=&search_is_sticker=0&search_price_gte=&search_price_lte=&search_rarity_id=&search_exterior_id=&search_is_stattrak=0&search_sort_key=2&search_sort_rule=0"
]


def doSteamLogin(pageBot, username, password):

	# Fill in steam usernam and password
	steamLoginUser = pageBot.find_element_by_id('steamAccountName')
	steamLoginUser.send_keys(username)
	steamLoginPwd = pageBot.find_element_by_id('steamPassword')
	steamLoginPwd.send_keys(password)

	# Execute login
	pageBot.find_element_by_id('imageLogin').click()

	# Wait for login success page
	print '\nWaiting for login success...\n'
	time.sleep(10)

def itemTracking(pageBot):

	global trackList

	# Select the item to track
	print """
	[1] Karambit, Gamma Doppler, Factory New
	[2] Moto Gloves, Mint/Cool Mint, Field Tested
	[3] M9, Slaughter, Factory New
	[4] AWP, Graphite, Factory New
	"""
	targetItem = raw_input("Enter the number to track an item: ")
	pageContent = redirectToSearchPage(pageBot, trackList[int(targetItem)-1])
	priceList, ratioList_str, mod_hotEquipment_ft = keywordFilter(pageBot, pageContent)
	degreeFromCsgola(pageBot, priceList, ratioList_str, mod_hotEquipment_ft)

	# Current page finished
	proceedOrNot(pageBot, targetItem)

def redirectToSearchPage(pageBot, url):

	# Redirect
	pageBot.get(url)
	print '\nRedirecting...\n'
	time.sleep(3)
	return pageBot.page_source

def keywordFilter(pageBot, content):

	# Get price of each item
	priceList = re.findall('(?<=<strong>).*?(?=</strong>)', content, re.S)
	# Get ratio of each item. If the item does not have a ratio, then the item is too expensive
	ratioList = re.findall('(?<=<span class="bili fr">).*?(?=</span>)', content, re.S)
	ratioList_str = ' '.join(ratioList)
	# Get exact degree of wear of each item
	allGoodsItem = re.findall('(?<=<li class="all-goods--item">).*?(?=</li>)', content, re.S)
	allGoodsItem_str = ' '.join(allGoodsItem)
	mod_hotEquipment_ft = re.findall('(?<=csgo_econ_action_preview\%20).*?(?=")', allGoodsItem_str, re.S)

	return priceList, ratioList_str, mod_hotEquipment_ft

def getCsgolaCookies(pageBot):

	pageCookies = pageBot.get_cookies()

	gatValue = ""
	gidValue = ""
	gaValue = ""
	umValue = ""
	cnzzValue = ""
	phpsessidValue = ""
	cfduidValue = ""

	# Get every part of the cookie
	for cookie in pageCookies:
		if cookie["name"] == "CNZZDATA1257529055":
			cnzzValue = cookie["value"]
		if cookie["name"] == "UM_distinctid":
			umValue = cookie["value"]
		if cookie["name"] == "_ga":
			gaValue = cookie["value"]
		if cookie["name"] == "_gid":
			gidValue = cookie["value"]
		if cookie["name"] == "_gat":
			gatValue = cookie["value"]
		if cookie["name"] == "PHPSESSID":
			phpsessidValue = cookie["value"]
		if cookie["name"] == "__cfduid":
			cfduidValue = cookie["value"]

	# Concatenate to the final cookie value
	finalCookies = ""
	finalCookies += "__cfduid=" + cfduidValue + "; "
	finalCookies += "UM_distinctid=" + umValue + "; "
	finalCookies += "PHPSESSID=" + phpsessidValue + "; "
	finalCookies += "_gat=" + gatValue + "; "
	finalCookies += "CNZZDATA1257529055=" + cnzzValue + "; "
	finalCookies += "_ga=" + gaValue + "; "
	finalCookies += "_gid=" + gidValue

	return finalCookies

def degreeFromCsgola(pageBot, price, ratio, inspect):

	global loginFlag

	if loginFlag == 0:
		pageBot.get('http://www.csgola.com/login/')
		pageBot.find_element_by_xpath("//input[@type='image']").click()
		time.sleep(2)
		pageBot.find_element_by_xpath("//form[@id='openidForm']//input[@type='submit']").click()
		time.sleep(2)
	else:
		pageBot.get('http://www.csgola.com')
		time.sleep(2)

	reqCookies = getCsgolaCookies(pageBot)

	# Change login flag after login success
	loginFlag = 1

	csgolaFetch = 'http://www.csgola.com/market_item_detail'
	headers = {
		'Accept':'*/*',
		'Accept-Encoding':'gzip, deflate',
		'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
		'Connection':'keep-alive',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Cookie': reqCookies,
		'Host':'www.csgola.com',
		'Origin':'http://www.csgola.com',
		'Referer':'http://www.csgola.com/float/',
		'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36',
		'X-Requested-With':'XMLHttpRequest'
	}

	# Integrating price, ratio and degree of wear and then formatting 
	ratio = ratio.replace(' ','')
	ratio = ratio.replace('\n','')

	# Output search results
	print 'Below are search results: \n'

	try:
		printCount = 0
		ratioCount = 0
		for i in range(len(price)):
			sys.stdout.write('价格: ')
			sys.stdout.write(price[i])
			sys.stdout.write('   ')

			for ratioItem in ratio:
				sys.stdout.write(ratioItem)
				ratioCount += 1
				if ratioCount % 7 == 0:
					sys.stdout.write('   ')
					break

			sys.stdout.write(u'\u78e8\u635f\u5ea6: ')

			# Setup payload for each request
			payload = {"inspecturl":inspect[i]}
			req = requests.post(csgolaFetch, data = urllib.urlencode(payload),headers = headers)
			degreeWear = re.findall('(?<=floatval":").*?(?=")', req.text, re.S)
			print degreeWear[0]
			printCount += 1

			sys.stdout.write('\n')
	except Exception:
		print '\n\nFailed to load the remaining items. Connection is unstable now.\n'

	if printCount >= len(price)-1:
		sys.stdout.write('Page successfully loaded.\n\n')
	else:
		pass

def proceedOrNot(pageBot,trackNum):

	isProceed = raw_input("Enter A/D to previous/next page, R to reload page, N to choose another item, E to exit: ")
	if isProceed == 'A' or isProceed == 'a':
		proceedToPage(pageBot,trackNum,isProceed)
	elif isProceed == 'D' or isProceed == 'd':
		proceedToPage(pageBot,trackNum,isProceed)
	elif isProceed == 'R' or isProceed == 'r':
		proceedToPage(pageBot,trackNum,isProceed)
	elif isProceed == 'N' or isProceed == 'n':
		itemTracking(pageBot)
	elif isProceed == 'E' or isProceed == 'e':
		sys.exit(0)
	else:
		proceedOrNot(pageBot,trackNum)

def proceedToPage(pageBot, trackNum, pageFlag):

	global trackList

	itemUrl = trackList[int(trackNum)-1]
	urlSplit = itemUrl.split('&',2)

	# Modify the number of target page
	if pageFlag == 'D' or pageFlag == 'd':
		pageNum = int(urlSplit[1][15])+1
	elif pageFlag == 'R' or pageFlag == 'r':
		pageNum = int(urlSplit[1][15])
	else:
		pageNum = int(urlSplit[1][15])-1
		if pageNum == 0:
			print '\nThere is no more page at the front.\n'
			proceedOrNot(pageBot,trackNum)

	urlSplit[1] = '&search_page_no=' + str(pageNum) + '&'
	finalUrl = ''.join(urlSplit)
	trackList[int(trackNum)-1] = finalUrl

	# Go to target page and fetch infos
	pageBot.get(finalUrl)
	time.sleep(2)
	try:
		pageBot.find_element_by_xpath("//div[@class='all-goods--panel']//ul[@class='all-goods--list com-clean js-add-cart-parent']//li[@class='all-goods--item']")
	except Exception:
		print '\nThere is no more new pages!\n\nSending you back to the previous page...\n'
		pageNum = pageNum - 1
		urlSplit[1] = '&search_page_no=' + str(pageNum) + '&'
		finalUrl = ''.join(urlSplit)
		pageBot.get(finalUrl)

	pageContent = pageBot.page_source
	priceList, ratioList_str, mod_hotEquipment_ft = keywordFilter(pageBot, pageContent)
	degreeFromCsgola(pageBot, priceList, ratioList_str, mod_hotEquipment_ft)
	# Current page finished
	proceedOrNot(pageBot, trackNum)

def main():

	print """
------------------------------------------------------------------------
This is an automaton for weapon searches on IGXE.

GLHF.



Author: PLANCK_C
Update Log
2017/06/10: Basic functionality
2017/07/11: Fetch degree of wear from csgola.com
2017/07/12: Execution flow redesigned. Page turning is now availble.
------------------------------------------------------------------------
	"""

	# Steam login
	pageBot = webdriver.Chrome()
	pageBot.get('http://www.igxe.cn/login')
	steamUsername = 'crawlertest1'
	steamPassword = 'TerransFc4'
	doSteamLogin(pageBot, steamUsername, steamPassword)

	# Start to track CS:GO items
	itemTracking(pageBot)

	print '\nTracking finished.\n'


if __name__ == '__main__':
	main()








