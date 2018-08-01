import argparse
import json
import os.path
import pprint
import sys


def get_resource_types(directory_path):
    """
    to load ocf like resource type definition files under directory_path
    and transfer them to json and merge them into a json array which is
    friendly for mongo
    :param directory_path:
    :return: a json array includes all resource types
    """
    if not os.path.exists(directory_path):
        print("{} does not exist".format(directory_path))
        return

    rt_files = [root + '/' + filename
                for root, _, filenames in os.walk(directory_path)
                for filename in filenames
                if filename.endswith('.json')]
    pprint.pprint(rt_files)

    rt_contents = []
    for rt_file in rt_files:
        with open(rt_file, 'r') as f:
            content = json.load(f)
            rt_contents.append(content)

    # pprint.pprint(rt_contents)
    rt_mongo_jsons = transfer_2_mongo_json(rt_contents)

    return rt_mongo_jsons


def transfer_2_mongo_json(rt_contents):
    """
    to parse ocf like resource type definition, transfer it to
    mongo database documents
    :param rt_contents:
    :return: a json document
    """
    rt_mongo_jsons = []
    for rt_content in rt_contents:
        rt_mongo_json = {}
        res_def = rt_content.get('definitions', None)
        if res_def is None:
            print('no definitions from ' + str(rt_content))
            continue

        if 'rt' not in res_def:
            continue

        rt_mongo_json['n'] = res_def['rt']
        rt_mongo_json['d'] = res_def['rt']

        props_def = res_def.get('properties', [])
        props_mongo_json = []
        for prop_def in props_def:
            prop_mongo_json = {}

            if 'name' not in prop_def:
                continue

            prop_mongo_json['n'] = prop_def['name']
            prop_mongo_json['s'] = prop_def['name']

            if prop_def.get('readOnly', False):
                prop_mongo_json['a'] = 'r'
            else:
                prop_mongo_json['a'] = 'rw'

            prop_mongo_json['t'] = prop_def.get('type', 'opaque')
            prop_mongo_json['m'] = prop_def['name'] in rt_content.get(
                'required', [])

            props_mongo_json.append(prop_mongo_json)
        else:
            rt_mongo_json['ps'] = props_mongo_json

        rt_mongo_jsons.append(rt_mongo_json)

    return rt_mongo_jsons


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        "it is used to transfer resource type files into a list " \
        "which could be read and impoted by mongo")

    parser.add_argument('--rt_dir', dest='rt_dir',
                        action='store',
                        help="a path of the reource type directory")

    parser.add_argument('--out', dest='out_dir',
                        action='store',
                        default='.',
                        help="a path of directory to save result. by default, " \
                             "it is current directory")

    args = parser.parse_args()

    if args.rt_dir is None:
        sys.exit()

    rt_mongo_jsons = get_resource_types(args.rt_dir)
    output = args.out_dir + "/rt_for_mongo.json"
    with open(output, 'w') as f:
        json.dump(rt_mongo_jsons, f, indent=2)

    sys.exit()
