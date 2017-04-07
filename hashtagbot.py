# -*- coding: utf-8 -*-

import sys
import telepot
import random
import json
import os

from telepot.delegate import per_chat_id, create_open, pave_event_space


def do_main():
	print 'Telegram hashtag bot manager v1.0'
	start_bot(load_token())


def start_bot(token):
	bot = telepot.DelegatorBot(token, [
			pave_event_space()(per_chat_id(), create_open, MessageManager, timeout=30)
	])
	bot.message_loop(run_forever='Listening for messages...')


def load_token():
	with open('token.txt', 'r') as file:
		token = file.readline()
	return token


class MessageManager(telepot.helper.ChatHandler):
	def __init__(self, *args, **kwargs):
		super(MessageManager, self).__init__(*args, **kwargs)
		self.dummy_messages = self.load_dummy_messages()


	def load_dummy_messages(self):
		messages = []
		with open('dummy_messages.txt', 'r') as file:
			messages = file.readlines()
		return messages


	def on_chat_message(self, msg):
		text = msg['text']
		self.log_request(msg)

		if msg['chat']['type'] == 'group':
			if text.startswith('/show'):
				self.showhashtags(msg)
			elif text.startswith('/add'):
				self.addhashtag(msg)
			elif text.startswith('/delete'):
				self.deletehashtag(msg)
			else:
				self.sender.sendMessage(random.choice(self.dummy_messages))
		else:
			self.sender.sendMessage('Add me to some group to start working')
			image_path = os.path.join('img', 'alig.jpg')
			with open(image_path) as file:
				self.sender.sendPhoto(file)


	def log_request(self, msg):
		print '-' * 80
		print json.dumps(msg, indent=4, sort_keys=True)


	def showhashtags(self, msg):
		file_path = self.get_file_path(msg)
		data = {}
		with open(file_path, 'r') as file:
			data = json.load(file)
			message = self.get_msg_from_json(data)
			self.sender.sendMessage(message)


	def addhashtag(self, msg):
		file_path = self.get_file_path(msg)
		with open(file_path, 'r') as file:
			data = json.load(file)
			tag = self.get_parameter(msg, 1)
			hashtag = self.get_parameter(msg, 2)
			if tag in data:
				data[tag] += [hashtag]
			else:
				data.update({tag : [hashtag]})
			with open(file_path, 'w') as f:
				f.write(json.dumps(data))
				self.sender.sendMessage('Done')


	def get_parameter(self, msg, index):
		text = msg['text']
		arguments = text.split(' ')

		return arguments[index]


	def deletehashtag(self, msg):
		file_path = self.get_file_path(msg)
		with open(file_path, 'r') as file:
			data = json.load(file)
			hashtag = self.get_parameter(msg, 1)
			for key in data:
				values = data[key]
				if hashtag in values:
					values = [x for x in values if x != hashtag]
					if len(values) == 0:
						del data[key]
					else:
						data[key] = values
					break
			with open(file_path, 'w') as f:
				f.write(json.dumps(data))
				self.sender.sendMessage('Done')


	def get_file_path(self, msg):
		chat_id = msg['chat']['id']
		name_file = 'hashtags' + str(chat_id) + '.json'
		file_path = os.path.join('hashtags', name_file)
		if not os.path.exists('hashtags'):
			os.makedirs('hashtags')
			if not os.path.isfile(file_path):
				with open(file_path, 'w') as file:
					file.write('{}')

		return file_path


	def get_msg_from_json(self, data):
		message = ''
		for item in data:
			message += item + '\n\n'
			for value in data[item]:
				message += '#' + value + ', '
			else:
				message = message[:-2] + '\n\n'
		return message


do_main()