import platform
import re
import requests
import json
import sys

graphql_url = 'https://www.quora.com/graphql/gql_para_POST?q=UserProfileCombinedListQuery'

headers = {
        'Content-Type': 'application/json',
        'Cookie': 'm-b=BfoLuH6Z05auB68F79zmxg==;',
        'Quora-Formkey': '87353ce39798d6def9ec0efa21c77424'
}

graphql_json = {
        'queryName': 'UserProfileCombinedListQuery',
        'extensions': {'hash': '44cd9b2a5c236b42c2cba161b14214dbffdb192e83770a625b6839bd2b0d8361'},
        'variables': {'order': 1, 'first': 20, 'after': '0'}
}


def extract_answer_from_edge(edge):
    content = json.loads(edge['node']['answer']['content'])
    question = json.loads(edge['node']['answer']['question']['title'])
    answer = ''

    for i in range(len(content['sections'])):
        answer += content['sections'][i]['spans'][0]['text']

    return {'question': question['sections'][0]['spans'][0]['text'], 'answer': answer}


def get_total_answers_and_posts(uid, page='10000000'):
    graphql_json['variables']['uid'] = uid
    graphql_json['variables']['after'] = page
    answer_request = requests.post(url=graphql_url, json=graphql_json, headers=headers)
    answer_response = answer_request.json()

    end_cursor = answer_response['data']['user']['combinedProfileFeedConnection']['pageInfo']['endCursor']
    return int(end_cursor) if end_cursor is not page else get_total_answers_and_posts(uid, '1000000000')


def get_answers_from_uid(uid, page='0', collected_answers=None, total_answers=0, answers_downloaded=0):
    answers = collected_answers if collected_answers is not None else []
    graphql_json['variables']['uid'] = uid
    graphql_json['variables']['after'] = page
    answer_request = requests.post(url=graphql_url, json=graphql_json, headers=headers)
    answer_response = answer_request.json()

    combined_profile_feed = answer_response['data']['user']['combinedProfileFeedConnection']
    page_info = combined_profile_feed['pageInfo']
    edges = combined_profile_feed['edges']
    
    for edge in edges:
        if edge['node'].__contains__('answer'):
            answers.append(extract_answer_from_edge(edge))

        answers_downloaded += 1
        sys.stdout.write('\rProcessing {} of {} total items..'.format(answers_downloaded, total_answers))

    return get_answers_from_uid(uid, page_info['endCursor'], answers, total_answers, answers_downloaded) if page_info['hasNextPage'] else answers


def get_uid_from_profile_url(profile_url):
    profile_request = requests.get(url=profile_url)
    pattern = re.compile(".*window.ansFrontendRelayWebpackIncludedChunks.*\"uid\": (\\d+).*")
    results = pattern.search(profile_request.text).group(1)
    return int(results)


def write_answers_to_file(answers):
    pattern = re.compile("https://www.quora.com/profile/([\\w\\-]+).*")
    file = open(pattern.search(sys.argv[1]).group(1) + '-Answers.txt', 'w+', encoding='utf-8')
    for answer in answers:
        file.write(answer['question'].upper() + '\n')
        file.write(answer['answer'] + '\r\n\n')

    file.close()


def is_windows():
    return platform.system() == 'Windows'


if __name__ == '__main__':
    profile_pattern = re.compile("https://www\\.quora\\.com/profile/[\\w\\-]+.*")
    if len(sys.argv) > 1 and profile_pattern.match(sys.argv[1]):
        user_id = get_uid_from_profile_url(sys.argv[1])
        answers_total = get_total_answers_and_posts(user_id)
        all_answers = get_answers_from_uid(user_id, total_answers=answers_total)
        write_answers_to_file(all_answers)
    else:
        print('Usage: {} https://www.quora.com/profile/<profile-name>'.format('qscrape' if is_windows() else './qscrape'))



