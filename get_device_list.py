import asyncio
import aiohttp
import json
import csv

from okta.client import Client as OktaClient
from okta import models

class GetWorkspaceOneDevices:
    def __init__(self, config_file):
        # Load configuration from a JSON file
        self.config = json.load(open(config_file))
        # Connect to Okta
        self.okta_client = OktaClient({
            'orgUrl': self.config['okta_org_url'],
            'token': self.config['okta_token']
        })

    async def fetch_token_info(self, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()
            
    async def get_token(self):
        headers = {
            'grant_type': 'client_credentials',
            'client_id': self.config['CLIENT_ID'],
            'client_secret': self.config['CLIENT_SECRET']
        }
        response_json = await self.fetch_token_info(self.config['TOKEN_URL'], headers)
        return response_json['access_token']

    async def fetch_device_info(self, url, headers):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()

    async def fetch_device_info_by_id(self, url, headers):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
            
    async def get_device_info_by_id(self, device_id):
        bearer_token = await self.get_token()
        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {bearer_token}",
            'aw-tenant-code': self.config['API_TOKEN']
        }
        url = self.config['DEVICE_BY_ID_URL'] + str(device_id)
        response_json = await self.fetch_device_info_by_id(url, headers)
        return response_json['DeviceReportedName'], \
               response_json['UserEmailAddress'], \
               response_json['Model']

    async def get_devices(self):
        all_data_active = []
        all_data_inactive = []
        bearer_token = await self.get_token()
        headers = {
            'Accept': 'application/json',
            'Authorization': f"Bearer {bearer_token}",  
            'aw-tenant-code': self.config['API_TOKEN']
        }
        response_json = await self.fetch_device_info(self.config['WORKSPACEONE_URL'], headers)
        print(f"{'USERNAME':<25} {'USER STATUS':<15} {'SERIAL NUMBER':<25} " \
              f"{'MODEL':<65} {'PLATFORM':<15} {'ASSET NUMBER':<15}")
        for device in response_json['EnrolledDeviceInfoList']:
            hostname, email, model = await self.get_device_info_by_id(device['DeviceID'])
            try:
                user, _, _ = await self.okta_client.get_user(email)
                user_status = user.status
            except Exception:
                user_status = f"404: Not Found"
            try:
                print(f"{device['UserName'].lower():<25} {user_status:<15} {device['SerialNumber']:<25} " \
                    f"{model:<65} {device['Platform']:<15} {device['AssetNumber']:<15}")
            except Exception as e:
                pass
            # Assigns the data to variable and appends it into json/csv logs
            device_data = [device['UserName'].lower(), user_status, device['FriendlyName'], device['SerialNumber'],
                           model, device['Platform'], device['AssetNumber'], device['DeviceID']]
            if user_status == 'ACTIVE':
                all_data_active.append((email, device_data))
            else:
                all_data_inactive.append((email, device_data))

        # Creates csv and json logs
        with open('active_user_devices.csv', 'w', newline='') as csvfile_active:
            fieldnames = ['username', 'user_status', 'device_name', 'serial_number',
                          'model', 'platform', 'asset_number', 'device_id']
            writer_active = csv.writer(csvfile_active)
            writer_active.writerow(fieldnames)
            writer_active.writerows([data for _, data in all_data_active])

        active_data_dicts = [{email: dict(zip(fieldnames, data))} for email, data in all_data_active]
        with open('active_user_devices.json', 'w') as jsonfile:
            json.dump(active_data_dicts, jsonfile, indent=4)
            
        with open('inactive_user_devices.csv', 'w', newline='') as csvfile_inactive:
            fieldnames = ['username', 'user_status', 'device_name', 'serial_number', 'model',
                          'platform', 'asset_number', 'device_id']
            writer_inactive = csv.writer(csvfile_inactive)
            writer_inactive.writerow(fieldnames)
            writer_inactive.writerows([data for _, data in all_data_inactive])

        inactive_data_dicts = [{email: dict(zip(fieldnames, data))} for email, data in all_data_inactive]
        with open('inactive_user_devices.json', 'w') as jsonfile:
            json.dump(inactive_data_dicts, jsonfile, indent=4)

async def main():
    config_file = 'config.json'
    get_devices = GetWorkspaceOneDevices(config_file)
    await get_devices.get_devices()

if __name__ == '__main__':
    asyncio.run(main())
