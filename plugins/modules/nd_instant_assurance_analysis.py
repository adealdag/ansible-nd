#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Alejandro de Alda (@adealdag) <adealdag@cisco.com>
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import time
import os
import json
from ansible_collections.cisco.nd.plugins.module_utils.ndi import NDI
from ansible_collections.cisco.nd.plugins.module_utils.nd import NDModule, nd_argument_spec
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: nd_instant_assurance_analysis
version_added: "0.1.0"
short_description: Manage instant online assurance analysis jobs
description:
- Manage instant online assurance analysis jobs on Cisco Nexus Dashboard Insights (NDI).
author:
- Alejandro de Alda (@adealdag)
options:
  insights_group:
    description:
    - The name of the insights group.
    type: str
    required: yes
    aliases: [ fab_name, ig_name ]
  site_name:
    description:
    - Name of the Assurance Entity.
    type: str
    required: yes
    aliases: [ site ]
  state:
    description:
    - Use C(present) for triggering an instant (on-demand) assurance analysis job.
    - Use C(query) for listing the history of instant assurance analysis jobs that are running or completed.
    type: str
    choices: [ present, query ]
    default: query
extends_documentation_fragment: cisco.nd.modules
'''

EXAMPLES = r'''
- name: Trigger instant assurance analysis job
  cisco.nd.nd_instant_assurance_analysis:
    insights_group: exampleIG
    site_name: siteName
    state: present
- name: Get history of instant assurance analysis
  cisco.nd.nd_instant_assurance_analysis:
    insights_group: exampleIG
    site_name: siteName
    state: query
  register: query_results
'''

RETURN = r'''
'''


def main():
    argument_spec = nd_argument_spec()
    argument_spec.update(
        insights_group=dict(type='str', required=True,
                            aliases=["fab_name", "ig_name"]),
        site_name=dict(type='str', required=True, aliases=["site"]),
        state=dict(type='str', default='query', choices=[
                   'query', 'present']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    nd = NDModule(module)
    ndi = NDI(nd)

    state = nd.params.get("state")
    insights_group = nd.params.get('insights_group')
    site_name = nd.params.get('site_name')

    if state == 'query':
        analysis_history = ndi.query_instant_assurance_analysis(
            insights_group, site_name)
        nd.existing = analysis_history

    elif state == 'present':
        if module.check_mode:
            nd.existing = {}

        trigger_path = ndi.config_ig_path + "/" + \
            ndi.run_analysis_ig_path.format(insights_group, site_name)
        resp = nd.request(trigger_path, method='POST', prefix=ndi.prefix)

        if resp["success"] is True:
            job_id = resp["value"]["data"]["configId"]
            analysis_history = ndi.query_instant_assurance_analysis(
                insights_group, site_name, job_id)
            if len(analysis_history) == 1:
                nd.existing = analysis_history[0]
            else:
                nd.fail_json(
                    msg="Instant Assurance Analysis trigger failed. Job {0} not found after creation".format(job_id))
        else:
            nd.fail_json(
                msg="Instant Assurance Analysis trigger failed")

    nd.exit_json()


if __name__ == "__main__":
    main()
