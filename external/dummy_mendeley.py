#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mendeley_client import MendeleyClient

# Renomeie o arquivo para mendeley.py após adicionar as chaves abaixo!
mendeley = MendeleyClient('<consumer_key>', '<secret_key>')

try:
    mendeley.load_keys()
except IOError:
    mendeley.get_required_keys()
    mendeley.save_keys()
