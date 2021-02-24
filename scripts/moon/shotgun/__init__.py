# -*- coding: utf-8 -*-
import shotgun_api3


# SUPERVISORS_GROUP_ID = 6
# SG_PERMISSION_RULE_SET_MANAGER = {'type': 'PermissionRuleSet', 'id': 7}
# SG_PERMISSION_RULE_SET_ARTIST = {'type': 'PermissionRuleSet', 'id': 8}

# Groups
# SG_GROUP_SUPERVISORS = {'type': 'Group', 'id': 6}

# Departments
# SG_DEPARTMENT_PD = {'type': 'Department', 'id': 75}
# SG_DEPARTMENT_DEGISN = {'type': 'Department', 'id': 74}
# SG_DEPARTMENT_MODELING = {'type': 'Department', 'id': 107}
# SG_DEPARTMENT_RIGGING = {'type': 'Department', 'id': 41}
# SG_DEPARTMENT_ANIMATION = {'type': 'Department', 'id': 42}
# SG_DEPARTMENT_LIGHTING = {'type': 'Department', 'id': 140}
# SG_DEPARTMENT_FX = {'type': 'Department', 'id': 141}
# SG_DEPARTMENT_COMP = {'type': 'Department', 'id': 142}
# SG_DEPARTMENT_DIRECTOR = {'type': 'Department', 'id': 143}
# SG_DEPARTMENT_STORY = {'type': 'Department', 'id': 144}


class Shotgun(shotgun_api3.Shotgun):

    SHOTGUN_URL = 'https://pinkmoon.shotgunstudio.com'

    def __init__(self, appname, username=None, password=None, **kwargs):
        appset = {
            'admin_api': {
                'name': 'admin_api',
                'key': 'npauxuwxbzjdgbramOeqp0iz(',
            },
        }
        super(Shotgun, self).__init__(
            self.SHOTGUN_URL,
            script_name=appset[appname]['name'],
            api_key=appset[appname]['key'],
            login=username,
            password=password,
            **kwargs
        )
