from abc import ABC

class JobAbstract(ABC):

    def on_validate(self, *args, **kwargs):
        raise NotImplementedError

    def on_process(self, *args, **kwargs):
        raise NotImplementedError

    def on_complete(self, *args, **kwargs):
        raise NotImplementedError