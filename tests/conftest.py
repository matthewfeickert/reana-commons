# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.

"""Pytest configuration for REANA-Commons."""

from __future__ import absolute_import, print_function

from unittest.mock import ANY, patch

import pytest
from kombu import Connection, Exchange, Producer, Queue

from reana_commons.config import (MQ_DEFAULT_EXCHANGE, MQ_DEFAULT_QUEUE,
                                  MQ_DEFAULT_ROUTING_KEY,
                                  MQ_DEFAULT_SERIALIZER)
from reana_commons.consumer import REANABaseConsumer


class _REANABaseConsumerTestIMPL(REANABaseConsumer):
    """Test implementation of a REANAConsumer class."""

    def get_consumers(self, Consumer, channel):
        """Sample get consumers method."""
        return [Consumer(queues=self.queues, callbacks=[self.on_message],
                         accept=[self.default_serializer])]

    def on_message(self, body, message):
        """Sample on message method."""
        message.ack()


@pytest.fixture
def ConsumerBase():
    """REANABaseConsumer implementation fixture."""
    return _REANABaseConsumerTestIMPL


@pytest.fixture
def ConsumerBaseOnMessageMock(ConsumerBase):
    """REANABaseConsumer implementation fixture with ``on_message`` mocked."""
    with patch.object(ConsumerBase, 'on_message'):
        yield ConsumerBase


@pytest.fixture
def consume_queue():
    """Provides a callable to consume a queue."""
    def _consume_queue(consumer, limit=None):
        """."""
        consumer_generator = consumer.consume(limit=limit)
        while True:
            try:
                next(consumer_generator)
            except StopIteration:
                # no more items to consume in the queue
                break

    return _consume_queue


@pytest.fixture(scope='module')
def in_memory_queue_connection():
    """In memory message queue."""
    return Connection('memory:///')


@pytest.fixture
def default_exchange():
    """Default ``kombu.Exchange`` created from configuration."""
    exchange = Exchange(MQ_DEFAULT_EXCHANGE, type='direct')
    return exchange


@pytest.fixture
def default_queue(default_exchange):
    """Default ``kombu.Queue`` created from configuration."""
    queue = Queue(MQ_DEFAULT_QUEUE, exchange=default_exchange,
                  routing_key=MQ_DEFAULT_ROUTING_KEY)
    return queue


@pytest.fixture
def default_in_memory_producer(in_memory_queue_connection, default_exchange):
    """``kombu.Producer`` connected to in memory queue.."""
    return in_memory_queue_connection.Producer(
        exchange=default_exchange,
        routing_key=MQ_DEFAULT_ROUTING_KEY,
        serializer=MQ_DEFAULT_SERIALIZER)
