# -*- coding: utf-8 -*-
import re
import logging
import functools

import utils.builtin
import precedure.liepin
import jobs.definition.cloudshare

from utils.utils_parsing import *
from sources.industry_id import *

class Liepin(jobs.definition.cloudshare.Cloudshare):

    JTDB_PATH = 'liepin'
    CVDB_PATH = 'output/liepin'
    FF_PROFILE_PATH = '/home/followcat/.mozilla/firefox/yffp11op.followcat'
    PRECEDURE_CLASS = precedure.liepin.Liepin

    def cloudshare_yaml_template(self):
        template = super(Liepin, self).cloudshare_yaml_template()
        template['origin'] = u'猎聘爬取'
        return template

    def jobgenerator(self, industry_needed):
        for classify_value in industry_needed:
            classify_id = industryID[classify_value.encode('utf-8')]
            try:
                self.urlsfile = self.jtstorage.get(classify_id)
                self.urlsdata = self.urlsfile['datas']
            except Exception:
                continue
            sorted_id = sorted(self.urlsdata,
                           key = lambda cvid: self.urlsdata[cvid]['peo'][-1],
                           reverse=True)
            for cv_id in sorted_id:
                if not self.cvstorage.existscv(cv_id):
                    if 'Nocontent' not in self.urlsdata[cv_id] or not self.urlsdata[cv_id]['Nocontent']:
                        cv_info = self.urlsdata[cv_id]
                        job_process = functools.partial(self.downloadjob, cv_info, classify_id)
                        yield job_process
                else:
                    try:
                        yamlload = utils.builtin.load_yaml('output/liepin/RAW', cv_id+'.yaml')
                    except IOError:
                        continue
                    try:
                        yamlload.pop('tag')
                    except KeyError:
                        pass
                    yamlload['tags'] = self.urlsdata[cv_id]['tags']
                    resultpath = self.cvstorage.addyaml(cv_id, yamlload)

    def downloadjob(self, cv_info, classify_id):
        job_logger = logging.getLogger('schedJob')
        cv_id = cv_info['id']
        print('Download: '+cv_id)
        try:
            cv_content =  self.precedure.cv(cv_info['href'])
            cvresult = True
        except precedure.liepin.NocontentCVException:
            print('Failed! Download: '+cv_id)
            self.urlsdata[cv_id]['Nocontent'] = True
            self.jtstorage.modify_data(classify_id, self.urlsdata,
                                       message='Add Nocontent to: '+cv_id)
            cvresult = False
        if cvresult is True:
            yamldata = self.extract_details(cv_info, cv_content)
            cvresult = self.cvstorage.addcv(cv_id, cv_content.encode('utf-8'), yamldata)
            job_logger.info('Download: '+cv_id)
        else:
            job_logger.info('Failed! Download: '+cv_id)
        return cvresult

    def extract_details(self, uploaded_details, cv_content):
        details = super(Liepin, self).extract_details(uploaded_details)
        if not details['name']:
            details['name'] = uploaded_details['name']
        if not details['age']:
            try:
                details['age'] = int(re.compile('[0-9]*').match(uploaded_details['peo'][2]).group())
            except ValueError:
                details['age'] = re.compile('[0-9]*').match(uploaded_details['peo'][2]).group()
        add_cr = lambda x:'\n'+x.group()
        for education in re.compile(STUDIES, re.M).finditer(re.compile(PERIOD).sub(add_cr, uploaded_details['info'][0])):
            if not details['school']:
                details['school'] = education.group('school').replace('\n', '')\
                                       .replace('\t', '').replace('\r', '').replace(' ', '')
            if not details['education']:
                details['education'] = education.group('education').replace('\n', '')\
                                       .replace('\t', '').replace('\r', '').replace(' ', '')
        if (not details['experience'] or
            re.match(TODAY, details['experience'][0][1]) and not details['position']):
            for expe in uploaded_details['info']:
                for w in re.compile(WORKXP, re.M).finditer(re.compile(PERIOD).sub(add_cr, expe)):
                    details['experience'].append((fix_date(w.group('from')), fix_date(w.group('to')),
                        fix_name(w.group('company'))+'|'+fix_name(w.group('position'))+'('+fix_duration(w.group('duration'))+')'))
            if details['experience'] and re.match(TODAY, details['experience'][0][1]) is not None:
                details['company'] = uploaded_details['peo'][7]
                details['position'] = uploaded_details['peo'][6]
                if u'…' in details['company']:
                    no_braket = lambda x:x.replace('(','').replace(')','')
                    escape_star = lambda x:x.replace('*','\*')
                    RE = re.compile(escape_star(no_braket(details['company'])[:-1]))
                    xp = details['experience'][0]
                    if RE.match(no_braket(xp[2])):
                        details['company'] = xp[2].split('|')[0]

        if not details['tags']:
            details['tags'] = uploaded_details['tags']

        return details
