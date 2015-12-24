#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, logging, json
from grab.spider import Spider, Task
from grab import Grab

file_result = open('result.txt', 'w+')

class Yaplakal_Spider(Spider):
	base_url = ''
	get_request = 'st/%s/100/Z-A/last_post'
	results = []

	def get_int(self, str):
		return int(re.findall('(\d+)', str)[0])

	def get_count_page(self):
		g = Grab()
		g.go(self.base_url)
		str = g.doc.select('//div[@id="content-inner"]//table[2]//a')[-1].attr('title')
		count_page = self.get_int(str)

		return count_page

	def get_status(self, html):
		start = html.find('</a><br>')
		end = html.find('<br>', start + 8)
		result = html[start + 8:end]
		return result.strip()

	def get_registration_date(self, html):
		string_html = re.sub(r'\s', '', html)
		end = string_html.find('<br>')
		result = string_html[:end]
		result = result.replace(u'<divalign="left"style="padding-left:5px">\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f:', '')
		return result

	def get_count_messages(self, html):
		string_html = re.sub(r'\s', '', html)
		start = string_html.find('<br>')
		result = string_html[start + 4:]
		return self.get_int(result)

	def task_generator(self):
		count_page = self.get_count_page()
		count_post = 0

		for page in range(0, 1):
			yield Task('page', self.base_url + (self.get_request % count_post))
			count_post += 30

	def task_page(self, grab, task):
		for post in grab.doc.select('//div[@id="content-inner"]//form[1]//table//tr//a[@class="subtitle"]'):
			yield Task('post', post.attr('href'))

	def task_post(self, grab, task):
		url = task.url
		# author = {
		# 	'id': grab.doc.select('//div[@id="content-inner"]//span[@class="postdetails"]//a').attr('href'),
		# 	'login': grab.doc.select('//div[@id="content-inner"]//span[@class="normalname"]').text(),
		# }
		# answers = 0
		# views = self.get_int(grab.doc.select('//table[@class="activeuserstrip"]//td[2]').text())
		# rating = grab.doc.select('//div[contains(@class, "rating-value")]').text()
		# category = 'Лента/'.decode('utf-8') + grab.doc.select('//div[@id="navstrip"]//a')[-1].text()
		title = grab.doc.select('//h1[@class="subpage"]//a').text()
		# description = grab.doc.select('//h1[@class="subpage"]//span').text()[2:]

		post_data = {
			'url': url,
			# 'author': author,
			# 'answers': answers,
			# 'views': views,
			# 'rating': rating,
			# 'category': category,
			'title': title,
			# 'description': description,
		}
		# self.results.append(post_data)


		count_comments_page = grab.doc.select('//div[@id="content-inner"]//table[@class="row3"]').text()
		r_page = re.compile('[^()]+')
		count_comments_page = self.get_int(r_page.findall(count_comments_page)[1])
		url_list = url.split('/')
		count_comments = 0

		for comment in range(0, count_comments_page):
			comment_url = '{0}//{1}/{2}/st/{3}/{4}'.format(url_list[0], url_list[2], url_list[3], count_comments, url_list[-1])
			yield Task('comment', comment_url, post_data = post_data)
			count_comments += 25

	def task_comment(self, grab, task):
		count_comment = 1
		query_select = '//div[@id="content-inner"]//table//tr//td[1]//table[@class="tableborder"]//tr//td//form[1]//table['

		comment_list = []
		
		for commentt in grab.doc.select('//div[@id="content-inner"]//table//tr//td[1]//table[@class="tableborder"]//tr//td//form[1]//table'):
			id = grab.doc.select(query_select+str(count_comment)+']//a[1]').attr('name')
			login = grab.doc.select(query_select+str(count_comment)+']//span[@class="normalname"]').text()
			status = grab.doc.select(query_select+str(count_comment)+']//span[@class="postdetails"]').html()
			registration = grab.doc.select(query_select+str(count_comment)+']//span[@class="postdetails"]//div[1]').html()
			try:
				awards = grab.doc.select(query_select+str(count_comment)+']//span[@class="postdetails"]//div[2]//tr[2]//span[@class="postdetails"]').text()
			except:
				awards = ''
			date = grab.doc.select(query_select+str(count_comment)+']//a[@class="anchor"]').text()
			try:
				text = {
					'type': 'str',
					'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]').text()
				}
			except:
				text = ''
			try:
				img = {
					'type': 'img',
					'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]//img').attr('src'),
				}
			except:
				img = ''
			try:
				video = {
					'type': 'video',
					'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]//iframe').attr('src'),
				}
			except:
				video = ''


			# content = [
			# 	{
			# 		'type': 'str',
			# 		'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]').text()
			# 	},
			# 	{
			# 		'type': 'img',
			# 		'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]//img').attr('src'),
			# 	},
			# 	{
			# 		'type': 'video',
			# 		'value': grab.doc.select(query_select+str(count_comment)+']//div[@class="postcolor"]//iframe').attr('src'),
			# 	},
			# ]

			print(id)
			print(login)
			print(self.get_status(status))
			print(self.get_registration_date(registration))
			print(self.get_count_messages(registration))
			print(awards)
			print(date)
			print(text)
			print(img)
			print(video)
			print('///////////////')

			comment_list.append({
				'id': id,
				'author': {
					'login': login,
					'status': self.get_status(status),
					'registration': self.get_registration_date(registration),
					'number_comments': self.get_count_messages(registration),
					# 'awards': [
					# 	awards,
					# ],
				},
				# 'date': 'date',
				# 'content': content
			})
			count_comment += 1
			if count_comment > 3: break

		task.post_data.update({'comments': comment_list,})
		self.results.append(task.post_data)

if __name__ == '__main__':
	logging.basicConfig(level = logging.DEBUG, filename = 'logging.txt')
	g = Yaplakal_Spider(thread_number = 4)
	g.base_url = 'http://www.yaplakal.com/forum2/'
	g.run()
	jsonn = json.dumps(g.results)
	file_result.write(jsonn)
