class Apk:

    def __init__(self, name, version, updateTime, type, mainActivity):
        self.name = name
        self.version = version
        self.updateTime = updateTime
        self.type = type
        self.mainActivity = mainActivity

    def obj_2_json(self):
        return {
            'name': self.name,
            'version': self.version,
            'updateTime': self.updateTime,
            'type': self.type,
            'mainActivity': self.mainActivity
        }

    def json_2_obj(dict):
        return Apk(dict['name'], dict['version'], dict['updateTime'], dict['type'], dict['mainActivity'])
