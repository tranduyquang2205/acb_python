import requests
import json
class ACB:
    def __init__(self):
        self.connect = None  # You can initialize your database connection here
        self.clientId = 'iuSuHYVufIUuNIREV0FB9EoLn9kHsDbm'
        self.URL = {
            "LOGIN": "https://apiapp.acb.com.vn/mb/auth/tokens",
            "getBalance": "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment",
            "INFO": "https://mobile.mbbank.com.vn/retail_lite/loan/getUserInfo",
            "GET_TOKEN": "https://mobile.mbbank.com.vn/retail_lite/loyal/getToken",
            "GET_NOTI": "https://mobile.mbbank.com.vn/retail_lite/notification/getNotificationDataList",
            "GET_TRANS": "https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/saving/tx-history?maxRows=20&account=4650511"
        }
        self.token = ""

    def handleLogin(self, username, password):
        header = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'apiapp.acb.com.vn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.26 Safari/537.36 Edg/85.0.564.13',
        }
        data = {
            'clientId': self.clientId,
            'username': username,
            'password': password
        }
        return self.curl("LOGIN", header, data)

    def get_balance(self):
        header = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'apiapp.acb.com.vn',
            'Authorization': f'Bearer {self.token}',
        }
        result = self.curl("getBalance", header, data=None)
        return json.dumps(result)

    def get_transactions(self, accountNo, rows):
        header = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'apiapp.acb.com.vn',
            'Authorization': f'Bearer {self.token}',
        }
        result = self.curl2(f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/saving/tx-history?maxRows={rows}&account={accountNo}', header, data=None)
        return result

    def curl2(self, action, header, data):
        data = json.dumps(data) if isinstance(data, dict) else data
        headers = header
        proxy = {'http': 'http://linhvudieu329:l0Ks3Jp@103.189.79.189:38866', 'https': 'http://linhvudieu329:l0Ks3Jp@103.189.79.189:38866'}

        if data:
            response = requests.post(action, headers=headers, data=data,proxies=proxy)
        else:
            response = requests.get(action, headers=headers, data=data,proxies=proxy)
        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def get_bank_info(self, bankCode, accountNumber, accountNo, token):
        header = {
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'apiapp.acb.com.vn',
            'Authorization': f'Bearer {token}',
        }
        result = self.curl2(f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/accounts/{accountNumber}?bankCode={bankCode}&accountNumber={accountNo}', header, data=None)
        return result

    def curl(self, action, header, data):
        proxy = {'http': 'http://linhvudieu329:l0Ks3Jp@103.189.79.189:38866', 'https': 'http://linhvudieu329:l0Ks3Jp@103.189.79.189:38866'}
        data = json.dumps(data) if isinstance(data, dict) else data
        url = self.URL[action]
        headers = header
        headers['Content-Type'] = 'application/json; charset=utf-8'
        headers['accept'] = 'application/json'
        headers['Content-Length'] = str(len(data)) if data else '0'
        if data:
            response = requests.post(url, headers=headers, data=data,proxies=proxy)
        else:
            response = requests.get(url, headers=headers, data=data,proxies=proxy)

        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def load_user(self, username):
        # Implement database queries to load user here
        pass

    def login(self, username, password):
        if not username or not password:
            return {'success': 0, 'msg': 'Vui lòng nhập đầy đủ thông tin'}
        user = self.load_user(username)

        res = self.handleLogin(username, password)
        if 'accessToken' in res:
            self.token = res['accessToken']
            data = json.dumps(res)
            if not user:
                # Implement database insert here
                pass
            else:
                # Implement database update here
                pass
            return {'success': 1, 'msg': 'Đăng nhập thành công'}
        else:
            return {'success': 0, 'msg': res['message']} 

    def get_bank_info(self, username, password, bankCode, accountNumber, accountNo):
        user = self.load_user(username)

        if not user:
            res = self.login(username, password)
            if not res['success']:
                return res
            user = self.load_user(username)

        res = self.get_bank_info(bankCode, accountNumber, accountNo, user['token'])
        if 'codeStatus' in res and 'data' in res:
            return {'success': 1, 'results': res['data']}

        if 'exp' in res or ('message' in res and res['message'] == 'Unauthorized'):
            res = self.login(username, password)
            if not res['success']:
                return res
            user = self.load_user(username)

        res = self.get_bank_info(bankCode, accountNumber, accountNo, user['token'])

        if 'codeStatus' in res and 'data' in res:
            return {'success': 1, 'results': res['data']}

        return {'success': 0, 'msg': 'Có lỗi xảy ra'}
