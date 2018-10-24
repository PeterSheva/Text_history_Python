
class TextHistory:
    def __init__(self):
        self._text = ""
        self._version = 0
        self._actions = []
        
    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.text)

        a = InsertAction(pos, text, self._version, self._version + 1)
        return self.action(a)

    def replace(self, text, pos = None):
        if pos is None:
            pos = len(self.text)

        a = ReplaceAction(pos, text, self._version, self._version + 1)
        return self.action(a)

    def delete(self, pos, length):
        a = DeleteAction(pos, length, self._version, self._version + 1)
        return self.action(a)

    def action(self, action):
        if action.pos > len(self.text) or action.pos < 0 or action.to_version <= action.from_version:
            raise ValueError

        self._text = action.apply(self._text)
        self._version = action.to_version
        self._actions.append(action)

        return self._version

    def get_actions(self, from_version=None, to_version=None):
        if from_version is None:
            from_version = 0

        if to_version is None:
            to_version = self._version

        if from_version > self._version or to_version > self._version:
            raise ValueError
        elif from_version > to_version:
            raise ValueError
        elif from_version < 0 or to_version < 0:
            raise ValueError

        actions = []
        for action in self._actions:
            if from_version <= action.from_version < to_version:
                actions.append(action)
        return self.optimize(actions)

    def optimize(self, action_list):
        for act in range(len(action_list)-1):

            pre_act = action_list[len(action_list)-1]

            if(isinstance(pre_act, DeleteAction) and isinstance(act, DeleteAction) and act.pos == pre_act.pos):
                pre_act.length = pre_act.length + act.length
                pre_act.to_version = act.to_version

            if(isinstance(pre_act, InsertAction) and isinstance(act, InsertAction)):
                if(act.pos == pre_act.pos):
                    pre_act.text = act.text + pre_act.text
                elif((act.pos - pre_act.pos) == len(pre_act.text)):
                    pre_act.text = pre_act.text + act.text 

        return action_list

class Action:
    def __init__(self, pos, text, from_version, to_version):
        self.pos = pos
        self.text = text
        self.from_version = from_version
        self.to_version = to_version

class InsertAction(Action):
    def __repr__(self):
        return 'insert({}, pos = {}, version1 = {}, version2 = {})'.format(self.text, self.pos, self.from_version, self.to_version)

    def apply(self, text):
        text = text[:self.pos] + self.text + text[self.pos:]
        return text


class ReplaceAction(Action):
    def __repr__(self):
        return 'replace({}, pos = {}, version1 = {}, version2 = {})'.format(self.text, self.pos, self.from_version, self.to_version)

    def apply(self, text):
        end_idx = self.pos + len(self.text)

        if end_idx >= len(text):
            text = text[:self.pos] + self.text
        else:
            text = text[:self.pos] + self.text + text[end_idx:]

        return text

class DeleteAction(Action):

    def __init__(self, pos, length, from_version, to_version):
        self.pos = pos
        self.length = length
        self.from_version = from_version
        self.to_version = to_version

    def __repr__(self):
        return 'delete(pos = {}, length = {}, version1 = {}, version2 = {})'.format(self.pos, self.length, self.from_version, self.to_version)

    def apply(self, text):
        if self.pos + self.length > len(text):
            raise ValueError

        text = text[:self.pos] + text[self.pos + self.length:]
        return text
