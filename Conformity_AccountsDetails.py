import requests
import csv
from datetime import datetime

def unix_to_utc(unix_time):
    return datetime.utcfromtimestamp(int(unix_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')

def process_aws_accounts(data, current_utc_time):
    aws_accounts = [item for item in data if item['attributes']['cloud-type'] == 'aws']
    aws_data = []
    for account in aws_accounts:
        aws_data.append({
            'Account Name': account['attributes']['name'],
            'Environment': account['attributes']['environment'] or '',
            'Cloud Account ID': f"'{account['attributes']['awsaccount-id']}",
            'Creation Time': unix_to_utc(account['attributes']['created-date']),
            'Account size (consumption)': account['attributes']['consumption-tier'],
            'Current UTC Time': current_utc_time
        })
    return aws_data

def process_gcp_accounts(data, current_utc_time):
    gcp_accounts = [item for item in data if item['attributes']['cloud-type'] == 'gcp']
    gcp_data = []
    for account in gcp_accounts:
        gcp_data.append({
            'Project Name': account['attributes']['cloud-data']['gcp']['projectName'],
            'Environment': account['attributes'].get('meta', ''),
            'Cloud Account ID': account['attributes']['cloud-data']['gcp']['projectId'],
            'Creation Time': unix_to_utc(account['attributes']['created-date']),
            'Account size (consumption)': account['attributes']['consumption-tier'],
            'Current UTC Time': current_utc_time
        })
    return sorted(gcp_data, key=lambda x: x['Project Name'])

def write_to_csv(file_name, field_names, data):
    with open(file_name, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def main():
    region = input("Please enter your region: ")
    api_key = input("Please enter your API key: ")

    url = f"https://conformity.{region}.cloudone.trendmicro.com/api/accounts"
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': f'ApiKey {api_key}'
    }

    response = requests.get(url, headers=headers)
    data = response.json()['data']

    current_utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    aws_data = process_aws_accounts(data, current_utc_time)
    gcp_data = process_gcp_accounts(data, current_utc_time)

    current_utc_time_for_file = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    write_to_csv(f'AWSConformity_{current_utc_time_for_file}.csv', aws_data[0].keys(), aws_data)
    write_to_csv(f'GCPConformity_{current_utc_time_for_file}.csv', gcp_data[0].keys(), gcp_data)

if __name__ == "__main__":
    main()
