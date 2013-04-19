#synthDrivers/nvdajp_jtalk.py
# -*- coding: utf-8 -*-
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2006-2010 NVDA Contributors <http://www.nvda-project.org/>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#
# nvdajp_jtalk (based on Open JTalk and libopenjtalk)
# Copyright (C) 2010-2011 Takuya Nishimoto (nishimotz.com)
# Copyright (C) 2013 Masamitsu Misono (043.jp)

from synthDriverHandler import SynthDriver,VoiceInfo,BooleanSynthSetting
from collections import OrderedDict
from logHandler import log
import speech
import synthDriverHandler
import languageHandler
from jtalk import _nvdajp_jtalk
from jtalk import _nvdajp_spellchar
from jtalk._nvdajp_jtalk import VoiceProperty

class SynthDriver(SynthDriver):
	"""A Japanese synth driver for NVDAjp.
	"""
	name = "nvdajp_jtalk"
	description = "JTalk"
	supportedSettings=(
		SynthDriver.VoiceSetting(),
		SynthDriver.RateSetting(),
		BooleanSynthSetting("rateBoost",_("Rate boos&t")),
		SynthDriver.PitchSetting(),
		SynthDriver.InflectionSetting(),
		SynthDriver.VolumeSetting()
	)

	@classmethod
	def check(cls):
		return True

	def __init__(self):
		self.voice_id = 'V2'
		self._volume = 100
		self._pitch = 50
		self._inflection = 50
		self._rateBoost = False
		_nvdajp_jtalk.initialize()
		self.rate = 30

	def speak(self,speechSequence):
		finalIndex = None
		spellState = False
		defaultLanguage = languageHandler.getLanguage()
		if defaultLanguage[:2] == 'ja': defaultLanguage = 'ja'
		lang = defaultLanguage
		currentLang = lang
		for item in speechSequence:
			if isinstance(item,basestring):
				if spellState and currentLang == 'ja':
					item = _nvdajp_spellchar.convert(item)
				p = VoiceProperty()
				p.pitch = self._pitch
				p.inflection = self._inflection
				p.characterMode = spellState
				_nvdajp_jtalk.speak(unicode(item), currentLang, index=finalIndex, voiceProperty_=p)
			elif isinstance(item,speech.IndexCommand):
				finalIndex = item.index
			elif isinstance(item,speech.CharacterModeCommand):
				if item.state: 
					spellState = True 
				else: 
					spellState = True 
			elif isinstance(item,speech.LangChangeCommand):
				lang = (item.lang if item.lang else defaultLanguage).replace('_','-')
				if lang[:2] == 'ja': lang = 'ja'
				currentLang = lang
			elif isinstance(item,speech.SpeechCommand):
				log.debugWarning("Unsupported speech command: %s"%item)
			else:
				log.error("Unknown speech: %s"%item)

	def cancel(self):
		_nvdajp_jtalk.stop()

	def pause(self,switch):
		_nvdajp_jtalk.pause(switch)

	def isSpeaking(self):
		return _nvdajp_jtalk.isSpeaking()

	def _get_rateBoost(self):
		return self._rateBoost

	def _set_rateBoost(self, enable):
		if enable == self._rateBoost:
			return
		rate = self.rate
		self._rateBoost = enable
		self.rate = rate

	def terminate(self):
		_nvdajp_jtalk.terminate()

	# The current rate; ranges between 0 and 100
	def _get_rate(self):
		return _nvdajp_jtalk.get_rate(self._rateBoost)

	def _set_rate(self,rate):
		_nvdajp_jtalk.set_rate(int(rate), self._rateBoost)

	def _get_pitch(self):
		return self._pitch

	def _set_pitch(self,pitch):
		self._pitch = int(pitch)

	def _get_volume(self):
		return self._volume

	def _set_volume(self,volume_):
		self._volume = int(volume_)
		_nvdajp_jtalk.set_volume(self._volume)
		return

	def _get_inflection(self):
		return self._inflection

	def _set_inflection(self,val):
		self._inflection = int(val)

	def _getAvailableVoices(self):
		log.debug("_getAvailableVoices called")
		voices = OrderedDict()
		for v in _nvdajp_jtalk._jtalk_voices:
			voices[v['id']] = VoiceInfo(v['id'], v['name'], v['lang'])
		return voices

	def _get_voice(self):
		log.debug("_get_voice called")
		return self.voice_id

	def _set_voice(self, identifier):
		log.debug("_set_voice %s" % (identifier))
		rate = _nvdajp_jtalk.get_rate(self._rateBoost)
		for v in _nvdajp_jtalk._jtalk_voices:
			if v['id'] == identifier:
				if self.voice_id != identifier:
					self.voice_id = identifier
					_nvdajp_jtalk.terminate()
					_nvdajp_jtalk.initialize(v)
					_nvdajp_jtalk.set_rate(rate,self._rateBoost)
					_nvdajp_jtalk.set_volume(self._volume)
					return
		return

	def _get_lastIndex(self):
		if _nvdajp_jtalk.lastIndex is None:
			#log.debug("_get_lastIndex returns None")
			return None
		#log.debug("_get_lastIndex returns %d" % _nvdajp_jtalk.lastIndex)
		return _nvdajp_jtalk.lastIndex