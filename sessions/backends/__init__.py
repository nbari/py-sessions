"""
base backend abstract class
"""

from abc import ABCMeta, abstractmethod


class HandlerBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set(self, sid, data, ttl=0):
        return

    @abstractmethod
    def get(self, sid):
        return

    @abstractmethod
    def delete(self, sid):
        return
