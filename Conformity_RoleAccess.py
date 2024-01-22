import requests
import csv
from datetime import datetime
from collections import Counter

def format_access_level(access_level):
    words = access_level.split('-')
    return ' '.join(word.capitalize() for word in words)

def get_conformity_access(service_role_urns):
    conformity_urn_prefix = "urn:cloudone:conformity:au-1:406000301716:role/"
    for urn in service_role_urns:
        if conformity_urn_prefix in urn:
            return format_access_level(urn.split('/')[-1])
    return "No Access"

def count_users_by_role(url, headers):
    response = requests.get(url, headers=headers)
    users = response.json()['users']
    return Counter(user['roleID'] for user in users)

def main():
    api_key = input("Please enter your API key: ")

    headers = {
        'Api-Version': 'v1',
        'Authorization': f'ApiKey {api_key}'
    }

    roles_url = "https://accounts.cloudone.trendmicro.com/api/roles"
    local_users_url = "https://accounts.cloudone.trendmicro.com/api/users"
    saml_users_url = "https://saml.cloudone.trendmicro.com/api/saml-users"

    roles_response = requests.get(roles_url, headers=headers)
    roles_data = roles_response.json()['roles']

    local_users_count = count_users_by_role(local_users_url, headers)
    saml_users_count = count_users_by_role(saml_users_url, headers)

    total_counts = local_users_count + saml_users_count

    roles_info = []
    for role in roles_data:
        conformity_access = get_conformity_access(role['serviceRoleURNs'])
        user_count = total_counts.get(role['id'], 0)
        roles_info.append({
            'Role': role['name'],
            'Conformity Access': conformity_access,
            'Count of Users': user_count
        })

    current_utc_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    file_name = f'RoleConformityAccess_{current_date_utc}.csv'
    with open(file_name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Role', 'Conformity Access', 'Count of Users'])
        writer.writeheader()
        writer.writerows(roles_info)

    print(f"CSV file '{file_name}' has been created.")

if __name__ == "__main__":
    main()
