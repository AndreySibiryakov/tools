'''
Maya class for combining poses splitted on two sides: left and right.
	Used it to restore emotions after auto skinning process
	done with a Webber Huang's DLS.
	Combine operation Works with joints.


Code to insert to the shelf:
	import combine_l_r as co
	reload(co)
	sum = co.SumAttrs()
	sum.gui()
'''

import maya.cmds as cmds
import sys

__author__ = "Andrey Sibiryakov"
__email__ = "comcommac@gmail.com"

class SumAttrs(object):
	def __init__(self):
		self.axis = [o+a for o in ['rotate','translate', 'scale'] for a in ['X','Y','Z']]
		self.right = {}
		self.left = {}
		self.neutral = {}
		self.selection = []
		self.sum = {}

	def get(self, objects):
		attrs = {}
		objects_attrs = [o+'.'+a for o in objects for a in self.axis]
		
		for o_a in objects_attrs:
			attrs[o_a] = cmds.getAttr(o_a)
		
		return attrs

	def get_diff(self, a, b):
		attrs = [attr for attr in a.keys()]
		diff = {}
		
		for attr in attrs:
			diff[attr] = b[attr]-a[attr]
		
		return diff

	def get_sum(self, a, b):
		t = self.neutral
		attrs = [attr for attr in a.keys()]
		
		for attr in attrs:
			self.sum[attr] = t[attr]+a[attr]+b[attr]

	def sett(self, a):
		
		for attr, value in a.iteritems():
			cmds.setAttr(attr, value)

	def get_neutral(self, *args):
		self.selection = cmds.ls(sl=True)
		if not self.selection:
			sys.exit('Select something to get attributes from.')
		self.neutral = self.get(self.selection)

	def get_right(self, *args):
		if not self.selection:
			sys.exit('Set neutral.')
		self.right = self.get(self.selection)

	def get_left(self, *args):
		if not self.selection:
			sys.exit('Set neutral.')
		self.left = self.get(self.selection)

	def set_sum(self, *args):
		if not self.left or not self.right or not self.neutral:
			sys.exit('Collect all three attributes')
		delta_left = self.get_diff(self.neutral, self.left)
		delta_right = self.get_diff(self.neutral, self.right)
		self.get_sum(delta_left, delta_right)
		self.sett(self.sum)

	def gui(self):
		cmds.window('Sum R L', width=250)
		cmds.columnLayout( adjustableColumn=True )
		cmds.button( label='Get Neutral', command=self.get_neutral)
		cmds.button(label='Get L', command=self.get_left)
		cmds.button(label='Get R', command=self.get_right)
		cmds.button(label='Set', command=self.set_sum)
		cmds.showWindow()














