from torrentmanager.interfaces import TorrentInterface


class DelugeTorrent(TorrentInterface):
    _id_ = None
    _name = None
    _status = None
    _progress = None
    _size = None
    _age = None

    @property
    def id_(self) -> str:
        return self._id_

    @id_.setter
    def id_(self, id_: str):
        self._id_ = id_

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress: str):
        self._progress = progress

    @property
    def size(self) -> str:
        return self._size

    @size.setter
    def size(self, size: str):
        self._size = size

    @property
    def age(self) -> str:
        return self._age

    @age.setter
    def age(self, age: str):
        self._age = age

    def set_data_from_dict(self, data: dict):
        if 'name' in data:
            self.name = data['name']
        if 'id' in data:
            self.id_ = data['id']
        if 'status' in data:
            self.status = data['status']
        if 'progress' in data:
            self.progress = data['progress']
        if 'size' in data:
            self.size = data['size']
        if 'age' in data:
            self.age = data['age']

    def __repr__(self):
        return "Name: %s\nStatus: %s - Progress: %s (%s)\nAge: %s\n" % (
            self.name,
            self.status,
            self.progress,
            self.size['actual_size'],
            self.age['added']
        )

    def __iter__(self):
        d = {
            "id_": self.id_,
            "name": self.name,
            "status": self.status,
            "progress": self.progress,
            "size": self.size,
            "age": self.age,
        }
        for key in d.keys():
            yield (key, d[key])
