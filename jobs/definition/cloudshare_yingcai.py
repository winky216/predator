# -*- coding: utf-8 -*-
import re
import bs4
import time
import datetime
import logging
import datetime
import functools

import utils.builtin
import precedure.yingcai
import jobs.definition.cloudshare

from sources.industry_id import *

class Yingcai(jobs.definition.cloudshare.Cloudshare):

    CVDB_PATH = 'output/yingcai'
    FF_PROFILE_PATH_LIST = [
                           '/home/winky/.mozilla/firefox/4idae7tm.winky3',
                           '/home/winky/.mozilla/firefox/jvqqz5ch.winky',
                           '/home/winky/.mozilla/firefox/bs9yw52t.winky2'
                            ]
    profilepath_index=0
    FF_PROFILE_PATH=FF_PROFILE_PATH_LIST[profilepath_index]
    PRECEDURE_CLASS = precedure.yingcai.Yingcai
    START_TIME=datetime.datetime.now()

    def cloudshare_yaml_template(self):
        template = super(Yingcai, self).cloudshare_yaml_template()
        template['origin'] = u'中华英才爬取'
        return template

    def jobgenerator(self, industry_needed):
        for _classify_value in industry_needed:
            _classify_id = industryID[_classify_value.encode('utf-8')]
            print _classify_id
            _file = _classify_id + '.yaml'
            try:
              yamlfile = utils.builtin.load_yaml('yingcai/JOBTITLES', _file)
              yamldata = yamlfile['datas']
            except Exception:
                continue
            sorted_id = sorted(yamldata,
                               key = lambda cvid: yamldata[cvid]['info'][-1],
                               reverse=True)
            for cv_id in sorted_id:
                if not self.cvstorage.existscv(cv_id):
                    cv_info = yamldata[cv_id]
                    job_process = functools.partial(self.downloadjob, cv_info, _classify_id)
                    t1 = time.time()
                    yield job_process
                else:
                    try:
                        yamlload = utils.builtin.load_yaml('output/yingcai/RAW', cv_id+'.yaml')
                    except IOError:
                        continue
                    try:
                        yamlload.pop('tag')
                    except KeyError:
                        pass
                    yamlload['tags'] = yamldata[cv_id]['tags']
                    resultpath = self.cvstorage.addyaml(cv_id, yamlload)

                current_time=datetime.datetime.now()
                duration=(current_time-self.START_TIME).seconds
                if duration > 1800:
                    self.wb_downloader.close()
                    time.sleep(1)
                    self.profilepath_index+=1
                    self.FF_PROFILE_PATH=self.FF_PROFILE_PATH_LIST[self.profilepath_index%len(self.FF_PROFILE_PATH_LIST)]
                    self.wb_downloader = self.get_wb_downloader(self.FF_PROFILE_PATH)
                    self.precedure = self.PRECEDURE_CLASS(wbdownloader=self.wb_downloader)
                    self.START_TIME=current_time
                else:
                    continue

    def downloadjob(self, cv_info, classify_id):
        job_logger = logging.getLogger('schedJob')
        cv_id = cv_info['id']
        print('Download: '+cv_id)
        print (cv_info['href'])
        cv_content =  self.precedure.cv(cv_info['href'])
        yamldata = self.extract_details(cv_info, cv_content)
        result = self.cvstorage.addcv(cv_id, cv_content.encode('utf-8'), yamldata)
        job_logger.info('Download: '+cv_id)
        result = True

    def extract_details(self, uploaded_details, cv_content):
        details = super(Yingcai, self).extract_details(uploaded_details)
        soup=bs4.BeautifulSoup(cv_content,'lxml')

        if not details['name']:
            name = uploaded_details['name']
            if len(name) == 0:
                details['name'] = uploaded_details['id']
            else:
                details['name'] = uploaded_details['name']

        if not details['age']:
            age = uploaded_details['info'][0]
            age_pattern = re.compile(r'(\d+)')
            details['age'] = int(re.findall(age_pattern, age)[0])

        if not details['education']:
            details['education'] = uploaded_details['info'][2].strip()

        if not details['tags']:
            details['tags'] = uploaded_details['tags']
        
        return details
