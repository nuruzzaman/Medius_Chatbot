#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ConfigParser
import shelve
import aiml
import jieba

class ChatBot:

    def __init__(self, config_file='config.cfg'):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.load_file = config.get('resource', 'load_file')
        self.save_file = config.get('resource', 'save_file')
        self.shelve_file = config.get('resource', 'shelve_file')

        # initialize
        jieba.initialize()

        self.mybot = aiml.Kernel()
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')

        self.template = '<aiml version="1.0" encoding="UTF-8">\n{rule}\n</aiml>'
        self.category_template = '<category><pattern>{pattern}</pattern><template>{answer}</template></category>'

    def response(self, message):

        if len(message) > 60:
            return self.mybot.respond('MAX')
        elif len(message) == 0:
            return self.mybot.respond('MIN')

        if message.find("*") != -1:
            return self.mybot.respond('filter')

        if message == 'exit' or message == 'quit':
            return self.mybot.respond('Good Bye')
        
        else:
            ########
            # AIML #
            ########
            result = self.mybot.respond(' '.join(jieba.cut(message)))

            # Matching mode
            if result[0] != '#':
                return result
            # Search mode 
            elif result.find('#NONE#') != -1:
                #########
                # WebQA #
                #########
                ans = crawl.search(message)
                if ans != '':
                    return ans.encode('utf-8')
                else:
                    ################
                    # Deep learing #
                    ################
                    ans = deep.tuling(message)
                    return ans.encode('utf-8')
            # Learning mode 
            elif result.find('#LEARN#') != -1:
                question = result[8:]
                answer = message
                self.save(question, answer)
                return self.mybot.respond('Already studied.')
            # check for BUG
            else:
                return self.mybot.respond('No Answer')

    def save(self, question, answer):
        db = shelve.open(self.shelve_file, 'c', writeback=True)
        db[question] = answer
        db.sync()
        rules = []
        for r in db:
            rules.append(self.category_template.format(pattern=r, answer=db[r]))
        with open(self.save_file, 'w') as fp:
            fp.write(self.template.format(rule='\n'.join(rules)))

    def forget(self):
        import os
        os.remove(self.save_file) if os.path.exists(self.save_file) else None
        os.remove(self.shelve_file) if os.path.exists(self.shelve_file) else None
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')


if __name__ == '__main__':
    bot = ChatBot()
    while True:
        message = raw_input('User > ')
        print 'Bot > ' + bot.response(message)
