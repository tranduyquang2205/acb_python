import requests
import json
class ACB:
    def __init__(self, username, password, account_number):
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
        self.password = password
        self.username = username
        self.account_number = account_number

    def handleLogin(self):
        data = {
            'clientId': self.clientId,
            'username': self.username,
            'password': self.password
        }
        return self.curl_post(self.URL["LOGIN"], data)
    def get_balance(self):
        result = self.curl_get(self.URL["getBalance"])
        if 'data' in result:
            for account in result['data']:
                if self.account_number == account['accountNumber']:
                    return int(account['balance'])
            return None
        else: 
            return None

    def get_transactions(self, accountNo, rows):
        result = self.curl_get(f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/saving/tx-history?maxRows={rows}&account={accountNo}')
        return result

    def get_bank_info_func(self, bank_code, ben_account_number):
        result = self.curl_get(f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/accounts/{ben_account_number}?bankCode={bank_code}&accountNumber={self.account_number}')
        return result


    def load_user(self, username):
        # Implement database queries to load user here
        pass

    def login(self):
        if not self.username or not self.username:
            return {'code':400,'success': False, 'message': 'Vui lòng nhập đầy đủ thông tin'}
        user = self.load_user(self.username)

        res = self.handleLogin()
        if 'accessToken' in res:
            self.token = res['accessToken']
            data = json.dumps(res)
            if not user:
                # Implement database insert here
                pass
            else:
                # Implement database update here
                pass
            return {'code':200,'success': True, 'message': 'Đăng nhập thành công'}
        else:
            return {'code':444,'success': False, 'message': res['message']} 

    def get_bank_info(self,bank_code, ben_account_number):
        user = self.load_user(self.username)

        if not user:
            res = self.login()
            if not res['success']:
                return res
            user = self.load_user(self.username)

        res = self.get_bank_info_func(bank_code, ben_account_number)
        if 'codeStatus' in res and 'data' in res:
            return {'success': True, 'results': res['data']}

        if 'exp' in res or ('message' in res and res['message'] == 'Unauthorized'):
            res = self.login()
            if not res['success']:
                return res
            user = self.load_user(self.username)

        res = self.get_bank_info_func(bank_code, ben_account_number)

        if 'codeStatus' in res and 'data' in res:
            return {'success': True, 'results': res['data']}

        return {'success': False, 'message': 'Có lỗi xảy ra'}
    def curl_get(self, url):
        try:
            headers = self.header_null()
            response = requests.get(url, headers=headers, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return False

    def curl_post(self, url, data=None):
        try:
            headers = self.header_null()
            response = requests.post(url, headers=headers, json=data, timeout=60)
            result = response.json()
            return result
        except Exception as e:
            return e
    def header_null(self):
            header = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'vi',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json',
                'sec-ch-ua-mobile': '?0',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            }
            if self.token:
                header['Authorization'] = 'Bearer ' + self.token

            return header
    # def get_list_bank(self):
    #     url = 'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/banks'
    #     res =  self.curl_get(url)
    #     return res
    def get_list_bank(self):
        with open('acb_list_bank.json','r', encoding='utf-8') as f:
            data = json.load(f)
        return data 
    def transfer_limit(self, bankName, bank_code, ben_account_number):
        status = False
        message = 'Error exception'
        data = {}
        url = 'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/transaction-limits'

        params = {
            "accountNumber": self.account_number,
            "transferType": "1",
            "receivedBank": bankName,
            "napasBankCode": bank_code,
            "receivedAccountNumber": ben_account_number,
            "transferTime": {"type": 1, "period": 0, "startDate": 0, "endDate": 0},
            "receivedCardNumber": "",
            "receivedIdCardNumber": "",
            "receivedPassportNumber": ""
        }

        count = 0
        while True:
            limit = self.curl_post(url, params)
            if limit:
                data = limit
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()

            count += 1
            if count > 5:
                message = 'Connect false'
                break
        return {'success': status, 'message': message, 'data': data}
    def transfer(self, local, amount, partnerName, name_bank, comment, ben_account_number, bbank_code, bank_code):
        status = False
        message = 'Error exception'
        data = {}
        url = 'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/submit'
        type = 1 if bank_code == '970416' else 3
        params = {
                    "type": type,
                    "authMethod": "OTPA",
                    "menu": str(local),
                    "amount": int(amount),
                    "currency": "VND",
                    "fromAccount": self.account_number,
                    "transactionAmount": int(amount),
                    "receiverName": partnerName,
                    "bankName": name_bank,
                    "comment": comment,
                    "transferTime": {"type": 1, "period": 0, "startDate": 0, "endDate": 0},
                    "fee": 0,
                    "resultToEmails": [],
                    "accountInfo": {
                        "accountNumber": ben_account_number,
                        "bankCode": bbank_code,
                        "bankName": name_bank,
                        "napasBankCode": bank_code,
                        "bankcheckId": 0
                    },
                    "bankCode": bbank_code,
                    "napasBankCode": bank_code,
                    "referenceNumber": "",
                    "province": "",
                    "mbTransactionLimitInfo": {
                        "byPass": 0,
                        "bySMS": 0,
                        "byToken": 0,
                        "bySafeKey": 0,
                        "byAdvSafeKey": ''
                    }
                }

        count = 0
        while True:
            transfer = self.curl_post(url, params)
            if transfer:
                data = transfer
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()

            count += 1
            if count > 5:
                message = 'Connect false'
                break

        return {'success': status, 'message': message, 'data': data}



    def confirm_transfer(self, uuid, otp):
        status = False
        message = 'Error exception'
        data = {}
        url = 'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/verify'

        params = {
            'uuid': uuid,
            'code': otp,
            'authMethod': 'OTPA'
        }

        count = 0
        while True:
            confirm = self.curl_post(url, params)
            if confirm:
                data = confirm
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()

            count += 1
            if count > 5:
                message = 'Connect false'
                break

        return {'success': status, 'message': message, 'data': data}

    def get_detail(self):
        status = False
        message = 'Error exception'
        data = {}
        url = 'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/list/account-payment'

        count = 0
        while True:
            detail = self.curl_get(url)
            if detail:
                data = detail
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()

            count += 1
            if count > 5:
                message = 'Connect false'
                break

        return {'success': status, 'message': message, 'data': data}

    def get_bank_name(self, ben_account_number, bank_code):
        status = False
        message = 'Error exception'
        data = {}
        url = f'https://apiapp.acb.com.vn/mb/legacy/ss/cs/bankservice/transfers/accounts/{ben_account_number}?bankCode={bank_code}&accountNumber={self.account_number}'

        count = 0
        while True:
            bankName = self.curl_get(url)
            if bankName:
                data = bankName
                status = True
                message = 'Successfully'
                break
            else:
                login = self.login()

            count += 1
            if count > 5:
                message = 'Connect false'
                break

        return {'success': status, 'message': message, 'data': data}