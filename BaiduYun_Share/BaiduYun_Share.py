import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ShareUrl = 'https://pan.baidu.com/share/'
PcsUrl = 'https://d.pcs.baidu.com/rest/2.0/pcs/'
#UserAgent = None
UserAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
#UserAgent = 'netdisk;5.3.4.5;PC;PC-Windows;5.1.2600;WindowsBaiduYunGuanJia'
DefaultHeaders = {
    'User-Agent': UserAgent,
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
}


class BYS(object):
    def __init__(self, access_token, **kwargs):
        self.access_token = access_token
        self.session = requests.Session()
        self.sslverify = False
        if 'headers' in kwargs:
            self.headers = kwargs['header']
        else:
            self.headers = DefaultHeaders

    def _request(self, method, url, data=None, token=True, **kwargs):
        kwnew = kwargs.copy()
        if 'headers' not in kwnew:  #add headers
            kwnew['headers'] = self.headers
        if token:
            if 'params' not in kwnew:  #add access_token
                kwnew['params'] = {}
            if 'access_token' not in kwnew['params']:
                kwnew['params']['access_token'] = self.access_token

        if method == 'get':
            return self.session.get(url, verify=False, **kwnew)
        elif method == 'post':
            return self.session.post(url, data=data, verify=False, **kwnew)

    def meta(self, path):
        url = PcsUrl + 'file'
        params = {
            'method': 'meta',
            'path': path
        }
        response = self._request('get',url, params=params)
        return json.loads(response.content.decode("utf-8"))

    def share(self, paths, pwd=None):
        """分享文件
        :param paths: 要分享的所有文件（夹）
        :type paths: list[]
        :param pwd: 分享密码，默认无密码
        :type pwd: str

        :return: 返回结果，json对象
            正确结果：
            {
                'errno': 0,
                'request_id': 请求id,
                'sharedid': 分享id,
                'link': 分享的长链接,
                'shortrul': 分享的短链接,
                'ctime': 分享时间,
                'premis': False
            }
        """
        url = ShareUrl + 'set'
        fid_list = []
        try:
            for path in paths:
                response = self.meta(path)
                #print(response)
                pid = response['list'][0]['fs_id']
                fid_list.append(pid)
        except KeyError:
            print("Error: sharing file: %s, errno: %s, error_msg: %s" % (path, response['error_code'],response['error_msg']))
        #print(fid_list)
        if pwd:
            data = {
                'fid_list': json.dumps(fid_list),
                'schannel': 4,
                'channel_list': '[]',
                'pwd': pwd
            }
        else:
            data = {
                'fid_list': json.dumps(fid_list),
                'schannel': 0,
                'channel_list': '[]'
            }
        response = self._request('post', url, data=data)
        return json.loads(response.content.decode("utf-8"))

    def list_share(self):
        """列出所有分享
        :return: 返回结果，json对象
            正确结果：
            {
                'errno': 0,
                'request_id': 请求id,
                'count': 分享数,
                'nextpage'： 0,
                'list':[{
                        'sharedId': 分享id
                        'passwd': 分享密码
                        'shortlink': 分享的短链接
                        ......
                        },
                        {},{}......
                        ]
            }
        """
        url = ShareUrl + 'record'
        response = self._request('get', url)
        return json.loads(response.content.decode("utf-8"))

    def cancel_share(self, shareids):
        """删除一个分享
        :param shareids: 分享id
        :type shareids: int

        :return: 返回结果，json对象
            正确结果：
            {
                'errno': 0
                'request_id': 请求id
                'err_msg': ''
            }
        """
        url = ShareUrl + 'cancel'
        data = {'shareid_list': json.dumps(shareids)}
        response = self._request('post', url, data=data)
        return json.loads(response.content.decode("utf-8"))

    def save_share(self, url, passwd):
        #TODO:save shared files from url
        pass