import os
import json
from pathlib import Path
from dotenv import load_dotenv
from exceptions.exceptions import InvalidJsonConfigFileException


class KalinanConfig:
    def __init__(self):
        try:
            self.login_url, self.reserve_url, self.dashboard_url, self.sms_notif, self.tele_notif = self._read_config()
            self.api_id, self.api_hash, self.token = self._read_env_config()
        except InvalidJsonConfigFileException:
            exit(2)

    def _read_env_config(self):
        load_dotenv(verbose=False)
        env_path = Path('./env') / '.env'
        load_dotenv(dotenv_path=str(env_path))

        api_id = os.getenv("API_ID")
        api_hash = os.getenv("API_HASH")
        token = os.getenv("TOKEN")

        return api_id, api_hash, token

    def _read_config(self):
        with open('./config/config.json') as f:
            data = json.load(f)

        if 'kalinan_login_url' not in data:
            raise InvalidJsonConfigFileException('kalinan_login_url')
        if 'kalinan_reservation_url' not in data:
            raise InvalidJsonConfigFileException('kalinan_reservation_url')
        if 'kalinan_dashboard_url' not in data:
            raise InvalidJsonConfigFileException('kalinan_dashboard_url')
        if 'tele_notif' not in data:
            raise InvalidJsonConfigFileException('tele_notif')
        if 'sms_notif' not in data:
            raise InvalidJsonConfigFileException('sms_notif')
        
        return data['kalinan_login_url'], data['kalinan_reservation_url'], data['kalinan_dashboard_url'] ,data['sms_notif'], data['tele_notif']