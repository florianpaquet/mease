# -*- coding: utf-8 -*-


class SettingsMixin(object):
    def get_setting(self, settings, parent, name, default=None):
        root = settings

        if parent:
            root = settings.get(parent, {})

        return root.get(name, default)
