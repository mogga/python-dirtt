"""
	looper.py
	Helper for looping over sequences, particular in templates.
	# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
	# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

	Often in a loop in a template it's handy to know what's next up,
	previously up, if this is the first or last item in the sequence, etc.
	These can be awkward to manage in a normal Python loop, but using the
	looper you can get a better sense of the context.  Use like::

	>>> for loop, item in looper(['a', 'b', 'c']):
	...	 print loop.number, item
	...	 if not loop.last:
	...		 print '---'
	1 a
	---
	2 b
	---
	3 c

"""

__all__ = ['looper']

class looper(object):
	"""
	Helper for looping (particularly in templates)
	
	Use this like::
	
		for loop, item in looper(seq):
			if loop.first:
				...
	"""

	def __init__(self, seq):
		self.seq = seq

	def __iter__(self):
		return looper_iter(self.seq)

	def __repr__(self):
		return '<%s for %r>' % (
			self.__class__.__name__, self.seq)

class looper_iter(object):

	def __init__(self, seq):
		self.seq = list(seq)
		self.pos = 0

	def __iter__(self):
		return self

	def next(self):
		if self.pos >= len(self.seq):
			raise StopIteration
		result = loop_pos(self.seq, self.pos), self.seq[self.pos]
		self.pos += 1
		return result

class loop_pos(object):

	def __init__(self, seq, pos):
		self.seq = seq
		self.pos = pos

	def __repr__(self):
		return '<loop pos=%r at %r>' % (
			self.seq[pos], pos)

	def index(self):
		return self.pos
	index = property(index)

	def number(self):
		return self.pos + 1
	number = property(number)

	def item(self):
		return self.seq[self.pos]
	item = property(item)

	def next(self):
		try:
			return self.seq[self.pos+1]
		except IndexError:
			return None
	next = property(next)

	def previous(self):
		if self.pos == 0:
			return None
		return self.seq[self.pos-1]
	previous = property(previous)

	def odd(self):
		return not self.pos % 2
	odd = property(odd)

	def even(self):
		return self.pos % 2
	even = property(even)

	def first(self):
		return self.pos == 0
	first = property(first)

	def last(self):
		return self.pos == len(self.seq)-1
	last = property(last)

	def length(self):
		return len(self.seq)
	length = property(length)

	def first_group(self, getter=None):
		"""
		Returns true if this item is the start of a new group,
		where groups mean that some attribute has changed.  The getter
		can be None (the item itself changes), an attribute name like
		``'.attr'``, a function, or a dict key or list index.
		"""
		if self.first:
			return True
		return self._compare_group(self.item, self.previous, getter)

	def last_group(self, getter=None):
		"""
		Returns true if this item is the end of a new group,
		where groups mean that some attribute has changed.  The getter
		can be None (the item itself changes), an attribute name like
		``'.attr'``, a function, or a dict key or list index.
		"""
		if self.last:
			return True
		return self._compare_group(self.item, self.next, getter)

	def _compare_group(self, item, other, getter):
		if getter is None:
			return item != other
		elif (isinstance(getter, basestring)
			  and getter.startswith('.')):
			getter = getter[1:]
			if getter.endswith('()'):
				getter = getter[:-2]
				return getattr(item, getter)() != getattr(other, getter)()
			else:
				return getattr(item, getter) != getattr(other, getter)
		elif callable(getter):
			return getter(item) != getter(other)
		else:
			return item[getter] != other[getter]
	