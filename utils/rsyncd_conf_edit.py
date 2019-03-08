import subprocess
import os
from django.conf import settings


def rsync_config_add(product_name):
    git_clone_basedir = settings.GIT_CLONE_BASEDIR
    title = '[' + product_name + ']'
    rsyncd_conf = settings.RSYNCD_CONFIG
    product_new = 'new'
    file = open(rsyncd_conf, "r")
    f = file.read()
    file.close()
    pos = f.find(title)
    if pos != 0:
        product_rsync_option = '[' + product_name + ']' + '\n'
        product_code_path = os.path.join(git_clone_basedir, product_name, product_new)
        product_rsync_path = 'path ' + '= ' + product_code_path + '\n'
        file = open(rsyncd_conf, "a")
        file.write(product_rsync_option)
        file.write(product_rsync_path)
        file.close()


def rsync_config_del(old_product_name):
    title = '[' + old_product_name + ']'
    rsyncd_conf = settings.RSYNCD_CONFIG
    file = open(rsyncd_conf, "r")
    content = file.read()
    file.close()
    pos = content.find(title)
    if pos != -1:
        product_inline = "sed -n '/\[%s\]/='  %s" % (old_product_name, rsyncd_conf)
        (command_status, command_output) = subprocess.getstatusoutput(product_inline)
        product_del = "sed -i '%s,%sd' %s" % (command_output, int(command_output) + 1, rsyncd_conf)
        del_status, del_info = subprocess.getstatusoutput(product_del)
        if del_status == 0:
            return True
    return False
