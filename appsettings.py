import json
import os.path


class AlphaStockSettings:
    recaptcha_secret = "secret"

    
    def create_settings(self, path):
        data = dict()
        data['recaptcha_secret'] = self.recaptcha_secret

        with open(path, 'w') as file:
            json.dump(data, file, indent=4)


    def load_settings(self, path):
        if not os.path.exists(path):
            print(f"설정 파일이 경로에 없음, '{path}'")
            return
        
        with open(path, 'r') as file:
            data = json.load(file)
            self.recaptcha_secret = data['recaptcha_secret']