from abc import ABC, abstractmethod


class IListener(ABC):
    @abstractmethod
    def run(self, **kwargs):
        """do the job"""
