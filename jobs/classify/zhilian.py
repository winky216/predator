# -*- coding: utf-8 -*-
import functools

import precedure.zhilian
import jobs.classify.base
import storage.gitinterface

from sources.industry_sources import *
from sources.industry_needed import *
from sources.industry_id import *

class Zhilian(jobs.classify.base.Base):

    ff_profile = '/home/winky/.mozilla/firefox/rikqqhcg.default'

    def jobgenerator(self):
        
        zhilian = precedure.zhilian.Zhilian(wbdownloader = self.downloader)
        '''
        industry_list = [
                # ['129900', '大型设备/机电设备/重工业'],
                # ['121200', '仪器仪表及工业自动化'],
                # ['300000', '航空/航天研究与制造'],
                # ['150000', '交通/运输/物流'],
                # ['121500', '医疗设备/器械'],
                # ['210500', '互联网/移动互联网/电子商务'],
                # ['160400', '计算机软件'],
                # ['160000', 'IT服务（系统/数据/维护）'],
                # ['160500', '电子技术/半导体/集成电路'],
                # ['160200', '计算机硬件及网络设备'],
                # ['300100', '通信/电信（设备/运营/增值）'],
                ['121100', '加工制造（原料加工/模具）'],
                ['121300', '医药/生物工程'],
                ['130100', '电气/电力/水利'],
                ['120600', '学术/科研'],
                ['200300', '专业服务(咨询/财会/法律/翻译等)'],
                ['201300', '检验/检测/认证'],
                ['201400', '中介服务/外包服务']
                        ]
        '''
        jobtype_list = [
                ['160000', '全部(计算机/网络技术)'],
                ['410', '测试/可靠性工程师(电子/电气/半导体/仪器仪表)'],
                ['684', '射频工程师(电子/电气/半导体/仪器仪表)'],
                ['409', '项目管理/产品管理(电子/电气/半导体/仪器仪表)'],
                ['528', '研发工程师(电子/电气/半导体/仪器仪表)'],
                ['84', 'FAE现场应用工程师(电子/电气/半导体/仪器仪表)'],
                ['687', '嵌入式软件开发(Linux/单片机/DLC/DSP）(电子/电气/半导体/仪器仪表)'],
                ['407', '嵌入式硬件/软件工程师(电子/电气/半导体/仪器仪表)'],
                ['401', '设备工程师（调试/安装/维护）(电子/电气/半导体/仪器仪表)'],
                ['319', '机电工程师(电子/电气/半导体/仪器仪表)'],
                ['33', '自动化工程师(电子/电气/半导体/仪器仪表)'],
                ['467', '电气设计(电子/电气/半导体/仪器仪表)'],
                ['685', '工艺工程师(电子/电气/半导体/仪器仪表)'],
                ['249', '质量管理/测试经理(QA/QC经理)(质量管理/安全防护)'],
                ['250', '质量管理/测试主管(QA/QC主管)(质量管理/安全防护)'],
                ['251', '质量管理/测试工程师(QA/QC工程师)(质量管理/安全防护)'],
                ['253', '认证/体系工程师/审核员(质量管理/安全防护)'],
                ['295', '产品研发/注册(生物/制药/医疗器械)'],
                ['90', '技术文档工程师(工程机械)'],
                ['332', '工程机械经理/主管(工程机械)'],
                ['729', '工程/设备经理(工程机械)'],
                ['583', '工程/设备工程师(工程机械)'],
                ['584', '技术研发工程师(工程机械)'],
                ['732', '机电工程师(工程机械)'],
                ['734', '飞机维修机械师(工程机械)'],
                ['735', '飞行器设计与制造(工程机械)'],
                ['65', '生产总监/经理/车间主任(生产/加工/制造)'],
                ['63', '项目经理/主管(生产/加工/制造)'],
                ['66', '质量管理(生产/加工/制造)'],
                ['64', '生产主管/督导/组长(生产/加工/制造)'],
                ['72', '产品开发/技术/工艺(生产/加工/制造)'],
                ['735', '飞行器设计与制造(生产/加工/制造)'],
                ['245', '航空/列车/船舶操作维修(交通/物流/仓储)'],
                ['595', '飞机/列车/船舶设计与制造(交通/物流/仓储)'],
                # ['290', '核力/火力工程师(能源/矿产/地质勘查)'],
                # ['286', '电力工程师/技术员(能源/矿产/地质勘查)'],
                # ['158', '市场总监(市场/营销)'],
                # ['600', '市场经理/主管(市场/营销)'],
                # ['168', '品牌经理/主管(市场/营销)'],
                # ['7001000', '全部(销售管理/支持)'],
                # ['200', '财务总监(财务/审计/税务)'],
                # ['201', '财务经理(财务/审计/税务)'],
                # ['120', '人力资源总监(人力资源)'],
                # ['121', '人力资源经理/主管(人力资源)'],
                # ['128', '猎头顾问/助理(人力资源)'],
                # ['255', '科研人员(公务员/事业单位/科研机构)']
                        ]
        for industry in industry_needed:
            industry = industry.encode('utf-8')
            industryid = industryID[industry]
            zhilian_industry = industry_dict[industry]['zhilian']
            if len(zhilian_industry) == 0:
                continue
            for index in zhilian_industry:
                industry_id = index[0]
                industry_value = index[1]
                filename = industryid
                print '抓取的行业：' + industry_value
                postinfo = {
                    'industrys': industry_value
                            }
                for jobtype_item in jobtype_list:
                    print "正在抓取的职位: " + str(jobtype_item[1])
                    paramsdict = {
                            'CompanyIndustry':industry_id,
                            'JobType':jobtype_item[0]
                        }
                    header = self.get_header(paramsdict, postinfo)
                    print header
                    job_process = functools.partial(zhilian.update_classify,
                                                filename, filename,
                                                 paramsdict, self.repojt,header)
                    yield job_process

repo = storage.gitinterface.GitInterface('zhilian')
instance = Zhilian(repo)
PROCESS_GEN = instance.jobgenerator()

PLAN = [dict(second='*/6', hour='8-20'),
        dict(second='*/30', hour='21-23'),
        dict(minute='*/2', hour='0-6')]

