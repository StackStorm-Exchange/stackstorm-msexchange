# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and


from st2tests.base import BaseActionTestCase, BaseSensorTestCase


class ExchangeBaseActionTestCase(BaseActionTestCase):
    _test_config = {
        "username": "test",
        "password": "test",
        "primary_smtp_address": "test@test.com",
        "timezone": "Europe/London",
        "server": "10.0.0.1",
        "timeout": 1,
    }

    def setUp(self):
        super(ExchangeBaseActionTestCase, self).setUp()


class ExchangeBaseSensorTestCase(BaseSensorTestCase):
    _test_config = {
        "username": "test",
        "password": "test",
        "primary_smtp_address": "test@test.com",
        "timezone": "Europe/London",
        "sensor_folder": "Inbox",
        "server": "10.0.0.1",
        "timeout": 1,
    }

    def setUp(self):
        super(ExchangeBaseSensorTestCase, self).setUp()