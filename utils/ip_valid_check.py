import re


def ip_list_check(args):
    """
    test if given ip list is valid for project_manage.views.ProjectCreateView or ProjectUpdateView.
    :param args: self.request
    :return:
    """
    flag = args.POST['sync_type']

    def re_check(ip_list, ff):
        for ip in ip_list:
            if not re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip):
                return False, ff
        return True, ff

    def test_ip_list_check():
        ips = args.POST['test_ip_list']
        if ips:
            ip_list = str(ips).split(',')
            return re_check(ip_list, '测试IP列表')

    def gray_ip_list_check():
        ips = args.POST['gray_ip_list']
        if ips:
            ip_list = str(ips).split(',')
            return re_check(ip_list, '灰度IP列表')

    def online_ip_list_check():
        ips = args.POST['online_ip_list']
        if ips:
            ip_list = str(ips).split(',')
            return re_check(ip_list, '线上IP列表')

    if flag == 't':
        test_ip_check_result, ff1 = test_ip_list_check()
        if test_ip_check_result is False:
            return False, ff1
        else:
            return True, ff1
    elif flag == 'g':
        gray_ip_check_result, ff1 = gray_ip_list_check()
        if gray_ip_check_result is False:
            return False, ff1
        else:
            return True, ff1
    elif flag == 'o':
        online_ip_check_result, ff1 = online_ip_list_check()
        if online_ip_check_result is False:
            return False, ff1
        else:
            return True, ff1
    elif flag == 'tg':
        test_ip_check_result, ff1 = test_ip_list_check()
        gray_ip_check_result, ff2 = gray_ip_list_check()
        if test_ip_check_result is False:
            return False, ff1
        elif gray_ip_check_result is False:
            return False, ff2
        else:
            return True, ''
    elif flag == 'to':
        test_ip_check_result, ff1 = test_ip_list_check()
        online_ip_check_result, ff2 = gray_ip_list_check()
        if test_ip_check_result is False:
            return False, ff1
        elif online_ip_check_result is False:
            return False, ff2
        else:
            return True, ''
    elif flag == 'go':
        gray_ip_check_result, ff1 = gray_ip_list_check()
        online_ip_check_result, ff2 = online_ip_list_check()
        if gray_ip_check_result is False:
            return False, ff1
        elif online_ip_check_result is False:
            return False, ff2
        else:
            return True, ''
    elif flag == 'tgo':
        test_ip_check_result, ff1 = test_ip_list_check()
        gray_ip_check_result, ff2 = gray_ip_list_check()
        online_ip_check_result, ff3 = online_ip_list_check()
        if test_ip_check_result is False:
            return False, ff1
        elif gray_ip_check_result is False:
            return False, ff2
        elif online_ip_check_result is False:
            return False, ff3
        else:
            return True, ''
