from celery import task, shared_task
from .models import Issue
from time import sleep
from product.models import Product
from django.db.models import F, Q
from salt import client
from django.conf import settings
import os
import subprocess
import shutil
from utils.get_now_time_for_issue import get_now_time

salt_client = client.LocalClient()
git_user = settings.GIT_USER
git_password = settings.GIT_PASSWORD
rsync_server = settings.RSYNC_SERVER
rsync_secrets = settings.RSYNC_SECRETS
remote_rsync_password = settings.REMOTE_RSYNC_PASSWORD

"""
    1   先拉取git代码， [成功 ， 失败]
    2   先判断主机列表状态 [正常执行      不正常放弃，打印无法连接远程主机]
    3   执行rsync同步  或者salt file

"""

@shared_task
def do_accept(issue):
    ip_list = []
    accept_fail_count = 0
    product = Product.objects.get(name=issue.product_name)
    product_name = product.name
    git_clone_code_save_basedir = settings.GIT_CLONE_BASEDIR + product_name
    current_version = product.version
    new_version = current_version + 1
    old_git_clone_code_save_fulldir = git_clone_code_save_basedir + '/' + str(current_version) + '/'
    new_git_clone_code_save_fulldir = git_clone_code_save_basedir + '/' + str(new_version) + '/'
    if not os.path.exists(old_git_clone_code_save_fulldir):
        os.makedirs(old_git_clone_code_save_fulldir)
    git_clone_code_save_fulldir = git_clone_code_save_basedir + '/new/'
    git_address = product.git_address
    #   线上代码目录
    product_dir = product.product_dir
    sync_type = product.sync_type
    sync_option = product.sync_option
    test_ip_list = product.test_ip_list
    gray_ip_list = product.gray_ip_list
    online_ip_list = product.online_ip_list
    no_sync_file_and_path = product.no_sync_file_and_path
    command_before_sync = product.command_before_sync
    command_after_sync = product.command_after_sync
    send_mail = product.send_email
    send_msg = product.send_msg

    #   拉取git代码
    issue.timeline += get_now_time() + ': git 拉取中\n'
    issue.save()
    ## git_cmd = 'git clone' + ' ' + 'http://' + git_user + ':' + git_password + '@' + git_address + ' ' + git_clone_code_save_fulldir
    git_cmd = 'git clone' + ' ' + 'http://' + git_address + ' ' + git_clone_code_save_fulldir
    git_cmd_status, git_cmd_result = subprocess.getstatusoutput(git_cmd)
    if git_cmd_status == 0:
        issue.timeline += get_now_time() + ': git 拉取成功\n'
        issue.save()
    else:
        subprocess.getstatusoutput('rm -f %s' % git_clone_code_save_fulldir)
        issue.timeline += get_now_time() + ': git 拉取失败: %s\n' % git_cmd_result
        issue.status = 13
        issue.save()
        return 'Git fails'

    no_sync_file_and_path_file = "printf '.git\n%s' > /tmp/%s" % (no_sync_file_and_path, product_name)
    dos2unix = 'dos2unix /tmp/%s' % product_name
    test = test_ip_list.split(',')
    gray = gray_ip_list.split(',')
    online = online_ip_list.split(',')
    if sync_type == 't':
        ip_list = test
    elif sync_type == 'g':
        ip_list = gray
    elif sync_type == 'o':
        ip_list = online
    elif sync_type == 'tg':
        ip_list = test + gray
    elif sync_type == 'to':
        ip_list = test + online
    elif sync_type == 'go':
        ip_list = gray + online
    elif sync_type == 'tgo':
        ip_list = test + gray + online

    rsync_cmd_diff = 'exit 1'
    rsync_cmd_exec = 'exit 1'
    if sync_option == 'incremental':
        rsync_cmd_diff = 'rsync -abci --timeout=30 --dry-run --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + git_clone_code_save_fulldir + ' ' + old_git_clone_code_save_fulldir
        rsync_cmd_exec = 'rsync -abc --timeout=30 --contimeout=30 --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + '--password-file=' + remote_rsync_password + ' ' + 'root@' + rsync_server + '::' + product_name + ' ' + product_dir
    elif sync_option == 'full':
        rsync_cmd_diff = 'rsync -abci --timeout=30 --delete-after  --dry-run --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + git_clone_code_save_fulldir + ' ' + old_git_clone_code_save_fulldir
        rsync_cmd_exec = 'rsync -abc --timeout=30 --contimeout=30 --delete-after --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + '--password-file=' + remote_rsync_password + ' ' + 'root@' + rsync_server + '::' + product_name + ' ' + product_dir
    subprocess.getstatusoutput(no_sync_file_and_path_file)
    subprocess.getstatusoutput(dos2unix)
    rsync_cmd_diff_result_status, rsync_cmd_diff_result = subprocess.getstatusoutput(rsync_cmd_diff)
    new_file_and_dir_command = "echo '%s' | awk '{if($1 ~ /\+\+\+\+\+\+\+\+\+/) print $2}'" % rsync_cmd_diff_result
    change_file_and_dir_command = "echo '%s' | awk '{if($1 ~ /..c.*/) print $2}'" % rsync_cmd_diff_result
    delete_file_and_dir_command = "echo '%s' | awk '{if($1 ~ /\*deleting/) print $2}'" % rsync_cmd_diff_result
    a1, a2 = subprocess.getstatusoutput(new_file_and_dir_command)
    b1, b2 = subprocess.getstatusoutput(change_file_and_dir_command)
    c1, c2 = subprocess.getstatusoutput(delete_file_and_dir_command)

    if rsync_cmd_diff_result_status == 0:
        issue.diff_new = a2
        issue.diff_change = b2
        if sync_option == 'full':
            issue.diff_delete = c2
        issue.save()
    else:
        subprocess.getstatusoutput('rm -rf %s' % git_clone_code_save_fulldir)
        issue.timeline += get_now_time() + ': 无法比较代版本差异:%s\n' % rsync_cmd_diff_result
        issue.status = 13
        issue.save()
        return 'diff fails'

    issue.timeline += get_now_time() + ': 代码同步中\n'
    issue.save()
    mkdir = 'mkdir -p' + ' ' + product_dir
    cmd_list = [[mkdir], [no_sync_file_and_path_file], [dos2unix]]
    if command_before_sync:
        cmd_list.append([command_before_sync])
        cmd_list.append([rsync_cmd_exec])
    elif command_after_sync:
        cmd_list.append([rsync_cmd_exec])
        cmd_list.append([command_after_sync])
    elif command_before_sync and command_after_sync:
        cmd_list.append([command_before_sync])
        cmd_list.append(['sleep 5'])
        cmd_list.append([rsync_cmd_exec])
        cmd_list.append([command_after_sync])
    else:
        cmd_list.append([rsync_cmd_exec])
    for ip in ip_list:
        try:
            cmd_list_len = ['cmd.run' for _ in range(len(cmd_list))]
            res = salt_client.cmd(ip, cmd_list_len, cmd_list, tgt_type='ipcidr')
            if not res:
                raise Exception('请确认主机状态')
            issue.success_ip += ip + ','
            issue.save()
        except Exception as e:
            accept_fail_count += 1
            issue.timeline += get_now_time() + ': 代码同步到[%s]失败: %s\n' % (ip, str(e))
            issue.fail_ip += ip + ','
            issue.save()
        else:
            issue.timeline += get_now_time() + ': 代码同步至[%s]成功\n' % ip
            issue.save()
    if accept_fail_count != len(ip_list):
        Issue.objects.filter(can_rollback=True).update(can_rollback=False)
    issue.timeline += get_now_time() + ': 上线操作执行完毕\n'
    if accept_fail_count == 0:
        # subprocess.getstatusoutput('mv %s %s' % (git_clone_code_save_fulldir, new_git_clone_code_save_fulldir))
        os.rename(git_clone_code_save_fulldir, new_git_clone_code_save_fulldir)
        issue.status = 11
        issue.can_rollback = True
        issue.save()
        product.version = new_version
        product.save()
        return 'accept full completed'
    elif 0 < accept_fail_count < len(ip_list):
        # subprocess.getstatusoutput('mv %s %s' % (git_clone_code_save_fulldir, new_git_clone_code_save_fulldir))
        os.rename(git_clone_code_save_fulldir, new_git_clone_code_save_fulldir)
        issue.status = 12
        issue.can_rollback = True
        issue.save()
        product.version = new_version
        product.save()
        return 'accept part completed'
    elif accept_fail_count == len(ip_list):
        shutil.rmtree(git_clone_code_save_fulldir)
        # subprocess.getstatusoutput('rm -rf %s' % git_clone_code_save_fulldir)
        issue.status = 13
        issue.can_rollback = False
        issue.save()
        return 'accept full failed'


@shared_task
def do_rollback(issue):
    product = Product.objects.get(name=issue.product_name)
    rollback_ip = [ip for ip in str(issue.success_ip).split(',') if ip != '']
    current_version = product.version
    old_version = int(current_version) - 1
    product_name = product.name
    product_dir = product.product_dir
    sync_option = product.sync_option
    git_clone_code_save_basedir = settings.GIT_CLONE_BASEDIR + product_name
    rollback_code_dir_before = git_clone_code_save_basedir + '/' + str(old_version) + '/'
    rollback_code_dir_current = git_clone_code_save_basedir + '/' + str(current_version) + '/'
    rollback_code_dir_become_new = git_clone_code_save_basedir + '/new/'
    shutil.copytree(rollback_code_dir_before, rollback_code_dir_become_new)
    rsync_cmd_rollback_exec = 'exit 1'
    error_count = 0
    if sync_option == 'incremental':
        rsync_cmd_rollback_exec = 'rsync -abc --timeout=30 --contimeout=30 --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + '--password-file=' + remote_rsync_password + ' ' + 'root@' + rsync_server + '::' + product_name + ' ' + product_dir
    elif sync_option == 'full':
        rsync_cmd_rollback_exec = 'rsync -abc --timeout=30 --contimeout=30 --delete-after --delay-updates --exclude-from=' + '/tmp/' + product_name + ' ' + '--password-file=' + remote_rsync_password + ' ' + 'root@' + rsync_server + '::' + product_name + ' ' + product_dir
    for ip in rollback_ip:
        try:
            res = salt_client.cmd(ip, 'cmd.run', [rsync_cmd_rollback_exec], tgt_type='ipcidr')
            if not res:
                raise Exception('回滚失败,请确认主机状态')
            issue.timeline += get_now_time() + ': 代码回滚至[%s]成功\n' % ip
        except Exception as e:
            error_count += 1
            issue.timeline += get_now_time() + ': 代码回滚到[%s]失败: %s\n' % (ip, str(e))
            issue.save()
    issue.timeline += get_now_time() + ': 回滚操作执行完毕\n'
    if error_count == 0:
        shutil.rmtree(rollback_code_dir_become_new)
        shutil.rmtree(rollback_code_dir_current)
        product.version = old_version
        product.save()
        issue.status = 14
        issue.can_rollback = False
        issue.save()
    elif 0 < error_count < len(rollback_ip):
        shutil.rmtree(rollback_code_dir_become_new)
        shutil.rmtree(rollback_code_dir_current)
        product.version = old_version
        product.save()
        issue.status = 15
        issue.can_rollback = False
        issue.save()
        return "rollback part success"
    else:
        issue.status = 17
        issue.save()
        return "rollback fails"
    return "rollback success"


"""
awk '{if($1 ~ /\+\+\+\+\+\+\+\+\+/) print $2}' 新增的文件和目录
awk '{if($1 ~ /..c.*/) print $2}'   匹配变化的文件或者文件夹
awk '{if($1 ~ /\*deleting/) print $2}' 删除的文件或者文件夹
"""