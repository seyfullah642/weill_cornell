def create_dummy_json(variant=None, error=None):
    response = []
    call = {}
    match = [{'relevance': 1, 'variants': 'NA',
              'therapies': [{'interpretation': '{}'.format(error), 'citations': [{'citation': '{}'.format(error)}],
                             'tier': '{}'.format(error)}]
              }]

    call['params'] = variant
    call['status'] = "1 matches"
    call['matches'] = match
    response.append(call)

    return response


if __name__ == '__main__':
    create_dummy_json()
