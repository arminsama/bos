from django.contrib.auth.mixins import UserPassesTestMixin


# 用户权限检查 跳转登录页面
class RootRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        elif not self.request.user.is_root:
            self.raise_exception = True
            return False
        return True
