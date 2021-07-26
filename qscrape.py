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


def get_answers_from_uid(uid, page='0', collected_answers=None):
    answers = collected_answers if collected_answers is not None else []
    graphql_json['variables']['uid'] = uid
    graphql_json['variables']['after'] = page
    answer_request = requests.post(url=graphql_url, json=graphql_json, headers=headers)
    answer_response = answer_request.json()

    combined_profile_feed = answer_response['data']['user']['combinedProfileFeedConnection']
    page_info = combined_profile_feed['pageInfo']
    edges = combined_profile_feed['edges']

    for edge in edges:
        answers.append(extract_answer_from_edge(edge))

    return get_answers_from_uid(uid, page_info['endCursor'], answers) if page_info['hasNextPage'] else answers


def get_uid_from_profile_url(profile_url):
    profile_request = requests.get(url=profile_url)
    pattern = re.compile(".*window.ansFrontendRelayWebpackIncludedChunks.*\"uid\": (\\d+).*")
    results = pattern.search(profile_request.text).group(1)
    return int(results)


def write_answers_to_file(answers):
    pattern = re.compile("https://www.quora.com/profile/(.*)")
    file = open(pattern.search(sys.argv[1]).group(1) + '-Answers.txt', 'w+', encoding='utf-8')
    for answer in answers:
        file.write(answer['question'].upper() + '\n')
        file.write(answer['answer'] + '\r\n\n')

    file.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_id = get_uid_from_profile_url(sys.argv[1])
        all_answers = get_answers_from_uid(user_id)
        write_answers_to_file(all_answers)
    else:
        print('No profile URL was supplied')



