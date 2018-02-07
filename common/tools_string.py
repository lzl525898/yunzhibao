__author__ = 'mlzx'
import common.string as string

multi_language_format = "{0}__{1}"


class KeyErrorException(BaseException):
    def __init__(self, key, obj):
        self.key = key
        self.obj = obj

    def __str__(self):
        return "The key {0} not found in {1}".format(self.key, self.obj)


class StringTools(object):
    language_code = 'zh_cn'

    def __init__(self, language_code='zh_cn'):
        if isinstance(language_code, str):
            self.language_code = language_code.strip().replace('-', '_')
        else:
            self.language_code = str(language_code).strip().replace('-', '_')

    def get_string(self, key):
        if hasattr(string, multi_language_format.format(key, self.language_code)):
            return getattr(string, multi_language_format.format(key, self.language_code))
        elif hasattr(string, key):
            return getattr(string, key)
        else:
            raise KeyErrorException(key=key, obj=string)

    @staticmethod
    def default_tool():
        return StringTools('zh-cn')


class Match:
    def __init__(self, percent):
        self.percent = percent

    #
    # 比较dest中字符在src中出现过的次数#
    def match(self, src, dest):
        length = len(dest)
        count = 0
        for c in dest:
            if src.find(c) > -1:
                count += 1
        if count/length > self.percent:
            return True
        else:
            return False