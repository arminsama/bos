#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest
from issue.models import Issue, Product
from django.db.models import Q
# from config.models import Config
# from mail import send_mail
# from to_task.tasks import send_mail_task
# import salt.client

# client = salt.client.LocalClient()

import os, subprocess, commands
import shutil
import time
from datetime import datetime
import re
from django.conf import settings
import salt.client
# from tasks.task import send_mail_task
from mail import send_mail

client = salt.client.LocalClient()

import sys
import logging
from .models import Issue
from product.models import Product
from users.models import User

logger = logging.getLogger('django')
reload(sys)
sys.setdefaultencoding('utf-8')


import sys, os
import time

def code_back(issueid_old, issueid_now):
    issue_old = Issue.objects.get(id=issueid_old)
    issue_now = Issue.objects.get(id=issueid_now)
    product = Product.objects.get(productname=issue_now.product_name)
    product_simu_ip = product.product_simu_ip
    product_name = product.productname
    product_path = product.product_path
    product_version = issue_old.code_version
    product_keepfile = product.product_keep_file
    product_model = product.model_online
    codepath = settings.CODE_PATH
    rsyncserver_ip = settings.RSYNCSERVER_ADDRESS
    rsync_passwd_file = settings.RSYNC_PATH
    product_rsync_option = product.rsync_option
    product_new = 'new'

    issue_now.assign_user = 'aos上线机器人'
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    issue_now.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>受理了提案\n' % now_time
    issue_now.save()

    product_code_path = os.path.join(codepath, product_name, product_new)
    product_code_path += '/'
    if os.path.exists(product_code_path):
        shutil.rmtree(product_code_path)

    product_v = 'v' + str(product_version)
    product_code_version_path = os.path.join(codepath, product_name, product_v)

    if os.path.exists(product_code_version_path):
        shutil.copytree(product_code_version_path, product_code_path)
    else:
        return 'No product file'

    onli_ips = product.product_online_ip.split('\n')
    onlinelation = []
    for online_ip in onli_ips:
        onlinelation.append(online_ip)
    if product_model == 'tgo':
        simu_ips = product.product_simu_ip.split('\n')
        for simu_ip in simu_ips:
            onlinelation.append(simu_ip)
    iplist = set(onlinelation)

    command_p = []
    product_command_get = product.product_command_later
    if product_command_get:
            product_command = product.product_command_later.split(';')
            for p_c in product_command:
                command_p.append(p_c)

    for ip in iplist:
        ip = ip.strip()
        pattern = re.compile(r'not found|No such file or directory| error|Can\'t open|error|can\'t|fatal')
        if ip and '\r' not in ip and '\t' not in ip and ' ' not in ip:
            check = client.cmd(ip, 'cmd.cun', ['echo 1'])
            if check:
                mkdir_cmd = "mkdir -p " + product_path
                m_ret = client.cmd(ip, 'cmd.run', [mkdir_cmd])
                rsync_exlude_cmd = 'echo "%s"  > /tmp/%s' % (product_keepfile, product_name)
                client.cmd(ip, 'cmd.run', [rsync_exlude_cmd])
                if product_rsync_option == 'delete':
                    rsync_cmd = "rsync -rltDz --delete-after  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                else:
                    rsync_cmd = "rsync -rltDz  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                ret = client.cmd(ip, 'cmd.run', [rsync_cmd])

                out_ret = str(ret)
                if pattern.search(out_ret):
                    issue_now.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">" + out_ret + "</font> \n"
                    issue_now.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##########################################</p>"
                else:
                    issue_now.msg += "<font color=\"green\">" + ip + " : </font>" + 'rsync success!' + "\n"
                    if command_p:
                        for i in command_p:
                                cmd_ret = client.cmd(ip, 'cmd.run', [i])
                                issue_now.msg += "<font color=\"green\">" + ip + " : </font>" + str(cmd_ret) + "\n"
                                print 'now command code %s' % i
            else:
                issue_now.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">saltapi 无法连接到远程主机 </font> \n"
                issue_now.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##########################################</p>"

    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    issue_now.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>完成了回滚\n' % now_time
    issue_now.status = 10
    issue_now.assign_user = issue_now.test_user
    issue_now.msg += '<h3>回滚到%s</h3>' % product_version
    issue_now.issue_title = '[已回滚]' + issue_now.issue_title
    issue_now.code_version = product_version
    issue_now.save()
    if os.path.exists(product_code_path):
        shutil.rmtree(product_code_path)
    send_mail(issueid_now)


def gray_back(issue_id, product_id):
    global iplist
    issue = Issue.objects.get(id=issue_id)
    product = Product.objects.get(id=product_id)
    product_simu_ip = product.product_simu_ip
    product_name = product.productname
    product_path = product.product_path
    product_version = product.product_version
    product_keepfile = product.product_keep_file
    codepath = settings.CODE_PATH
    gituser = settings.GII_USER
    gitpasswd = settings.GIT_PASSWD
    rsyncserver_ip = settings.RSYNCSERVER_ADDRESS
    rsync_passwd_file = settings.RSYNC_PATH
    product_rsync_option = product.rsync_option
    product_new = 'new'

    issue.assign_user = 'aos上线机器人'
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>受理了提案\n' % now_time
    issue.save()

    product_code_path = os.path.join(codepath, product_name, product_new)
    product_code_path += '/'
    if os.path.exists(product_code_path):
        shutil.rmtree(product_code_path)
    product_v = 'v' + str(product.product_version)
    product_code_version_path = os.path.join(codepath, product_name, product_v)
    if os.path.exists(product_code_version_path):
        shutil.copytree(product_code_version_path, product_code_path)
    else:
        return 'No product file'

    simu_ips = product.product_simu_ip.split('\n')
    simulation = []
    for simu_ip in simu_ips:
        simulation.append(simu_ip)
    iplist = set(simulation)

    command_p = []
    product_command_get = product.product_command_later
    if product_command_get:
            product_command = product.product_command_later.split(';')
            for p_c in product_command:
                command_p.append(p_c)

    for ip in iplist:
        ip = ip.strip()
        pattern = re.compile(r'not found|No such file or directory| error|Can\'t open|error|can\'t|fatal')
        if ip and '\r' not in ip and '\t' not in ip and ' ' not in ip:
            check = client.cmd(ip, 'cmd.cun', ['echo 1'])
            if check:
                mkdir_cmd = "mkdir -p " + product_path
                m_ret = client.cmd(ip, 'cmd.run', [mkdir_cmd])
                rsync_exlude_cmd = 'echo "%s"  > /tmp/%s' % (product_keepfile, product_name)
                print rsync_exlude_cmd
                client.cmd(ip, 'cmd.run', [rsync_exlude_cmd])
                if product_rsync_option == 'delete':
                    rsync_cmd = "rsync -rltDz --delete-after  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                else:
                    rsync_cmd = "rsync -rltDz  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                ret = client.cmd(ip, 'cmd.run', [rsync_cmd])
                print 'now rsync code %s' % rsync_cmd

                out_ret = str(ret)
                if pattern.search(out_ret):
                    issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">" + out_ret + "</font> \n"
                    issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##############################d############</p>"
                else:
                    issue.msg += "<font color=\"green\">" + ip + " : </font>" + 'rsync success!' + "\n"
                    if command_p:
                        for i in command_p:
                                cmd_ret = client.cmd(ip, 'cmd.run', [i])
                                issue.msg += "<font color=\"green\">" + ip + " : </font>" + str(cmd_ret) + "\n"
                                print 'now command code %s' % i
            else:
                issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">saltapi 无法连接到远程主机 </font> \n"
                issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##########################################</p>"

    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>完成了灰度回滚\n' % now_time
    issue.status = -1
    issue.assign_user = issue.test_user
    issue.save()
    if os.path.exists(product_code_path):
        shutil.rmtree(product_code_path)


def test(issue_id, product_id):
    global iplist
    issue = Issue.objects.get(id=issue_id)
    product = Product.objects.get(id=product_id)
    product_name = product.productname
    product_git_addr = product.git_path
    product_path = product.product_path
    product_rsync_option = product.rsync_option
    product_model_online = product.model_online
    product_command_later = product.product_command_later
    product_add_mail = product.product_add_mail
    product_test_ip = product.product_test_ip
    product_simu_ip = product.product_simu_ip
    product_online_ip = product.product_online_ip
    product_keep_file = product.product_keep_file
    product_version = product.product_version
    product_keepfile = product.product_keep_file
    product_ad = product.productline.productline_users
    product_ad_name = User.objects.get(username=product_ad).name
    # status = int(issue.status) + 1
    # issue.status = status
    issue.lastupdate = datetime.now()
    issue.save()
    if not issue.msg:
        issue.msg = ''

    issue.assign_user = 'aos上线机器人'
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>受理了提案\n' % now_time
    issue.save()

    codepath = settings.CODE_PATH
    gituser = settings.GII_USER
    gitpasswd = settings.GIT_PASSWD
    rsyncserver_ip = settings.RSYNCSERVER_ADDRESS
    rsync_passwd_file = settings.RSYNC_PATH
    product_new = 'new'

    product_code_path = os.path.join(codepath, product_name, product_new)
    product_code_path += '/'

    if issue.status == 1 or (product_model_online == 'o' and issue.status == 8):
        if not os.path.exists(product_code_path):
            os.makedirs(product_code_path)
        else:
            shutil.rmtree(product_code_path)
            os.makedirs(product_code_path)

        if 'http://' in product_git_addr:
            product_git_addr = product_git_addr.split('http://')[1]

        clone_cmd = 'git clone ' + ' http://' + gituser + ':' + gitpasswd + '@' + product_git_addr + ' ' + product_code_path
        print clone_cmd
        (command_status, command_output) = commands.getstatusoutput(clone_cmd)
        if command_status != 0:
            issue.msg += "<font color=\"red\">" + command_output + "</font>"
            issue.status = -1
            issue.lastupdate = datetime.now()
            issue.save()
            # send_mail_task.delay(issue)
            return
        else:
            git_init_file = product_code_path + '.git'
            shutil.rmtree(git_init_file)
        version_laster = 'v' + product_version
        product_last_version = os.path.join(codepath, product_name, version_laster)
        issue.gitdiff = ''
        if os.path.exists(product_last_version):
            diff_cmd = 'diff -ruaq ' + product_code_path + ' ' + product_last_version + " | grep -v '\.git'  | grep 'differ$' | awk '{print $2}' | awk -F 'new' '{print $2}'"
            (command_status, command_output) = commands.getstatusoutput(diff_cmd)
            if command_output:
                issue.gitdiff += '<span class="label label-info">变化的文件</span>\n'
                issue.gitdiff += "<font color=\"green\">" + command_output + "</font>\n"
            else:
                issue.gitdiff += '<span class="label label-info">变化的文件</span>\n'
                issue.gitdiff += "<font color=\"green\">" + 'None' + "</font>\n"

            diff_cmd = 'diff -ruaq ' + product_code_path + ' ' + product_last_version + " | grep -v '\.git'  | grep '^Only'  | grep  -v 'new:'  | awk '{print $NF}'"
            (command_status, command_output) = commands.getstatusoutput(diff_cmd)
            if command_output:
                issue.gitdiff += '<span class="label label-info">增加的文件或文件夹</span>\n'
                issue.gitdiff += "<font color=\"green\">" + command_output + "</font>\n"
            else:
                issue.gitdiff += '<span class="label label-info">增加的文件或文件夹</span>\n'
                issue.gitdiff += "<font color=\"green\">" + 'None' + "</font>\n"

            diff_cmd = 'diff -ruaq ' + product_code_path + ' ' + product_last_version + " | grep -v '\.git'  | grep '^Only'  | grep 'new:'  | awk '{print $NF}'"
            (command_status, command_output) = commands.getstatusoutput(diff_cmd)
            if command_output:
                issue.gitdiff += '<span class="label label-info">删除的文件或文件夹</span>\n'
                issue.gitdiff += "<font color=\"green\">" + command_output + "</font>\n"
            else:
                issue.gitdiff += '<span class="label label-info">删除的文件或文件夹</span>\n'
                issue.gitdiff += "<font color=\"green\">" + 'None' + "</font>\n"

    if issue.status == 1:
        test_ips = product.product_test_ip.split('\n')
        testlation = []
        for test_ip in test_ips:
                testlation.append(test_ip)
        iplist = set(testlation)
    elif issue.status == 4:
        simu_ips = product.product_simu_ip.split('\n')
        simulation = []
        for simu_ip in simu_ips:
                simulation.append(simu_ip)
        iplist = set(simulation)
    elif issue.status == 8:
        onli_ips = product.product_online_ip.split('\n')
        onlinelation = []
        for online_ip in onli_ips:
                onlinelation.append(online_ip)
        iplist = set(onlinelation)

    command_p = []
    #product_command = product.product_command_later.split(';')
    product_command_get = product.product_command_later
    if product_command_get:
            product_command = product.product_command_later.split(';')
            for p_c in product_command:
                command_p.append(p_c)
    # p_command = set(command_p)

    for ip in iplist:
        ip = ip.strip()
        pattern = re.compile(r'not found|No such file or directory| error|Can\'t open|error|can\'t|fatal')
        if ip and '\r' not in ip and '\t' not in ip and ' ' not in ip:
            check = client.cmd(ip, 'cmd.cun', ['echo 1'])
            if check:
                mkdir_cmd = "mkdir -p " + product_path
                m_ret = client.cmd(ip, 'cmd.run', [mkdir_cmd])
                rsync_exlude_cmd = 'echo "%s"  > /tmp/%s' % (product_keepfile, product_name)
                print rsync_exlude_cmd
                client.cmd(ip, 'cmd.run', [rsync_exlude_cmd])
                if product_rsync_option == 'delete':
                    rsync_cmd = "rsync -rltDz --delete-after  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                else:
                    rsync_cmd = "rsync -rltDz  --timeout=15 --contimeout=15 --exclude-from=/tmp/" + product_name + " root@" + rsyncserver_ip + "::" + product_name + ' ' + product_path + " --password-file=" + rsync_passwd_file
                ret = client.cmd(ip, 'cmd.run', [rsync_cmd])
                print 'now rsync code %s' % rsync_cmd

                out_ret = str(ret)
                if pattern.search(out_ret):
                    issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">" + out_ret + "</font> \n"
                    issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##########################################</p>"
                else:
                    issue.msg += "<font color=\"green\">" + ip + " : </font>" + 'rsync success!' + "\n"
                    if command_p:
                        for i in command_p:
                                cmd_ret = client.cmd(ip, 'cmd.run', [i])
                                issue.msg += "<font color=\"green\">" + ip + " : </font>" + str(cmd_ret) + "\n"
                                print 'now command code %s' % i
            else:
                issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">saltapi 无法连接到远程主机 </font> \n"
                issue.msg += "<font color=\"green\">" + ip + " : </font> <font color=\"red\">执行失败</font> \n <p>##########################################</p>"
    issue.status = issue.status + 1
    issue.lastupdate = datetime.now()
    issue.save()

    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if issue.status == 2:
        issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>完成了测试上线操作\n' % now_time
    elif issue.status == 5:
        issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>完成了灰度上线操作\n' % now_time
    elif issue.status == 9:
        issue.info += '%s  &emsp;<span class="label label-info">aos上线机器人</span>完成了正式上线操作\n' % now_time
    issue.assign_user = issue.test_user
    issue.lastupdate = datetime.now()
    issue.save()
    if issue.status == 9:
        product.product_version = issue.code_version
        product.save()
        product_v = 'v' + str(product.product_version)
        product_code_v = os.path.join(codepath, product_name, product_v)
        os.rename(product_code_path, product_code_v)
        version = float(product.product_version) - 0.6
        pro_back_v = 'v' + str(version)
        product_code_path = os.path.join(codepath, product_name)
        product_code_path += '/'
        issue_v = os.listdir(product_code_path)
        for i in issue_v:
            product_version_d = os.path.join(product_code_path, i)
            if i <= pro_back_v:
                if os.path.exists(product_version_d):
                    shutil.rmtree(product_version_d)
    send_mail(issue_id)
