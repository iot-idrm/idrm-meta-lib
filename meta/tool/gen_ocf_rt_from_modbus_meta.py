import argparse
import json
import os
import shutil
import sys

OCF_LIKE_DEFINITION = {
    'title': None,
    'definitions': None,
    'required': [],
}

OCF_LIKE_DEFINITION_RESOURCE = {
    'rt': None,
    'description': None,
    'properties': []
}

OCF_LIKE_DEFINITION_PROPERTY = {
    'name': None,
    'type': None,
    'description': None,
    'readOnly': False,
    'ext': []
}

OCF_LIKE_DEFINITION_EXT = {
    'ext_n': None,
    'ext_v': None
}


def get_resource_type_from_modbus_type(modbus_meta_cfg_path):
    """
    to load modbus_meta.cfg files under modbus_meta_cfg_path
    and transfer modbus_meta.cfg content to ocf like resource
    type definitions and merge them together and remove
    duplicated definitions
    :param modbus_meta_cfg_path:
    :return:
    """
    if not os.path.exists(modbus_meta_cfg_path):
        print(modbus_meta_cfg_path + " does not exist")
        return None

    modbus_meta_cfg_files = [root + '/' + filename
                             for (root, _, filenames) in os.walk(modbus_meta_cfg_path)
                             for filename in filenames]
    modbus_meta_cfg_files = [os.path.normpath(file_path)
                             for file_path in modbus_meta_cfg_files
                             if file_path.endswith('.cfg')]

    tmp = [parse_modbus_type_file(cfg_file)
           for cfg_file in modbus_meta_cfg_files]
    ocf_like_rt_def = {key: i[key] for i in tmp for key in i.keys()}
    return ocf_like_rt_def


def parse_modbus_type_file(cfg_file):
    """
    to load modbus_meta.cfg content as JSON and parse them
    :param cfg_file:
    :return:
    """
    with open(cfg_file, 'r') as f:
        info = json.load(f)
        return parse_resource_type_from_modbus_type(info)


def parse_resource_type_from_modbus_type(json):
    """
    to transfer json objects from modbus_meta.cfg into
    ocf like resource type definitions
    :param json:
    :return:
    """
    rts_info = {}

    for res in json['links']:
        # rt is a list here
        for res_t in res['rt']:
            ocf_like_rt = OCF_LIKE_DEFINITION.copy()
            cur_rt_item = OCF_LIKE_DEFINITION_RESOURCE.copy()
            ocf_like_rt['definitions'] = cur_rt_item
            ps_list = []
            required_list = []

            cur_rt_item['description'] = res_t
            cur_rt_item['rt'] = res_t

            for prop in res['p']:
                if 'n' not in prop:
                    continue

                if prop.get('m', False):
                    required_list += prop['n']

                if 'inst' in prop:
                    for i in range(int(prop['inst'])):
                        prop_name = "{}/{}".format(prop.get('n'), i)
                        ps_list.append(generate_property_from_modbus_def(
                            prop_name,
                            prop.get('vt', 's'),
                            prop.get('if', False)))
                else:
                    ps_list.append(generate_property_from_modbus_def(
                        prop.get('n'),
                        prop.get('vt', 's'),
                        prop.get('if', False)))
            else:
                cur_rt_item['properties'] = ps_list

            rts_info[res_t] = ocf_like_rt

    return rts_info


def generate_property_from_modbus_def(prop_name, prop_type='i',
                                      prop_if='r'):
    """
    to transfer 'p' fields of modbus_meta.cfg into 'properties'
    fileds of ocf like resource type definitions
    :param prop_name:
    :param prop_type:
    :param prop_if:
    :return:
    """
    cur_ps_item = OCF_LIKE_DEFINITION_PROPERTY.copy()

    cur_ps_item['name'] = prop_name
    cur_ps_item['description'] = prop_name

    if prop_if is 'r':
        cur_ps_item['readOnly'] = True
    else:
        cur_ps_item['readOnly'] = False

    if prop_type is 's':
        cur_ps_item['type'] = 'string'
    else:
        cur_ps_item['type'] = 'int'

    return cur_ps_item


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        "it is used to generate a ocf like resource type definition" \
        "from modbus_meta.cfg")

    parser.add_argument('--modbus_meta_dir', dest='modbus_meta_dir',
                        action='store',
                        default='..',
                        help="a path of modbus type files, like ../modbus-type")

    parser.add_argument('--out', dest='out_dir',
                        action='store',
                        default='../out',
                        help="a path of directory to save result. by default, " \
                             "it is ../out")

    args = parser.parse_args()
    if args.modbus_meta_dir is None:
        sys.exit()

    rt_collection = get_resource_type_from_modbus_type(args.modbus_meta_dir)
    if rt_collection is None or len(rt_collection) == 0:
        print("get an empty rt collection from " + args.modbus_meta_dir)
        sys.exit()

    if not os.path.exists(args.out_dir):
        os.mkdir(args.out_dir)
    else:
        shutil.rmtree(args.out_dir)
        os.mkdir(args.out_dir)

    for rt in rt_collection:
        output = '{}/{}.json'.format(args.out_dir, rt)
        with open(output, 'w') as f:
            json.dump(rt_collection[rt], f, indent=2)

    sys.exit()
