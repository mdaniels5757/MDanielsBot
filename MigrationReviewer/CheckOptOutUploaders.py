# Copyright 2020 Michael Daniels
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pywikibot
import re
import os
import sys
import pymysql.cursors
#import MigrationRegexes
#import time
#from datetime import datetime, timezone
#import wikitextparser as wtp

site = pywikibot.Site('commons', 'commons');
categoryName = "Category:License migration opt-out";
cat = pywikibot.Category(site, categoryName)

connection = pymysql.connect( \
    host = 'tools.db.svc.eqiad.wmflabs',\
    read_default_file = '~/replica.my.cnf',\
    database = 's54277__OptOutUploaders',
    autocommit=True)

with connection.cursor() as cursor:
    sql = "TRUNCATE TABLE `links`"
    cursor.execute(sql)

f = open("COOU_log.txt", "a")

i = 0;
for page in cat.articles(namespaces=6):
    i = i + 1;
    links = page.linkedPages(namespaces=2)
    for link in links:
        with connection.cursor() as cursor:
            sql = "SELECT `id` FROM `links` WHERE `link`=%s"
            numresults = cursor.execute(sql, link.title())
            if (numresults == 1):
                result = cursor.fetchone()
                sql = "UPDATE `links` SET `count`=`count` + 1 WHERE `id`=%s"
                cursor.execute(sql, result)
            elif (numresults == 0):
                sql = "INSERT INTO `links` (`link`, `count`) VALUES (%s, 1)"
                cursor.execute(sql, link.title())
            else:
                print("Error: duplicate found", file=sys.stderr, flush=True)
    
    hist = page.get_file_history();
    for key in hist:
        with connection.cursor() as cursor:
            sql = "SELECT `id` FROM `links` WHERE `link`=%s"
            numresults = cursor.execute(sql, 'User:' + hist[key]['user'])
            if (numresults == 1):
                id = cursor.fetchone()
                sql = "UPDATE `links` SET `count`=`count` + 1 WHERE `id`=%s"
                cursor.execute(sql, id)
            elif (numresults == 0):
                sql = "INSERT INTO `links` (`link`, `count`) VALUES (%s, 1)"
                cursor.execute(sql, 'User:' + hist[key]['user'])
            else:
                print("Error: duplicate found", file=sys.stderr, flush=True)
    
    if (i % 100 == 0):
        print(i, file=sys.stderr, flush=True);
        f.write("%d\n" % i)

f.close()