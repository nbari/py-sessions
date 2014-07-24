"""
base backend abstract class
"""

from abc import ABCMeta, abstractmethod


class HandlerBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def set(self, key, value, ttl=0):
        return

    @abstractmethod
    def get(self, key):
        return

    @abstractmethod
    def delete(sekf, key):
        return
