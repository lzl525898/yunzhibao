__author__ = 'mlzx'
from common.tools import RequestTools
from common.models import *
from common.interface_helper import *
from common.tools_legoo import ImageTools, ImageFolderType


class AuthRequestTools(RequestTools):

    def validation_client(self, entity):
        if not isinstance(entity, Client):
            raise ParameterError("parameter type error of entity:{0}".format(type(entity)))

    def validation_profile(self, profile, user):
        if not isinstance(profile, UserProfile):
            raise ParameterError("parameter type error of profile:{0}".format(type(profile)))
        if not isinstance(user, User):
            raise ParameterError("parameter type error of user:{0}".format(type(user)))
        # 昵称
        nickname = self.get_parameter("nickname")
        if nickname:
            profile.nickname = nickname
            user.update(set__last_name=nickname)
        # 手机号
        phone = self.get_parameter("phone")
        if phone:
            profile.phone = phone
        # 用户头像
        if 'icon' in self.request.FILES and self.request.FILES['icon']:
            image_tool = ImageTools()
            image = self.request.FILES['icon']
            image_url = image_tool.save(request_file=image, file_folder=ImageFolderType.user, old_file=profile.icon)
            profile.icon = image_url
        sex = self.get_parameter("sex")
        if sex:
            if FormatTools.validate_choices(sex, UserProfile.SEX_TYPE):
                profile.sex = sex
            else:
                raise ParameterError("unknown sex")